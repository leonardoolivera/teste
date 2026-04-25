"""Unit tests de `validation.monte_carlo_trades` (ADR-0003).

Cobre contrato de parâmetros, reprodutibilidade (mesma terna →
`MonteCarloSummary` idêntico), shape dos percentis e rejeição de `result`
sem trades.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from alpha_forge.backtest.schemas import (
    BacktestMetrics,
    BacktestResult,
    Side,
    Trade,
)
from alpha_forge.validation import ValidationError, monte_carlo_trades


def _make_result(pnls: list[float]) -> BacktestResult:
    trades = [
        Trade(
            side=Side.LONG,
            entry_timestamp=datetime(2026, 1, i + 1, tzinfo=timezone.utc),
            exit_timestamp=datetime(2026, 1, i + 2, tzinfo=timezone.utc),
            entry_price=100.0,
            exit_price=100.0 + pnl,
            size=1.0,
            pnl=pnl,
        )
        for i, pnl in enumerate(pnls)
    ]
    final_equity = 10_000.0 + sum(pnls)
    return BacktestResult(
        dataset_id="fixture",
        bars=len(pnls) * 2,
        fills=[],
        rejections=[],
        trades=trades,
        final_equity=final_equity,
        max_equity=final_equity,
        min_equity=final_equity,
        equity_curve=[
            (datetime(2026, 1, 1, tzinfo=timezone.utc), 10_000.0),
            (datetime(2026, 1, 2, tzinfo=timezone.utc), final_equity),
        ],
        metrics=BacktestMetrics(
            total_pnl=sum(pnls),
            trade_count=len(trades),
            hit_rate=sum(1 for p in pnls if p > 0) / len(pnls) if pnls else None,
            max_drawdown=0.0,
        ),
    )


class TestValidacaoParametros:
    def test_n_resamples_minimo_100(self) -> None:
        result = _make_result([10.0, -5.0])
        with pytest.raises(ValidationError, match="n_resamples"):
            monte_carlo_trades(
                result=result,
                capital_inicial=10_000.0,
                n_resamples=50,
                seed=42,
            )

    def test_capital_positivo(self) -> None:
        result = _make_result([10.0, -5.0])
        with pytest.raises(ValidationError, match="capital_inicial"):
            monte_carlo_trades(
                result=result, capital_inicial=0.0, n_resamples=100, seed=42
            )

    def test_result_sem_trades_rejeitado(self) -> None:
        result = _make_result([])
        with pytest.raises(ValidationError, match="result.trades"):
            monte_carlo_trades(
                result=result,
                capital_inicial=10_000.0,
                n_resamples=100,
                seed=42,
            )


class TestReprodutibilidade:
    def test_mesma_terna_mesmo_summary(self) -> None:
        result = _make_result([10.0, -5.0, 7.0, -3.0, 12.0])
        s1 = monte_carlo_trades(
            result=result, capital_inicial=10_000.0, n_resamples=500, seed=42
        )
        s2 = monte_carlo_trades(
            result=result, capital_inicial=10_000.0, n_resamples=500, seed=42
        )
        assert s1 == s2

    def test_seed_diferente_resultado_diferente(self) -> None:
        result = _make_result([10.0, -5.0, 7.0, -3.0, 12.0, -8.0])
        s1 = monte_carlo_trades(
            result=result, capital_inicial=10_000.0, n_resamples=500, seed=42
        )
        s2 = monte_carlo_trades(
            result=result, capital_inicial=10_000.0, n_resamples=500, seed=43
        )
        assert s1 != s2


class TestShape:
    def test_percentis_fixos(self) -> None:
        result = _make_result([10.0, -5.0, 7.0])
        summary = monte_carlo_trades(
            result=result,
            capital_inicial=10_000.0,
            n_resamples=200,
            seed=42,
        )
        assert set(summary.final_equity_percentiles) == {5, 25, 50, 75, 95}
        assert set(summary.max_drawdown_percentiles) == {5, 25, 50, 75, 95}

    def test_percentis_ordenados(self) -> None:
        result = _make_result([10.0, -5.0, 7.0, -12.0, 8.0, 3.0, -4.0])
        summary = monte_carlo_trades(
            result=result,
            capital_inicial=10_000.0,
            n_resamples=1000,
            seed=42,
        )
        keys = (5, 25, 50, 75, 95)
        values = [summary.final_equity_percentiles[k] for k in keys]
        assert values == sorted(values)
        dd_values = [summary.max_drawdown_percentiles[k] for k in keys]
        assert dd_values == sorted(dd_values)

    def test_original_metrics_refletidas(self) -> None:
        result = _make_result([10.0, -5.0, 7.0])
        summary = monte_carlo_trades(
            result=result,
            capital_inicial=10_000.0,
            n_resamples=200,
            seed=42,
        )
        assert summary.original_final_equity == result.final_equity
        assert summary.original_max_drawdown == result.metrics.max_drawdown
