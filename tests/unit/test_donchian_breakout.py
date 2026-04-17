"""Testes unitários do DonchianBreakoutStrategy (ADR-0011)."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.families.donchian import DonchianBreakoutStrategy


def _df_from_ohlc(
    *, opens: list[float], highs: list[float], lows: list[float], closes: list[float]
) -> pd.DataFrame:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    idx = pd.date_range(start=start, periods=len(closes), freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [1.0] * len(closes),
        },
        index=idx,
    )


def _df_flat(n: int, price: float = 100.0) -> pd.DataFrame:
    return _df_from_ohlc(
        opens=[price] * n,
        highs=[price] * n,
        lows=[price] * n,
        closes=[price] * n,
    )


class TestValidacaoParametros:
    def test_entry_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="entry_window deve ser > 0"):
            DonchianBreakoutStrategy(entry_window=0, exit_window=10)

    def test_entry_negativo_levanta(self) -> None:
        with pytest.raises(ValueError, match="entry_window deve ser > 0"):
            DonchianBreakoutStrategy(entry_window=-5, exit_window=10)

    def test_exit_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="exit_window deve ser > 0"):
            DonchianBreakoutStrategy(entry_window=20, exit_window=0)

    def test_exit_negativo_levanta(self) -> None:
        with pytest.raises(ValueError, match="exit_window deve ser > 0"):
            DonchianBreakoutStrategy(entry_window=20, exit_window=-1)

    def test_tipo_float_levanta(self) -> None:
        with pytest.raises(TypeError, match="entry_window deve ser int"):
            DonchianBreakoutStrategy(entry_window=20.0, exit_window=10)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="exit_window deve ser int"):
            DonchianBreakoutStrategy(entry_window=20, exit_window=10.0)  # type: ignore[arg-type]

    def test_bool_nao_aceito_como_inteiro(self) -> None:
        with pytest.raises(TypeError):
            DonchianBreakoutStrategy(entry_window=True, exit_window=10)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            DonchianBreakoutStrategy(entry_window=20, exit_window=False)  # type: ignore[arg-type]

    def test_entry_igual_exit_permitido(self) -> None:
        DonchianBreakoutStrategy(entry_window=14, exit_window=14)

    def test_entry_menor_que_exit_permitido(self) -> None:
        DonchianBreakoutStrategy(entry_window=10, exit_window=20)


class TestWarmUp:
    def test_warmup_hold_enquanto_menor_que_max_mais_dois(self) -> None:
        strat = DonchianBreakoutStrategy(entry_window=5, exit_window=3)
        df = _df_flat(8)
        for t in range(len(df)):
            window = df.iloc[: t + 1]
            sig = strat.decide(window)
            if len(window) < 7:
                assert sig == Signal.HOLD, f"t={t} len={len(window)} esperava HOLD"

    def test_warmup_usa_max_dos_dois_windows(self) -> None:
        strat = DonchianBreakoutStrategy(entry_window=3, exit_window=10)
        df = _df_flat(11)
        for t in range(len(df)):
            window = df.iloc[: t + 1]
            sig = strat.decide(window)
            if len(window) < 12:
                assert sig == Signal.HOLD


class TestEntradaBreakoutAlta:
    def test_breakout_alta_estrita_gera_enter_long(self) -> None:
        highs = [10.0] * 20
        highs[-2] = 15.0
        lows = [5.0] * 20
        closes = [8.0] * 20
        opens = [8.0] * 20
        df = _df_from_ohlc(opens=opens, highs=highs, lows=lows, closes=closes)
        strat = DonchianBreakoutStrategy(entry_window=5, exit_window=3)
        sig = strat.decide(df)
        assert sig == Signal.ENTER_LONG

    def test_empate_exato_nao_e_entrada(self) -> None:
        highs = [10.0] * 20
        lows = [5.0] * 20
        closes = [8.0] * 20
        opens = [8.0] * 20
        df = _df_from_ohlc(opens=opens, highs=highs, lows=lows, closes=closes)
        strat = DonchianBreakoutStrategy(entry_window=5, exit_window=3)
        sig = strat.decide(df)
        assert sig == Signal.HOLD


class TestSaidaBreakoutBaixa:
    def test_breakout_baixa_estrita_gera_exit(self) -> None:
        highs = [10.0] * 20
        lows = [5.0] * 20
        lows[-2] = 2.0
        closes = [8.0] * 20
        opens = [8.0] * 20
        df = _df_from_ohlc(opens=opens, highs=highs, lows=lows, closes=closes)
        strat = DonchianBreakoutStrategy(entry_window=5, exit_window=3)
        sig = strat.decide(df)
        assert sig == Signal.EXIT

    def test_empate_exato_na_baixa_nao_e_saida(self) -> None:
        highs = [10.0] * 20
        lows = [5.0] * 20
        closes = [8.0] * 20
        opens = [8.0] * 20
        df = _df_from_ohlc(opens=opens, highs=highs, lows=lows, closes=closes)
        strat = DonchianBreakoutStrategy(entry_window=5, exit_window=3)
        sig = strat.decide(df)
        assert sig == Signal.HOLD


class TestArbitragemReversao:
    def test_exit_vence_enter_long_em_reversao_simultanea(self) -> None:
        """Caso artificial: barra t-1 rompe tanto o high_max quanto o low_min.

        A ordem de avaliação da ADR-0011 é EXIT antes de ENTER_LONG.
        """
        highs = [10.0] * 20
        lows = [5.0] * 20
        closes = [8.0] * 20
        opens = [8.0] * 20
        highs[-2] = 50.0
        lows[-2] = 0.5
        df = _df_from_ohlc(opens=opens, highs=highs, lows=lows, closes=closes)
        strat = DonchianBreakoutStrategy(entry_window=5, exit_window=3)
        sig = strat.decide(df)
        assert sig == Signal.EXIT


class TestIgnoraBarraCorrente:
    def test_mutar_ohlc_em_t_nao_muda_sinal(self) -> None:
        highs = [10.0] * 20
        highs[-2] = 15.0
        lows = [5.0] * 20
        closes = [8.0] * 20
        opens = [8.0] * 20
        base = _df_from_ohlc(opens=opens, highs=highs, lows=lows, closes=closes)
        mutated = base.copy()
        mutated.iloc[-1, mutated.columns.get_loc("high")] = 999.0
        mutated.iloc[-1, mutated.columns.get_loc("low")] = 0.001
        mutated.iloc[-1, mutated.columns.get_loc("close")] = 999.0
        mutated.iloc[-1, mutated.columns.get_loc("open")] = 999.0

        strat = DonchianBreakoutStrategy(entry_window=5, exit_window=3)
        assert strat.decide(base) == strat.decide(mutated)


class TestLongOnly:
    def test_universo_de_saida_apenas_enter_long_exit_hold(self) -> None:
        import random

        rnd = random.Random(123)
        opens = []
        highs = []
        lows = []
        closes = []
        price = 100.0
        for _ in range(200):
            delta = rnd.uniform(-2.0, 2.0)
            price = max(10.0, price + delta)
            high = price + abs(rnd.uniform(0.1, 2.0))
            low = price - abs(rnd.uniform(0.1, 2.0))
            opens.append(price)
            highs.append(high)
            lows.append(low)
            closes.append(price)
        df = _df_from_ohlc(opens=opens, highs=highs, lows=lows, closes=closes)
        strat = DonchianBreakoutStrategy(entry_window=20, exit_window=10)
        allowed = {Signal.ENTER_LONG, Signal.EXIT, Signal.HOLD}
        for t in range(len(df)):
            sig = strat.decide(df.iloc[: t + 1])
            assert sig in allowed, f"sinal fora do universo long-only: {sig}"


class TestStateless:
    def test_duas_instancias_produzem_o_mesmo_sinal(self) -> None:
        highs = [10.0] * 30
        highs[-2] = 20.0
        lows = [5.0] * 30
        closes = [8.0] * 30
        opens = [8.0] * 30
        df = _df_from_ohlc(opens=opens, highs=highs, lows=lows, closes=closes)

        a = DonchianBreakoutStrategy(entry_window=5, exit_window=3)
        b = DonchianBreakoutStrategy(entry_window=5, exit_window=3)
        for t in range(10, len(df)):
            w = df.iloc[: t + 1]
            assert a.decide(w) == b.decide(w)

    def test_sinal_nao_depende_de_chamadas_anteriores(self) -> None:
        highs = [10.0] * 30
        highs[-2] = 20.0
        lows = [5.0] * 30
        closes = [8.0] * 30
        opens = [8.0] * 30
        df = _df_from_ohlc(opens=opens, highs=highs, lows=lows, closes=closes)
        strat = DonchianBreakoutStrategy(entry_window=5, exit_window=3)
        direct = strat.decide(df)
        for t in range(10, len(df) - 1):
            strat.decide(df.iloc[: t + 1])
        after = strat.decide(df)
        assert direct == after
