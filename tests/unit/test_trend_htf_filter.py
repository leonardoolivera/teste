"""Unit tests — TrendHTFRegimeFilter (ADR-0043)."""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from alpha_forge.regimes import TrendHTFRegimeFilter


def _window(closes: list[float], freq: str = "1h") -> pd.DataFrame:
    idx = pd.date_range(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc),
        periods=len(closes),
        freq=freq,
        tz="UTC",
    )
    c = np.array(closes, dtype=float)
    return pd.DataFrame(
        {"open": c, "high": c * 1.001, "low": c * 0.999, "close": c, "volume": 1.0},
        index=idx,
    )


class TestValidacaoParametros:
    def test_htf_invalido_levanta(self):
        with pytest.raises(ValueError, match="htf deve ser um de"):
            TrendHTFRegimeFilter(htf="2h", sma_window=50, mode="long_only")

    def test_htf_nao_string_levanta(self):
        with pytest.raises(TypeError, match="htf deve ser str"):
            TrendHTFRegimeFilter(htf=4, sma_window=50, mode="long_only")  # type: ignore[arg-type]

    def test_sma_window_zero_levanta(self):
        with pytest.raises(ValueError, match="sma_window deve ser > 0"):
            TrendHTFRegimeFilter(htf="4h", sma_window=0, mode="long_only")

    def test_sma_window_negativo_levanta(self):
        with pytest.raises(ValueError, match="sma_window deve ser > 0"):
            TrendHTFRegimeFilter(htf="4h", sma_window=-1, mode="long_only")

    def test_sma_window_bool_rejeitado(self):
        with pytest.raises(TypeError, match="sma_window deve ser int"):
            TrendHTFRegimeFilter(htf="4h", sma_window=True, mode="long_only")  # type: ignore[arg-type]

    def test_sma_window_float_rejeitado(self):
        with pytest.raises(TypeError, match="sma_window deve ser int"):
            TrendHTFRegimeFilter(htf="4h", sma_window=50.0, mode="long_only")  # type: ignore[arg-type]

    def test_mode_invalido_levanta(self):
        with pytest.raises(ValueError, match="mode deve ser um de"):
            TrendHTFRegimeFilter(htf="4h", sma_window=50, mode="any_side")


class TestWarmUp:
    def test_window_vazia_retorna_false(self):
        filt = TrendHTFRegimeFilter(htf="4h", sma_window=10, mode="long_only")
        idx = pd.DatetimeIndex([], tz="UTC")
        empty = pd.DataFrame(
            {"open": [], "high": [], "low": [], "close": [], "volume": []}, index=idx
        )
        assert filt.is_active(empty) is False

    def test_poucos_candles_htf_retorna_false(self):
        # 4h sma_window=10 exige 10 candles 4h fechados + 1 descartado = 44 barras 1h + algumas,
        # mas só daremos 20 barras 1h = ~5 candles 4h -> False.
        filt = TrendHTFRegimeFilter(htf="4h", sma_window=10, mode="long_only")
        w = _window(list(range(100, 120)))
        assert bool(filt.is_active(w)) is False


class TestLongOnly:
    def test_uptrend_preco_acima_sma_retorna_true(self):
        # Gera tendência up clara: 300 barras 1h -> ~75 candles 4h.
        filt = TrendHTFRegimeFilter(htf="4h", sma_window=20, mode="long_only")
        closes = [100.0 * (1.001 ** i) for i in range(300)]
        w = _window(closes)
        assert bool(filt.is_active(w)) is True

    def test_downtrend_preco_abaixo_sma_retorna_false(self):
        filt = TrendHTFRegimeFilter(htf="4h", sma_window=20, mode="long_only")
        closes = [100.0 * (0.999 ** i) for i in range(300)]
        w = _window(closes)
        assert bool(filt.is_active(w)) is False


class TestShortOnly:
    def test_downtrend_retorna_true(self):
        filt = TrendHTFRegimeFilter(htf="4h", sma_window=20, mode="short_only")
        closes = [100.0 * (0.999 ** i) for i in range(300)]
        w = _window(closes)
        assert bool(filt.is_active(w)) is True

    def test_uptrend_retorna_false(self):
        filt = TrendHTFRegimeFilter(htf="4h", sma_window=20, mode="short_only")
        closes = [100.0 * (1.001 ** i) for i in range(300)]
        w = _window(closes)
        assert bool(filt.is_active(w)) is False


class TestBothSides:
    def test_tendencia_qualquer_lado_retorna_true(self):
        filt = TrendHTFRegimeFilter(htf="4h", sma_window=20, mode="both_sides")
        closes = [100.0 * (1.001 ** i) for i in range(300)]
        w = _window(closes)
        assert bool(filt.is_active(w)) is True


class TestIgnoraBarraT:
    def test_mutar_ultima_barra_nao_muda_resultado(self):
        filt = TrendHTFRegimeFilter(htf="4h", sma_window=20, mode="long_only")
        closes = [100.0 * (1.001 ** i) for i in range(300)]
        w = _window(closes)
        baseline = filt.is_active(w)

        perturbed = w.copy()
        last = len(perturbed) - 1
        for col in ("open", "high", "low", "close", "volume"):
            perturbed.iloc[last, perturbed.columns.get_loc(col)] = 1e9

        assert filt.is_active(perturbed) == baseline


class TestDatetimeIndexObrigatorio:
    def test_index_nao_datetime_sem_coercao_retorna_false(self):
        filt = TrendHTFRegimeFilter(htf="4h", sma_window=10, mode="long_only")
        closes = list(range(100, 200))
        c = np.array(closes, dtype=float)
        # Index string não-parseável.
        df = pd.DataFrame(
            {"open": c, "high": c, "low": c, "close": c, "volume": 1.0},
            index=[f"bad_{i}" for i in range(len(c))],
        )
        # Não pode levantar — causal retorna False por não conseguir resample.
        assert filt.is_active(df) is False


class TestHTFTimeframes:
    def test_1d_timeframe_aceito(self):
        filt = TrendHTFRegimeFilter(htf="1d", sma_window=5, mode="long_only")
        # 1000 barras 1h ≈ 42 candles diários -> suficiente.
        closes = [100.0 * (1.0005 ** i) for i in range(1000)]
        w = _window(closes)
        assert bool(filt.is_active(w)) is True

    def test_1w_timeframe_aceito(self):
        filt = TrendHTFRegimeFilter(htf="1W", sma_window=4, mode="long_only")
        # 2000 barras 1h ≈ 12 semanas — suficiente pra sma_window=4 + 1 descartado.
        closes = [100.0 * (1.0002 ** i) for i in range(2000)]
        w = _window(closes)
        assert bool(filt.is_active(w)) is True
