"""Testes unitários da RSIMeanReversionStrategy (ADR-0027).

Cobrem: validação de parâmetros cedo, warm-up como HOLD, entrada por cruzamento
do oversold (edge-triggered), saída por cruzamento de 50 (edge-triggered),
arbitragem EXIT→ENTRY, causalidade estrutural (ignora t), long-only rígido, stateless.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.families.rsi import RSIMeanReversionStrategy


def _df_from_closes(closes: list[float]) -> pd.DataFrame:
    n = len(closes)
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    idx = pd.date_range(start=start, periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": closes,
            "high": [c + 0.001 for c in closes],
            "low": [c - 0.001 for c in closes],
            "close": closes,
            "volume": [1.0] * n,
        },
        index=idx,
    )


class TestValidacaoParametros:
    def test_period_zero_levanta(self) -> None:
        with pytest.raises(ValueError, match="period deve ser > 0"):
            RSIMeanReversionStrategy(period=0, oversold=30.0, overbought=70.0)

    def test_period_negativo_levanta(self) -> None:
        with pytest.raises(ValueError, match="period deve ser > 0"):
            RSIMeanReversionStrategy(period=-3, oversold=30.0, overbought=70.0)

    def test_period_tipo_nao_int_levanta(self) -> None:
        with pytest.raises(TypeError, match="period deve ser int"):
            RSIMeanReversionStrategy(period=14.0, oversold=30.0, overbought=70.0)  # type: ignore[arg-type]

    def test_period_bool_rejeitado(self) -> None:
        with pytest.raises(TypeError, match="period deve ser int"):
            RSIMeanReversionStrategy(period=True, oversold=30.0, overbought=70.0)  # type: ignore[arg-type]

    def test_oversold_fora_do_range_inferior_levanta(self) -> None:
        with pytest.raises(ValueError, match="oversold deve estar em"):
            RSIMeanReversionStrategy(period=14, oversold=0.0, overbought=70.0)

    def test_oversold_fora_do_range_superior_levanta(self) -> None:
        with pytest.raises(ValueError, match="oversold deve estar em"):
            RSIMeanReversionStrategy(period=14, oversold=50.0, overbought=70.0)

    def test_oversold_tipo_nao_numerico_levanta(self) -> None:
        with pytest.raises(TypeError, match="oversold deve ser float"):
            RSIMeanReversionStrategy(period=14, oversold="30", overbought=70.0)  # type: ignore[arg-type]

    def test_oversold_bool_rejeitado(self) -> None:
        with pytest.raises(TypeError, match="oversold deve ser float"):
            RSIMeanReversionStrategy(period=14, oversold=True, overbought=70.0)  # type: ignore[arg-type]

    def test_overbought_fora_do_range_inferior_levanta(self) -> None:
        with pytest.raises(ValueError, match="overbought deve estar em"):
            RSIMeanReversionStrategy(period=14, oversold=30.0, overbought=50.0)

    def test_overbought_fora_do_range_superior_levanta(self) -> None:
        with pytest.raises(ValueError, match="overbought deve estar em"):
            RSIMeanReversionStrategy(period=14, oversold=30.0, overbought=100.0)

    def test_overbought_tipo_nao_numerico_levanta(self) -> None:
        with pytest.raises(TypeError, match="overbought deve ser float"):
            RSIMeanReversionStrategy(period=14, oversold=30.0, overbought="70")  # type: ignore[arg-type]

    def test_overbought_bool_rejeitado(self) -> None:
        with pytest.raises(TypeError, match="overbought deve ser float"):
            RSIMeanReversionStrategy(period=14, oversold=30.0, overbought=True)  # type: ignore[arg-type]

    def test_oversold_int_aceito_e_coergido_para_float(self) -> None:
        s = RSIMeanReversionStrategy(period=14, oversold=30, overbought=70)
        assert isinstance(s.oversold, float)
        assert isinstance(s.overbought, float)
        assert s.oversold == 30.0
        assert s.overbought == 70.0

    def test_long_only_false_aceito_apos_adr_0051(self) -> None:
        s = RSIMeanReversionStrategy(
            period=14, oversold=30.0, overbought=70.0, long_only=False
        )
        assert s.long_only is False

    def test_long_only_tipo_nao_bool_levanta(self) -> None:
        with pytest.raises(TypeError, match="long_only deve ser bool"):
            RSIMeanReversionStrategy(
                period=14, oversold=30.0, overbought=70.0, long_only=1  # type: ignore[arg-type]
            )


class TestWarmUp:
    def test_janela_insuficiente_retorna_hold(self) -> None:
        s = RSIMeanReversionStrategy(period=5, oversold=30.0, overbought=70.0)
        # precisa period+3 = 8; 7 barras é insuficiente
        df = _df_from_closes([100.0] * 7)
        assert s.decide(df) == Signal.HOLD

    def test_janela_exata_ativa(self) -> None:
        s = RSIMeanReversionStrategy(period=5, oversold=30.0, overbought=70.0)
        # 8 barras; flat → avg_loss_now=0 → rsi_now=100 → nem exit nem entry → HOLD
        df = _df_from_closes([100.0] * 8)
        assert s.decide(df) == Signal.HOLD


class TestEntradaCruzandoOversold:
    """Entrada long: rsi_now < oversold e rsi_prev >= oversold (cruzou PARA dentro)."""

    def test_perdas_consecutivas_cruzam_oversold(self) -> None:
        # Construção: sequência com ganhos até quase no fim, depois uma perda forte
        # que derruba RSI em t-1 para abaixo de 30, enquanto t-2 estava >= 30.
        # closes[:-1] tem 7 valores; deltas tem 6 valores.
        # period=4 → gains/losses_now = últimos 4 deltas; prev = deltas[-5:-1].
        s = RSIMeanReversionStrategy(period=4, oversold=30.0, overbought=70.0)
        # closes[:-1] = [100, 105, 110, 115, 120, 125, 80]. Deltas = [5,5,5,5,5,-45]
        # now_slice (últimos 4 deltas): [5,5,5,-45]. gains=[5,5,5,0], losses=[0,0,0,45].
        # avg_gain=15/4=3.75, avg_loss=45/4=11.25. rs=3.75/11.25=0.333. rsi_now=100-100/1.333=24.98 (<30 ✓)
        # prev_slice (deltas[-5:-1]): [5,5,5,5]. avg_loss_prev=0 → rsi_prev=100 (>=30 ✓).
        # Cruzou!
        closes = [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 80.0, 999.0]
        df = _df_from_closes(closes)
        assert s.decide(df) == Signal.ENTER_LONG

    def test_ja_dentro_do_oversold_sem_cruzar_retorna_hold(self) -> None:
        # Construção onde AMBOS rsi_now e rsi_prev ficam < 30 → não cruzou
        s = RSIMeanReversionStrategy(period=4, oversold=30.0, overbought=70.0)
        # Perdas consecutivas pesadas: deltas = [-20,-20,-20,-20,-20,-20]
        # Qualquer slice de 4 → avg_gain=0 → rsi=0. Ambos rsi_now e rsi_prev = 0 < 30 → não cruzou.
        closes = [200.0, 180.0, 160.0, 140.0, 120.0, 100.0, 80.0, 999.0]
        df = _df_from_closes(closes)
        assert s.decide(df) == Signal.HOLD

    def test_preco_flat_retorna_hold(self) -> None:
        s = RSIMeanReversionStrategy(period=5, oversold=30.0, overbought=70.0)
        df = _df_from_closes([100.0] * 10)
        # rsi = 100 (avg_loss=0) em ambos → HOLD
        assert s.decide(df) == Signal.HOLD


class TestSaidaCruzandoMeio:
    """Saída: rsi_now >= 50 e rsi_prev < 50 (cruzou DE BAIXO para cima)."""

    def test_ganho_forte_apos_perdas_cruza_50(self) -> None:
        s = RSIMeanReversionStrategy(period=4, oversold=30.0, overbought=70.0)
        # closes[:-1] = [100, 90, 80, 70, 60, 50, 150]. Deltas=[-10,-10,-10,-10,-10,100]
        # now_slice (últimos 4 deltas): [-10,-10,-10,100]. gains=[0,0,0,100]. losses=[10,10,10,0]
        # avg_gain=25, avg_loss=7.5. rs=25/7.5=3.333. rsi_now=100-100/4.333=76.92 (>=50 ✓)
        # prev_slice deltas[-5:-1] = [-10,-10,-10,-10]. avg_gain=0 → rsi_prev=0 (<50 ✓)
        # Cruzou!
        closes = [100.0, 90.0, 80.0, 70.0, 60.0, 50.0, 150.0, 999.0]
        df = _df_from_closes(closes)
        assert s.decide(df) == Signal.EXIT

    def test_ja_acima_de_50_nao_emite_exit(self) -> None:
        # Ambos rsi_now e rsi_prev >= 50 → não cruzou
        s = RSIMeanReversionStrategy(period=4, oversold=30.0, overbought=70.0)
        # Ganhos consistentes: deltas todos positivos → avg_loss=0 → rsi=100 em ambos
        closes = [100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 999.0]
        df = _df_from_closes(closes)
        assert s.decide(df) == Signal.HOLD


class TestArbitragemEntradaSaidaSimultaneas:
    """Edge-case: ambos disparam simultaneamente → EXIT vence.

    Estruturalmente impossível em inputs reais (rsi_now não pode ser <30 E >=50
    simultaneamente). Teste documenta a arbitragem ordinal.
    """

    def test_estruturalmente_impossivel_ambos_disparam(self) -> None:
        s = RSIMeanReversionStrategy(period=5, oversold=30.0, overbought=70.0)
        df = _df_from_closes([100.0] * 10)
        assert s.decide(df) == Signal.HOLD


class TestIgnoraBarraCorrente:
    """Mutar window.iloc[-1] em OHLC — decisão não muda."""

    def test_mutar_barra_t_nao_muda_decisao(self) -> None:
        s = RSIMeanReversionStrategy(period=4, oversold=30.0, overbought=70.0)
        closes = [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 80.0, 100.0]
        df = _df_from_closes(closes)
        decision_original = s.decide(df)

        df_mut = df.copy()
        df_mut.iloc[-1, df_mut.columns.get_loc("close")] = 1e9
        df_mut.iloc[-1, df_mut.columns.get_loc("high")] = 1e9
        df_mut.iloc[-1, df_mut.columns.get_loc("low")] = -1e9
        df_mut.iloc[-1, df_mut.columns.get_loc("open")] = 1e9

        decision_mutada = s.decide(df_mut)
        assert decision_original == decision_mutada
        assert decision_original == Signal.ENTER_LONG


class TestLongOnly:
    """Universo de saída é {ENTER_LONG, EXIT, HOLD}. Nunca ENTER_SHORT."""

    def test_universo_sinais_restrito(self) -> None:
        s = RSIMeanReversionStrategy(period=5, oversold=30.0, overbought=70.0)
        import random
        random.seed(42)
        for _ in range(50):
            n = random.randint(8, 30)
            closes = [random.uniform(50.0, 150.0) for _ in range(n)]
            df = _df_from_closes(closes)
            sig = s.decide(df)
            assert sig in (Signal.ENTER_LONG, Signal.EXIT, Signal.HOLD)


class TestStateless:
    """Chamar decide() em sequência não acumula estado."""

    def test_mesma_janela_mesmo_resultado(self) -> None:
        s = RSIMeanReversionStrategy(period=4, oversold=30.0, overbought=70.0)
        closes = [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 80.0, 100.0]
        df = _df_from_closes(closes)
        r1 = s.decide(df)
        r2 = s.decide(df)
        r3 = s.decide(df)
        assert r1 == r2 == r3

    def test_nenhum_atributo_privado_alem_dos_parametros(self) -> None:
        s = RSIMeanReversionStrategy(period=14, oversold=30.0, overbought=70.0)
        closes = [100.0] * 20
        s.decide(_df_from_closes(closes))
        public_attrs = {
            name for name in vars(s) if not name.startswith("__")
        }
        assert public_attrs == {"period", "oversold", "overbought", "long_only"}
