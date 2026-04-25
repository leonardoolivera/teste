"""Testes unitários da KeltnerMeanReversionStrategy (ADR-0170).

Cobrem: validação de parâmetros, warm-up HOLD, causalidade (ignora bar t),
entrada/saida edge-triggered, simetria long/short, stateless.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.families.keltner import KeltnerMeanReversionStrategy


def _df_from_closes(closes: list[float], hl_spread: float = 0.001) -> pd.DataFrame:
    n = len(closes)
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    idx = pd.date_range(start=start, periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": closes,
            "high": [c + hl_spread for c in closes],
            "low": [c - hl_spread for c in closes],
            "close": closes,
            "volume": [1.0] * n,
        },
        index=idx,
    )


class TestValidacaoParametros:
    def test_window_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="window deve ser > 0"):
            KeltnerMeanReversionStrategy(window=0, atr_period=14, atr_mult=2.0)

    def test_window_negativo_levanta(self) -> None:
        with pytest.raises(ValueError, match="window deve ser > 0"):
            KeltnerMeanReversionStrategy(window=-5, atr_period=14, atr_mult=2.0)

    def test_atr_period_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="atr_period deve ser > 0"):
            KeltnerMeanReversionStrategy(window=20, atr_period=0, atr_mult=2.0)

    def test_atr_mult_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="atr_mult deve ser > 0"):
            KeltnerMeanReversionStrategy(window=20, atr_period=14, atr_mult=0.0)

    def test_atr_mult_negativo_levanta(self) -> None:
        with pytest.raises(ValueError, match="atr_mult deve ser > 0"):
            KeltnerMeanReversionStrategy(window=20, atr_period=14, atr_mult=-1.5)

    def test_window_tipo_nao_int_levanta(self) -> None:
        with pytest.raises(TypeError, match="window deve ser int"):
            KeltnerMeanReversionStrategy(window=20.0, atr_period=14, atr_mult=2.0)  # type: ignore[arg-type]

    def test_window_bool_rejeitado(self) -> None:
        with pytest.raises(TypeError, match="window deve ser int"):
            KeltnerMeanReversionStrategy(window=True, atr_period=14, atr_mult=2.0)  # type: ignore[arg-type]

    def test_atr_period_bool_rejeitado(self) -> None:
        with pytest.raises(TypeError, match="atr_period deve ser int"):
            KeltnerMeanReversionStrategy(window=20, atr_period=True, atr_mult=2.0)  # type: ignore[arg-type]

    def test_atr_mult_tipo_nao_numerico_levanta(self) -> None:
        with pytest.raises(TypeError, match="atr_mult deve ser float"):
            KeltnerMeanReversionStrategy(window=20, atr_period=14, atr_mult="2.0")  # type: ignore[arg-type]

    def test_atr_mult_bool_rejeitado(self) -> None:
        with pytest.raises(TypeError, match="atr_mult deve ser float"):
            KeltnerMeanReversionStrategy(window=20, atr_period=14, atr_mult=True)  # type: ignore[arg-type]

    def test_atr_mult_int_coergido_para_float(self) -> None:
        s = KeltnerMeanReversionStrategy(window=20, atr_period=14, atr_mult=2)
        assert isinstance(s.atr_mult, float)
        assert s.atr_mult == 2.0

    def test_long_only_false_aceito(self) -> None:
        s = KeltnerMeanReversionStrategy(
            window=20, atr_period=14, atr_mult=2.0, long_only=False
        )
        assert s.long_only is False

    def test_long_only_tipo_nao_bool_levanta(self) -> None:
        with pytest.raises(TypeError, match="long_only deve ser bool"):
            KeltnerMeanReversionStrategy(
                window=20, atr_period=14, atr_mult=2.0, long_only=1  # type: ignore[arg-type]
            )


class TestWarmUp:
    def test_janela_curta_retorna_hold(self) -> None:
        s = KeltnerMeanReversionStrategy(window=20, atr_period=14, atr_mult=2.0)
        df = _df_from_closes([100.0] * 10)
        assert s.decide(df) == Signal.HOLD

    def test_min_bars_exato_hold(self) -> None:
        s = KeltnerMeanReversionStrategy(window=5, atr_period=5, atr_mult=2.0)
        # min_bars = max(5,5)+3 = 8; 7 barras ainda é warm-up
        df = _df_from_closes([100.0 + i * 0.1 for i in range(7)])
        assert s.decide(df) == Signal.HOLD


class TestSinais:
    def test_entrada_long_em_ruptura_banda_inferior(self) -> None:
        """closes estáveis, spike down em t-1 abaixo da banda."""
        s = KeltnerMeanReversionStrategy(
            window=5, atr_period=5, atr_mult=2.0, long_only=False
        )
        # 10 closes estáveis, depois drop forte em t-1 abaixo da banda
        closes = [100.0] * 10 + [90.0, 100.0]  # t-2=100 acima banda_prev; t-1=90 abaixo banda_now; t ignorado
        df = _df_from_closes(closes, hl_spread=0.01)
        sig = s.decide(df)
        assert sig == Signal.ENTER_LONG

    def test_entrada_short_em_ruptura_banda_superior(self) -> None:
        s = KeltnerMeanReversionStrategy(
            window=5, atr_period=5, atr_mult=2.0, long_only=False
        )
        closes = [100.0] * 10 + [110.0, 100.0]
        df = _df_from_closes(closes, hl_spread=0.01)
        sig = s.decide(df)
        assert sig == Signal.ENTER_SHORT

    def test_short_entry_ignorado_em_long_only(self) -> None:
        s = KeltnerMeanReversionStrategy(
            window=5, atr_period=5, atr_mult=2.0, long_only=True
        )
        closes = [100.0] * 10 + [110.0, 100.0]
        df = _df_from_closes(closes, hl_spread=0.01)
        sig = s.decide(df)
        # long-only nunca retorna ENTER_SHORT; como não há long signal aqui, é HOLD
        assert sig == Signal.HOLD

    def test_sem_cruzamento_hold(self) -> None:
        s = KeltnerMeanReversionStrategy(
            window=5, atr_period=5, atr_mult=2.0, long_only=False
        )
        # Todos os closes estáveis dentro do envelope → HOLD
        closes = [100.0] * 15
        df = _df_from_closes(closes, hl_spread=0.01)
        assert s.decide(df) == Signal.HOLD


class TestCausalidade:
    def test_barra_t_ignorada(self) -> None:
        """A decisão não deve mudar se trocarmos o último close."""
        s = KeltnerMeanReversionStrategy(
            window=5, atr_period=5, atr_mult=2.0, long_only=False
        )
        base = [100.0] * 10 + [90.0]
        df_a = _df_from_closes(base + [100.0], hl_spread=0.01)
        df_b = _df_from_closes(base + [9999.0], hl_spread=0.01)
        assert s.decide(df_a) == s.decide(df_b)


class TestStateless:
    def test_mesma_entrada_mesma_saida(self) -> None:
        s = KeltnerMeanReversionStrategy(
            window=5, atr_period=5, atr_mult=2.0, long_only=False
        )
        closes = [100.0] * 10 + [90.0, 100.0]
        df = _df_from_closes(closes, hl_spread=0.01)
        sigs = [s.decide(df) for _ in range(3)]
        assert sigs[0] == sigs[1] == sigs[2]
