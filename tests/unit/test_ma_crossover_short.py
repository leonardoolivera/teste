"""Testes unitários do short side da MovingAverageCrossoverStrategy (ADR-0012).

Cobrem:
- `long_only=True` (default) preserva comportamento ADR-0008 bit-a-bit.
- Validação estrita de `long_only`.
- Simetria de sinais no modo `long_only=False`.
- Integração engine + estratégia com reverse-on-signal (LONG→SHORT→LONG).

A suite ADR-0008 em `test_ma_crossover.py` permanece intocada.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.backtest.schemas import Side, Signal
from alpha_forge.risk.schemas import RiskBudget
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


class TestDefaultPreservaLongOnly:
    """Construtor sem `long_only` deve ser idêntico ao comportamento ADR-0008."""

    def test_default_long_only_e_true(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        assert strat.long_only is True

    def test_cross_down_no_default_emite_exit_nao_short(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        closes = [10.0, 20.0, 30.0, 40.0, 1.0]
        df = _df_from_closes(closes)
        sig = strat.decide(df)
        assert sig == Signal.EXIT
        assert sig != Signal.ENTER_SHORT

    def test_cross_up_no_default_emite_enter_long(self) -> None:
        strat = MovingAverageCrossoverStrategy(short_window=2, long_window=3)
        closes = [10.0, 10.0, 10.0, 1.0, 50.0]
        df = _df_from_closes(closes)
        assert strat.decide(df) == Signal.ENTER_LONG


class TestValidacaoLongOnly:
    def test_int_nao_aceito(self) -> None:
        with pytest.raises(TypeError, match="long_only deve ser bool"):
            MovingAverageCrossoverStrategy(short_window=2, long_window=3, long_only=1)  # type: ignore[arg-type]

    def test_none_nao_aceito(self) -> None:
        with pytest.raises(TypeError, match="long_only deve ser bool"):
            MovingAverageCrossoverStrategy(
                short_window=2, long_window=3, long_only=None  # type: ignore[arg-type]
            )

    def test_string_nao_aceito(self) -> None:
        with pytest.raises(TypeError, match="long_only deve ser bool"):
            MovingAverageCrossoverStrategy(
                short_window=2, long_window=3, long_only="true"  # type: ignore[arg-type]
            )

    def test_bool_explicito_aceito(self) -> None:
        a = MovingAverageCrossoverStrategy(short_window=2, long_window=3, long_only=True)
        b = MovingAverageCrossoverStrategy(short_window=2, long_window=3, long_only=False)
        assert a.long_only is True
        assert b.long_only is False


class TestSimetriaSinais:
    """No modo `long_only=False`, cross-down emite ENTER_SHORT; cross-up emite ENTER_LONG."""

    def test_cross_down_emite_enter_short(self) -> None:
        strat = MovingAverageCrossoverStrategy(
            short_window=2, long_window=3, long_only=False
        )
        closes = [10.0, 20.0, 30.0, 40.0, 1.0]
        df = _df_from_closes(closes)
        assert strat.decide(df) == Signal.ENTER_SHORT

    def test_cross_up_emite_enter_long_mesmo_em_modo_simetrico(self) -> None:
        strat = MovingAverageCrossoverStrategy(
            short_window=2, long_window=3, long_only=False
        )
        closes = [10.0, 10.0, 10.0, 1.0, 50.0]
        df = _df_from_closes(closes)
        assert strat.decide(df) == Signal.ENTER_LONG

    def test_nunca_emite_exit_em_modo_simetrico(self) -> None:
        """Modo simétrico não usa EXIT — reversões são tratadas pelo engine."""
        strat = MovingAverageCrossoverStrategy(
            short_window=3, long_window=5, long_only=False
        )
        # Série com várias cross-ups e cross-downs alternadas
        closes = [
            100.0, 100.0, 100.0, 100.0, 100.0,
            90.0, 80.0, 70.0, 60.0,  # cross-down eventual
            70.0, 90.0, 120.0, 150.0,  # cross-up eventual
            130.0, 100.0, 70.0, 40.0,  # cross-down de novo
        ]
        df = _df_from_closes(closes)
        for t in range(len(df)):
            sig = strat.decide(df.iloc[: t + 1])
            assert sig != Signal.EXIT, f"t={t}: modo simétrico nunca deve emitir EXIT"

    def test_empate_exato_continua_nao_sendo_sinal(self) -> None:
        strat = MovingAverageCrossoverStrategy(
            short_window=2, long_window=3, long_only=False
        )
        closes = [1.0, 1.0, 1.0, 1.0, 1.0]
        df = _df_from_closes(closes)
        assert strat.decide(df) == Signal.HOLD


class TestLongToShort:
    """Integração engine + estratégia: duas reversões sucessivas em série construída."""

    def _build_series_with_two_reversals(self) -> list[float]:
        # Série suave que força: warm-up → cross-up → cross-down → cross-up.
        # short_window=2, long_window=3. Amplitudes pequenas para manter equity positivo
        # (contrato BacktestMetrics exige max_drawdown ∈ [0,1]).
        # Sequência construída e verificada manualmente:
        #   t0-t2: base plana (100, 100, 100) — warm-up.
        #   t3: 102 — short_ma sobe; short_prev<=long_prev, short_now>long_now → cross-up.
        #   t4-t5: 102, 102 — consolida long (nenhum cross novo).
        #   t6: 98 — short_ma cai; cross-down → ENTER_SHORT (reversa LONG→SHORT).
        #   t7-t8: 98, 98 — consolida short.
        #   t9: 102 — cross-up → ENTER_LONG (reversa SHORT→LONG).
        return [
            100.0, 100.0, 100.0,   # warm-up
            102.0, 102.0, 102.0,   # cross-up em t3 (LONG), consolida t4-t5
            98.0, 98.0, 98.0,      # cross-down em t6 (reverte p/ SHORT), consolida t7-t8
            102.0, 102.0,          # cross-up em t9 (reverte p/ LONG), consolida t10
        ]

    def test_reverse_on_signal_produz_trades_fechados_e_fills_duplos(self) -> None:
        closes = self._build_series_with_two_reversals()
        df = _df_from_closes(closes)
        strat = MovingAverageCrossoverStrategy(
            short_window=2, long_window=3, long_only=False
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
            dataset_id="test_long_to_short",
        )

        # Pelo menos dois trades fechados (LONG fechado via reversão + SHORT fechado via reversão)
        # O terceiro ENTER_LONG pode ficar aberto ao fim; MTM entra no final_equity, não no trade_count.
        assert result.metrics is not None
        assert result.metrics.trade_count >= 2, (
            f"esperava ao menos 2 trades fechados, veio {result.metrics.trade_count}"
        )

        # Deve haver pelo menos um fill com side=LONG e pelo menos um com side=SHORT.
        sides = {f.side for f in result.fills}
        assert Side.LONG in sides, "nenhum fill long registrado"
        assert Side.SHORT in sides, "nenhum fill short registrado"
        # Fill de fechamento é registrado com Side.FLAT
        assert Side.FLAT in sides, "nenhum fill de fechamento registrado"

    def test_reversao_aplica_custo_duas_vezes(self) -> None:
        """Custo duplo é parte da decisão ADR-0012: reverter = fechar + abrir."""
        closes = self._build_series_with_two_reversals()
        df = _df_from_closes(closes)
        strat = MovingAverageCrossoverStrategy(
            short_window=2, long_window=3, long_only=False
        )
        budget = RiskBudget(
            capital_inicial=10_000.0,
            fracao_por_trade=0.1,
            alavancagem_max=2.0,
        )
        zero_cost = CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0)
        with_cost = CostModel(taker_fee_bps=10.0, slippage_bps_per_unit_notional=0.0)

        r_zero = run_backtest(
            prices=df, strategy=strat, budget=budget,
            cost_model=zero_cost, dataset_id="t_zero",
        )
        r_cost = run_backtest(
            prices=df, strategy=strat, budget=budget,
            cost_model=with_cost, dataset_id="t_cost",
        )

        # Com custo > 0 e pelo menos uma reversão, final_equity com custo < sem custo
        assert r_cost.final_equity < r_zero.final_equity, (
            "custo deveria reduzir equity em série com reversões"
        )


class TestStateless:
    def test_duas_chamadas_mesma_janela_modo_simetrico(self) -> None:
        strat = MovingAverageCrossoverStrategy(
            short_window=2, long_window=3, long_only=False
        )
        closes = [10.0, 20.0, 30.0, 40.0, 1.0]
        df = _df_from_closes(closes)
        assert strat.decide(df) == strat.decide(df) == Signal.ENTER_SHORT
