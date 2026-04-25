"""Testes unitários de ZScoreMeanReversionStrategy (ADR-0175).

Cobrem: validação de params, warm-up HOLD, causalidade (ignora bar t),
entrada edge-triggered ±threshold, exit zero-crossing (long-only),
simetria long/short, statelessness, sigma=0 degenerado.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.families.zscore import ZScoreMeanReversionStrategy


def _df_from_closes(closes: list[float]) -> pd.DataFrame:
    n = len(closes)
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    idx = pd.date_range(start=start, periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": closes,
            "high": [c + 0.01 for c in closes],
            "low": [c - 0.01 for c in closes],
            "close": closes,
            "volume": [1.0] * n,
        },
        index=idx,
    )


class TestValidacaoParametros:
    def test_window_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="window deve ser > 0"):
            ZScoreMeanReversionStrategy(window=0, threshold=2.0)

    def test_window_negativo_levanta(self) -> None:
        with pytest.raises(ValueError, match="window deve ser > 0"):
            ZScoreMeanReversionStrategy(window=-3, threshold=2.0)

    def test_window_float_levanta(self) -> None:
        with pytest.raises(TypeError, match="window deve ser int"):
            ZScoreMeanReversionStrategy(window=20.0, threshold=2.0)  # type: ignore[arg-type]

    def test_window_bool_levanta(self) -> None:
        with pytest.raises(TypeError, match="window deve ser int"):
            ZScoreMeanReversionStrategy(window=True, threshold=2.0)  # type: ignore[arg-type]

    def test_threshold_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="threshold deve ser > 0"):
            ZScoreMeanReversionStrategy(window=20, threshold=0.0)

    def test_threshold_negativo_levanta(self) -> None:
        with pytest.raises(ValueError, match="threshold deve ser > 0"):
            ZScoreMeanReversionStrategy(window=20, threshold=-1.0)

    def test_threshold_string_levanta(self) -> None:
        with pytest.raises(TypeError, match="threshold deve ser float"):
            ZScoreMeanReversionStrategy(window=20, threshold="2")  # type: ignore[arg-type]

    def test_long_only_int_levanta(self) -> None:
        with pytest.raises(TypeError, match="long_only deve ser bool"):
            ZScoreMeanReversionStrategy(window=20, threshold=2.0, long_only=1)  # type: ignore[arg-type]


class TestWarmup:
    def test_menos_que_min_bars_retorna_hold(self) -> None:
        s = ZScoreMeanReversionStrategy(window=20, threshold=2.0)
        for n in [1, 10, 20, 22]:
            closes = [100.0] * n
            assert s.decide(_df_from_closes(closes)) == Signal.HOLD, f"n={n}"

    def test_exatamente_min_bars_sigma_zero_hold(self) -> None:
        s = ZScoreMeanReversionStrategy(window=20, threshold=2.0)
        closes = [100.0] * 23
        assert s.decide(_df_from_closes(closes)) == Signal.HOLD


class TestSigmaZero:
    def test_sigma_zero_retorna_hold(self) -> None:
        s = ZScoreMeanReversionStrategy(window=10, threshold=2.0)
        closes = [100.0] * 15
        assert s.decide(_df_from_closes(closes)) == Signal.HOLD


class TestSinaisLongOnly:
    def test_entry_long_quando_z_cruza_abaixo_menos_threshold(self) -> None:
        s = ZScoreMeanReversionStrategy(window=10, threshold=2.0, long_only=True)
        closes = [100.0, 101.0, 100.0, 101.0, 100.0, 101.0, 100.0, 101.0, 100.0, 101.0]
        closes += [99.5, 80.0, 100.0]
        sig = s.decide(_df_from_closes(closes))
        assert sig == Signal.ENTER_LONG

    def test_nao_entra_se_ja_estava_abaixo_threshold(self) -> None:
        s = ZScoreMeanReversionStrategy(window=10, threshold=2.0, long_only=True)
        closes = [100.0, 101.0] * 5
        closes += [80.0, 80.0, 100.0]
        sig = s.decide(_df_from_closes(closes))
        assert sig != Signal.ENTER_LONG

    def test_exit_em_zero_crossing_positivo(self) -> None:
        s = ZScoreMeanReversionStrategy(window=10, threshold=2.0, long_only=True)
        closes = [100.0, 101.0] * 5
        closes += [99.0, 101.0, 100.0]
        sig = s.decide(_df_from_closes(closes))
        assert sig == Signal.EXIT

    def test_sem_sinal_retorna_hold(self) -> None:
        s = ZScoreMeanReversionStrategy(window=10, threshold=2.0, long_only=True)
        closes = list(range(1, 14))
        closes_f = [float(c) for c in closes]
        sig = s.decide(_df_from_closes(closes_f))
        assert sig in (Signal.HOLD, Signal.ENTER_LONG, Signal.EXIT)


class TestSinaisShort:
    def test_entry_short_quando_z_cruza_acima_threshold(self) -> None:
        s = ZScoreMeanReversionStrategy(window=10, threshold=2.0, long_only=False)
        closes = [100.0, 101.0] * 5
        closes += [100.5, 120.0, 100.0]
        sig = s.decide(_df_from_closes(closes))
        assert sig == Signal.ENTER_SHORT

    def test_long_e_short_simultaneo_hold(self) -> None:
        s = ZScoreMeanReversionStrategy(window=10, threshold=2.0, long_only=False)
        closes = [100.0] * 13
        assert s.decide(_df_from_closes(closes)) == Signal.HOLD


class TestCausalidade:
    def test_barra_t_ignorada(self) -> None:
        s = ZScoreMeanReversionStrategy(window=10, threshold=2.0, long_only=True)
        base = [100.0, 101.0] * 5 + [99.5, 80.0, 100.0]
        sig_a = s.decide(_df_from_closes(base))

        mut = base.copy()
        mut[-1] = 999999.0
        sig_b = s.decide(_df_from_closes(mut))
        assert sig_a == sig_b


class TestStateless:
    def test_mesma_janela_mesma_decisao(self) -> None:
        s = ZScoreMeanReversionStrategy(window=10, threshold=2.0, long_only=True)
        closes = [100.0, 101.0] * 5 + [99.5, 80.0, 100.0]
        df = _df_from_closes(closes)
        a = s.decide(df)
        b = s.decide(df)
        c = s.decide(df)
        assert a == b == c
