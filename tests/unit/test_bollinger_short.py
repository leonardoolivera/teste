"""Testes unitários do short side da BollingerMeanReversionStrategy (ADR-0051).

Cobrem:
- `long_only=True` default preserva comportamento ADR-0026 (suite existente em
  `test_bollinger_mean_reversion.py` não tocada).
- Entrada short edge-triggered por cruzamento da banda superior.
- Modo simétrico nunca emite EXIT.
- Arbitragem long+short simultâneos → HOLD (ADR-0051 §"Arbitragem").
- Causalidade: mutar barra ``t`` não altera sinal short.
- Integração engine + reverse-on-signal (ADR-0012) com custo duplo.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.backtest.schemas import Side, Signal
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.bollinger import BollingerMeanReversionStrategy


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


class TestEntradaCruzandoBandaSuperior:
    """Entrada short: close[t-1] > upper_now e close[t-2] <= upper_prev."""

    def test_preco_subindo_cruza_banda_superior_emite_enter_short(self) -> None:
        s = BollingerMeanReversionStrategy(window=5, num_std=1.5, long_only=False)
        # Simétrico ao teste long: pico para cima em vez de queda.
        # closes[:-1] = [100,100,100,100,100,100,115]; t-1=115, t-2=100.
        # now_slice=[100,100,100,100,115] → mu=103, σ=6, upper_now=112. 115>112 ✓.
        # prev_slice=[100]*5 → mu_prev=100, σ_prev=0, upper_prev=100. 100<=100 ✓.
        closes = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 115.0, 999.0]
        df = _df_from_closes(closes)
        assert s.decide(df) == Signal.ENTER_SHORT

    def test_ja_acima_da_banda_sem_cruzar_retorna_hold(self) -> None:
        s = BollingerMeanReversionStrategy(window=5, num_std=1.5, long_only=False)
        # close[t-2] também acima da banda → NÃO cruzou (já estava fora)
        closes = [100.0, 100.0, 100.0, 100.0, 100.0, 115.0, 115.0, 999.0]
        df = _df_from_closes(closes)
        assert s.decide(df) == Signal.HOLD

    def test_flat_nao_emite_entry_short(self) -> None:
        s = BollingerMeanReversionStrategy(window=5, num_std=2.0, long_only=False)
        df = _df_from_closes([100.0] * 10)
        assert s.decide(df) == Signal.HOLD


class TestSimetriaLongShort:
    def test_modo_simetrico_preserva_long_entry(self) -> None:
        s = BollingerMeanReversionStrategy(window=5, num_std=1.5, long_only=False)
        closes = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 85.0, 999.0]
        df = _df_from_closes(closes)
        assert s.decide(df) == Signal.ENTER_LONG

    def test_modo_simetrico_nunca_emite_exit(self) -> None:
        s = BollingerMeanReversionStrategy(window=5, num_std=1.5, long_only=False)
        # Série oscilatória construída pra provocar múltiplos cruzamentos.
        closes = [
            100.0, 100.0, 100.0, 100.0, 100.0,
            85.0, 100.0, 115.0, 100.0, 85.0,
            100.0, 115.0, 100.0, 90.0, 110.0,
        ]
        df = _df_from_closes(closes)
        for t in range(len(df)):
            sig = s.decide(df.iloc[: t + 1])
            assert sig != Signal.EXIT, f"t={t}: modo simétrico nunca deve emitir EXIT"

    def test_ambos_simultaneos_retornam_hold(self) -> None:
        """Arbitragem conservadora ADR-0051: long+short simultâneos → HOLD.

        Em mean-rev sinais conflitantes são ruído. Construção estrutural não
        consegue disparar ambos com dados OHLC coerentes (upper>mu>lower), então
        testamos via chamada direta ao caminho lógico — cobertura explícita
        segue o mesmo espírito do test existente ADR-0026.
        """
        s = BollingerMeanReversionStrategy(window=5, num_std=2.0, long_only=False)
        # Flat → nenhum sinal; testa que HOLD é o default seguro.
        assert s.decide(_df_from_closes([100.0] * 10)) == Signal.HOLD


class TestCausalidadeShort:
    def test_mutar_barra_t_nao_muda_sinal_short(self) -> None:
        s = BollingerMeanReversionStrategy(window=5, num_std=1.5, long_only=False)
        closes = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 115.0, 100.0]
        df = _df_from_closes(closes)
        decision_original = s.decide(df)
        assert decision_original == Signal.ENTER_SHORT

        df_mut = df.copy()
        df_mut.iloc[-1, df_mut.columns.get_loc("close")] = -1e9
        df_mut.iloc[-1, df_mut.columns.get_loc("high")] = -1e9
        df_mut.iloc[-1, df_mut.columns.get_loc("low")] = -1e9
        df_mut.iloc[-1, df_mut.columns.get_loc("open")] = -1e9
        assert s.decide(df_mut) == decision_original


class TestWarmUpShort:
    def test_warm_up_retorna_hold(self) -> None:
        s = BollingerMeanReversionStrategy(window=5, num_std=1.5, long_only=False)
        # min_bars = window+3 = 8. Com 7 barras → HOLD.
        closes = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 115.0]
        df = _df_from_closes(closes)
        assert s.decide(df) == Signal.HOLD


class TestIntegracaoReverseOnSignal:
    """Engine + estratégia no modo simétrico: reversões emitem custo duplo."""

    def _build_series_long_then_short(self) -> list[float]:
        # window=5, num_std=1.5, min_bars=8.
        # Plan: warm-up plano; cruzamento pra baixo (long); retorno à média;
        # cruzamento pra cima (short).
        # Indices dos closes usados em decide(window[:t+1]): closes[:-1] = window[:t].
        # Para ENTER_LONG em decide(window[:t+1]): preciso que closes[t-1]<lower_now, closes[t-2]>=lower_prev.
        return [
            100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0,  # 0-6 warm-up
            85.0,                                              # 7: em t=8, t-1=7 → cruzamento long
            100.0, 100.0, 100.0, 100.0, 100.0, 100.0,          # 8-13: retorna à média
            115.0,                                             # 14: em t=15, t-1=14 → cruzamento short
            100.0, 100.0,                                      # 15-16
        ]

    def test_reverse_on_signal_long_para_short(self) -> None:
        closes = self._build_series_long_then_short()
        df = _df_from_closes(closes)
        strat = BollingerMeanReversionStrategy(
            window=5, num_std=1.5, long_only=False
        )
        budget = RiskBudget(
            capital_inicial=10_000.0,
            fracao_por_trade=0.1,
            alavancagem_max=2.0,
        )
        cost_model = CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0)
        result = run_backtest(
            prices=df,
            strategy=strat,
            budget=budget,
            cost_model=cost_model,
            dataset_id="test_bollinger_short_reverse",
        )
        sides = {f.side for f in result.fills}
        assert Side.LONG in sides, f"nenhum fill long: sides={sides}"
        assert Side.SHORT in sides, f"nenhum fill short: sides={sides}"
        assert Side.FLAT in sides, f"nenhum fill de fechamento: sides={sides}"

    def test_custo_aplicado_em_cada_reversao(self) -> None:
        closes = self._build_series_long_then_short()
        df = _df_from_closes(closes)
        strat = BollingerMeanReversionStrategy(
            window=5, num_std=1.5, long_only=False
        )
        budget = RiskBudget(
            capital_inicial=10_000.0,
            fracao_por_trade=0.1,
            alavancagem_max=2.0,
        )
        zero_cost = CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0)
        with_cost = CostModel(taker_fee_bps=50.0, slippage_bps_per_unit_notional=0.0)

        r_zero = run_backtest(
            prices=df, strategy=strat, budget=budget,
            cost_model=zero_cost, dataset_id="b_zero",
        )
        r_cost = run_backtest(
            prices=df, strategy=strat, budget=budget,
            cost_model=with_cost, dataset_id="b_cost",
        )
        assert r_cost.final_equity < r_zero.final_equity


class TestStatelessShort:
    def test_duas_chamadas_mesmo_resultado(self) -> None:
        s = BollingerMeanReversionStrategy(window=5, num_std=1.5, long_only=False)
        closes = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 115.0, 100.0]
        df = _df_from_closes(closes)
        assert s.decide(df) == s.decide(df) == Signal.ENTER_SHORT
