"""Testes unitários da DonchianBreakoutStrategy (ADR-0011).

Cobrem: validação de parâmetros (erros explícitos e cedo), warm-up como HOLD,
breakout de alta, breakout de baixa, arbitragem de reversão simultânea
(prioridade EXIT), causalidade estrutural (ignora a barra t por construção),
long-only e stateless.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.families.donchian import DonchianBreakoutStrategy


def _df_from_ohlc(
    opens: list[float],
    highs: list[float],
    lows: list[float],
    closes: list[float],
) -> pd.DataFrame:
    n = len(opens)
    assert len(highs) == n and len(lows) == n and len(closes) == n
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    idx = pd.date_range(start=start, periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [1.0] * n,
        },
        index=idx,
    )


def _flat_df(n: int, value: float = 100.0) -> pd.DataFrame:
    return _df_from_ohlc([value] * n, [value] * n, [value] * n, [value] * n)


class TestValidacaoParametros:
    def test_entry_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="entry_window deve ser > 0"):
            DonchianBreakoutStrategy(entry_window=0, exit_window=10)

    def test_entry_negativo_levanta(self) -> None:
        with pytest.raises(ValueError, match="entry_window deve ser > 0"):
            DonchianBreakoutStrategy(entry_window=-2, exit_window=10)

    def test_exit_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="exit_window deve ser > 0"):
            DonchianBreakoutStrategy(entry_window=20, exit_window=0)

    def test_exit_negativo_levanta(self) -> None:
        with pytest.raises(ValueError, match="exit_window deve ser > 0"):
            DonchianBreakoutStrategy(entry_window=20, exit_window=-5)

    def test_tipo_nao_inteiro_levanta(self) -> None:
        with pytest.raises(TypeError, match="entry_window deve ser int"):
            DonchianBreakoutStrategy(entry_window=20.0, exit_window=10)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="exit_window deve ser int"):
            DonchianBreakoutStrategy(entry_window=20, exit_window=10.0)  # type: ignore[arg-type]

    def test_float_inteiro_tambem_rejeitado(self) -> None:
        # 20.0 "é inteiro" matematicamente, mas é float — ADR-0011 rejeita.
        with pytest.raises(TypeError):
            DonchianBreakoutStrategy(entry_window=20.0, exit_window=10)  # type: ignore[arg-type]

    def test_bool_rejeitado_como_int(self) -> None:
        # bool é subclasse de int em Python; ADR-0011 exige int "verdadeiro".
        with pytest.raises(TypeError):
            DonchianBreakoutStrategy(entry_window=True, exit_window=10)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            DonchianBreakoutStrategy(entry_window=20, exit_window=False)  # type: ignore[arg-type]

    def test_entry_menor_que_exit_eh_valido(self) -> None:
        # ADR-0011 §"Contrato de parâmetros": sem restrição de ordenação.
        s = DonchianBreakoutStrategy(entry_window=10, exit_window=20)
        assert s.entry_window == 10
        assert s.exit_window == 20

    def test_entry_igual_exit_eh_valido(self) -> None:
        s = DonchianBreakoutStrategy(entry_window=14, exit_window=14)
        assert s.entry_window == 14
        assert s.exit_window == 14


class TestWarmUp:
    def test_hold_ate_min_bars(self) -> None:
        # entry=3, exit=2 → min_bars = max(3,2) + 2 = 5.
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        df = _flat_df(10, value=100.0)
        for t in range(len(df)):
            window = df.iloc[: t + 1]
            sig = strat.decide(window)
            if len(window) < 5:
                assert sig == Signal.HOLD, (
                    f"t={t} len={len(window)} esperava HOLD no warm-up, veio {sig}"
                )

    def test_fronteira_warmup_hold_mesmo_com_dados(self) -> None:
        # Com entry=2, exit=2 → min_bars = 4. Em len=3, HOLD obrigatório.
        strat = DonchianBreakoutStrategy(entry_window=2, exit_window=2)
        df = _df_from_ohlc(
            opens=[1.0, 2.0, 3.0],
            highs=[1.0, 2.0, 3.0],
            lows=[1.0, 2.0, 3.0],
            closes=[1.0, 2.0, 3.0],
        )
        assert strat.decide(df) == Signal.HOLD


class TestEntradaBreakoutAlta:
    def test_breakout_de_alta_estrito_emite_enter_long(self) -> None:
        # entry=3, exit=2. Janela de 6 barras: índices 0..5 (barra t = 5).
        # highs[:-1] = indices 0..4 → ref_high = highs[4]; prior = highs[1..3].
        # highs[4] = 15 > max(10,10,10) = 10 → ENTER_LONG.
        # lows[4] = 9 NÃO é < min(lows[2..3]) = 9 (estrito) → sem EXIT.
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        df = _df_from_ohlc(
            opens=[10.0, 10.0, 10.0, 10.0, 15.0, 16.0],
            highs=[10.0, 10.0, 10.0, 10.0, 15.0, 16.0],
            lows=[9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
            closes=[10.0, 10.0, 10.0, 10.0, 14.0, 15.0],
        )
        assert strat.decide(df) == Signal.ENTER_LONG

    def test_empate_exato_no_high_nao_emite_sinal(self) -> None:
        # highs[4] == max(highs[1..3]) → sem breakout estrito (> não >=).
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        df = _df_from_ohlc(
            opens=[10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            highs=[10.0, 10.0, 10.0, 10.0, 10.0, 11.0],
            lows=[9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
            closes=[10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
        )
        assert strat.decide(df) == Signal.HOLD

    def test_sem_breakout_emite_hold(self) -> None:
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        df = _flat_df(6, value=100.0)
        assert strat.decide(df) == Signal.HOLD


class TestSaidaBreakoutBaixa:
    def test_breakout_de_baixa_estrito_emite_exit(self) -> None:
        # lows[4] = 5 < min(lows[2..3]) = 9 → EXIT.
        # highs[4] = 10 NÃO é > max(highs[1..3]) = 10 → sem ENTER_LONG.
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        df = _df_from_ohlc(
            opens=[10.0, 10.0, 10.0, 10.0, 6.0, 5.0],
            highs=[10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            lows=[9.0, 9.0, 9.0, 9.0, 5.0, 4.0],
            closes=[10.0, 10.0, 10.0, 10.0, 6.0, 5.0],
        )
        assert strat.decide(df) == Signal.EXIT

    def test_empate_exato_no_low_nao_emite_sinal(self) -> None:
        # lows[4] == min(lows[2..3]) → sem breakout estrito de baixa.
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        df = _df_from_ohlc(
            opens=[10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            highs=[10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            lows=[9.0, 9.0, 9.0, 9.0, 9.0, 8.0],
            closes=[10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
        )
        assert strat.decide(df) == Signal.HOLD


class TestArbitragemReversao:
    def test_breakout_alta_e_baixa_simultaneos_dao_exit(self) -> None:
        # Caso artificial: uma barra simultaneamente rompe o máximo anterior
        # E rompe o mínimo anterior. Fisicamente raro, estruturalmente possível
        # (barra de amplitude muito grande contra janela contraída). ADR-0011
        # §"Separação estratégia × engine": ordem EXIT → ENTER_LONG resolve.
        # Estratégia emite EXIT (mais conservador); engine, com posição aberta,
        # fecha; sem posição, trata como no-op e a barra não entra.
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        df = _df_from_ohlc(
            opens=[10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            highs=[10.0, 10.0, 10.0, 10.0, 20.0, 20.0],
            lows=[9.0, 9.0, 9.0, 9.0, 1.0, 1.0],
            closes=[10.0, 10.0, 10.0, 10.0, 15.0, 15.0],
        )
        assert strat.decide(df) == Signal.EXIT


class TestIgnoraBarraCorrente:
    def test_mutacao_da_barra_t_nao_altera_sinal(self) -> None:
        # ADR-0011 §"Regra exata": a estratégia ignora window.iloc[-1] por
        # construção. Mutar high, low E close de t não pode mudar o sinal.
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        base = _df_from_ohlc(
            opens=[10.0, 10.0, 10.0, 10.0, 15.0, 16.0],
            highs=[10.0, 10.0, 10.0, 10.0, 15.0, 16.0],
            lows=[9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
            closes=[10.0, 10.0, 10.0, 10.0, 14.0, 15.0],
        )
        sig_base = strat.decide(base)
        assert sig_base == Signal.ENTER_LONG

        mutated = base.copy()
        last_idx = mutated.index[-1]
        mutated.at[last_idx, "high"] = 99999.0
        mutated.at[last_idx, "low"] = 0.0001
        mutated.at[last_idx, "close"] = 50000.0

        sig_mutated = strat.decide(mutated)
        assert sig_mutated == sig_base, (
            f"sinal mudou ao mutar barra t: {sig_base} → {sig_mutated}"
        )

    def test_mutacao_da_barra_t_nao_transforma_hold_em_sinal(self) -> None:
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        base = _flat_df(6, value=100.0)
        assert strat.decide(base) == Signal.HOLD

        mutated = base.copy()
        last_idx = mutated.index[-1]
        mutated.at[last_idx, "high"] = 1_000_000.0
        mutated.at[last_idx, "low"] = 0.0001
        mutated.at[last_idx, "close"] = 500_000.0

        assert strat.decide(mutated) == Signal.HOLD


class TestLongOnly:
    def test_nunca_emite_enter_short_em_queda_continua(self) -> None:
        # Forte regime de baixa. Sinais emitidos só podem estar em
        # {ENTER_LONG, EXIT, HOLD}. ADR-0011 §"Separação": ENTER_SHORT está
        # fora do universo de saída desta estratégia nesta fase.
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        closes = [100.0, 95.0, 90.0, 85.0, 80.0, 75.0, 70.0, 65.0, 60.0, 55.0]
        df = _df_from_ohlc(
            opens=closes,
            highs=[c + 1 for c in closes],
            lows=[c - 1 for c in closes],
            closes=closes,
        )
        allowed = {Signal.ENTER_LONG, Signal.EXIT, Signal.HOLD}
        for t in range(len(df)):
            sig = strat.decide(df.iloc[: t + 1])
            assert sig in allowed, f"t={t} emitiu sinal fora do contrato long-only: {sig}"
            assert sig != Signal.ENTER_SHORT

    def test_nunca_emite_enter_short_em_alta_continua(self) -> None:
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        closes = [55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 95.0, 100.0]
        df = _df_from_ohlc(
            opens=closes,
            highs=[c + 1 for c in closes],
            lows=[c - 1 for c in closes],
            closes=closes,
        )
        allowed = {Signal.ENTER_LONG, Signal.EXIT, Signal.HOLD}
        for t in range(len(df)):
            sig = strat.decide(df.iloc[: t + 1])
            assert sig in allowed
            assert sig != Signal.ENTER_SHORT


class TestStateless:
    def test_duas_chamadas_mesma_janela_mesmo_sinal(self) -> None:
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        df = _df_from_ohlc(
            opens=[10.0, 10.0, 10.0, 10.0, 15.0, 16.0],
            highs=[10.0, 10.0, 10.0, 10.0, 15.0, 16.0],
            lows=[9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
            closes=[10.0, 10.0, 10.0, 10.0, 14.0, 15.0],
        )
        s1 = strat.decide(df)
        s2 = strat.decide(df)
        assert s1 == s2 == Signal.ENTER_LONG

    def test_duas_instancias_mesmos_parametros_mesmo_sinal(self) -> None:
        a = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        b = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        df = _df_from_ohlc(
            opens=[10.0, 10.0, 10.0, 10.0, 15.0, 16.0],
            highs=[10.0, 10.0, 10.0, 10.0, 15.0, 16.0],
            lows=[9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
            closes=[10.0, 10.0, 10.0, 10.0, 14.0, 15.0],
        )
        assert a.decide(df) == b.decide(df)

    def test_nao_expõe_estado_interno_entre_barras(self) -> None:
        # Chamadas em ordem arbitrária devolvem o mesmo resultado que
        # chamadas em ordem temporal — é função pura de window.
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=2)
        df = _df_from_ohlc(
            opens=[10.0, 10.0, 10.0, 10.0, 15.0, 16.0],
            highs=[10.0, 10.0, 10.0, 10.0, 15.0, 16.0],
            lows=[9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
            closes=[10.0, 10.0, 10.0, 10.0, 14.0, 15.0],
        )
        forward = [strat.decide(df.iloc[: t + 1]) for t in range(len(df))]
        backward = [strat.decide(df.iloc[: t + 1]) for t in reversed(range(len(df)))]
        backward.reverse()
        assert forward == backward
