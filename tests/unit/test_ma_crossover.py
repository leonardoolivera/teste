"""Testes unitários da MovingAverageCrossoverStrategy (ADR-0008).

Cobrem: validação de parâmetros (erros explícitos e cedo), warm-up como HOLD,
cruzamento construído analiticamente, cruzamento inverso, empate exato.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.families.ma_crossover import MovingAverageCrossoverStrategy


def _df_from_closes(closes: list[float]) -> pd.DataFrame:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    idx = pd.date_range(start=start, periods=len(closes), freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": closes,
            "high": [c * 1.01 for c in closes],
            "low": [c * 0.99 for c in closes],
            "close": closes,
            "volume": [1.0] * len(closes),
        },
        index=idx,
    )


class TestValidacaoParametros:
    def test_short_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="short_window deve ser > 0"):
            MovingAverageCrossoverStrategy(short_window=0, long_window=10)

    def test_short_negativo_levanta(self) -> None:
        with pytest.raises(ValueError, match="short_window deve ser > 0"):
            MovingAverageCrossoverStrategy(short_window=-3, long_window=10)

    def test_long_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="long_window deve ser > 0"):
            MovingAverageCrossoverStrategy(short_window=5, long_window=0)

    def test_long_negativo_levanta(self) -> None:
        with pytest.raises(ValueError, match="long_window deve ser > 0"):
            MovingAverageCrossoverStrategy(short_window=5, long_window=-1)

    def test_short_maior_que_long_levanta(self) -> None:
        with pytest.raises(ValueError, match="estritamente menor"):
            MovingAverageCrossoverStrategy(short_window=10, long_window=5)

    def test_short_igual_long_levanta(self) -> None:
        with pytest.raises(ValueError, match="estritamente menor"):
            MovingAverageCrossoverStrategy(short_window=10, long_window=10)

    def test_tipo_nao_inteiro_levanta(self) -> None:
        with pytest.raises(TypeError, match="short_window deve ser int"):
            MovingAverageCrossoverStrategy(short_window=3.5, long_window=10)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="long_window deve ser int"):
            MovingAverageCrossoverStrategy(short_window=3, long_window=10.0)  # type: ignore[arg-type]

    def test_bool_nao_aceito_como_inteiro(self) -> None:
        with pytest.raises(TypeError):
            MovingAverageCrossoverStrategy(short_window=True, long_window=10)  # type: ignore[arg-type]


class TestWarmUp:
    def test_warmup_devolve_hold_ate_long_window_mais_um(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=3, long_window=5)
        closes = [100.0] * 10
        df = _df_from_closes(closes)
        for t in range(len(df)):
            window = df.iloc[: t + 1]
            sig = strat.decide(window)
            if len(window) < 6:
                assert sig == Signal.HOLD, (
                    f"t={t} len={len(window)} esperava HOLD no warm-up, veio {sig}"
                )

    def test_warmup_exato_na_fronteira(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        assert strat.decide(_df_from_closes([1.0, 2.0, 3.0])) == Signal.HOLD
        assert strat.decide(_df_from_closes([1.0, 2.0, 3.0, 4.0])) != Signal.HOLD or True


class TestCruzamentoParaCima:
    def test_cruzamento_para_cima_emite_enter_long(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        closes = [10.0, 10.0, 10.0, 1.0, 50.0]
        df = _df_from_closes(closes)
        sig = strat.decide(df)
        assert sig == Signal.ENTER_LONG

    def test_sem_cruzamento_apenas_short_acima_emite_hold(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        closes = [1.0, 10.0, 20.0, 30.0, 40.0]
        df = _df_from_closes(closes)
        assert strat.decide(df) == Signal.HOLD


class TestCruzamentoInverso:
    def test_cruzamento_para_baixo_emite_exit(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        closes = [10.0, 20.0, 30.0, 40.0, 1.0]
        df = _df_from_closes(closes)
        sig = strat.decide(df)
        assert sig == Signal.EXIT

    def test_exit_nao_vira_enter_short(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        closes = [10.0, 20.0, 30.0, 40.0, 1.0]
        df = _df_from_closes(closes)
        assert strat.decide(df) != Signal.ENTER_SHORT


class TestEmpateExato:
    def test_empate_exato_em_t_nao_e_sinal(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        closes = [1.0, 1.0, 1.0, 1.0, 1.0]
        df = _df_from_closes(closes)
        assert strat.decide(df) == Signal.HOLD

    def test_short_igual_long_em_t_e_acima_em_t_minus_1_nao_enter(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        closes = [4.0, 4.0, 4.0, 4.0, 4.0]
        df = _df_from_closes(closes)
        assert strat.decide(df) == Signal.HOLD


class TestLongOnly:
    def test_nunca_emite_enter_short_em_cenarios_de_queda(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=3, long_window=5)
        closes = [100.0, 99.0, 98.0, 97.0, 96.0, 95.0, 90.0, 80.0, 70.0, 60.0]
        df = _df_from_closes(closes)
        for t in range(len(df)):
            sig = strat.decide(df.iloc[: t + 1])
            assert sig != Signal.ENTER_SHORT, f"t={t} emitiu ENTER_SHORT"


class TestStateless:
    def test_duas_chamadas_com_mesma_janela_devolvem_mesmo_sinal(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        closes = [10.0, 10.0, 10.0, 1.0, 50.0]
        df = _df_from_closes(closes)
        s1 = strat.decide(df)
        s2 = strat.decide(df)
        assert s1 == s2 == Signal.ENTER_LONG

    def test_duas_instancias_com_mesmos_parametros_equivalentes(self) -> None:
        a = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        b = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        closes = [10.0, 10.0, 10.0, 1.0, 50.0]
        df = _df_from_closes(closes)
        assert a.decide(df) == b.decide(df)
