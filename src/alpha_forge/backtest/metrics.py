"""Métricas mínimas do núcleo (ADR-0007).

Função pura `compute_metrics` — não toca em I/O, não depende de estado global.
Vive em `backtest/` porque caracteriza um backtest; `ranking/scoring/` é para
comparação entre estratégias (fase futura).
"""

from __future__ import annotations

from alpha_forge.backtest.schemas import BacktestMetrics, BacktestResult


def compute_metrics(result: BacktestResult, capital_inicial: float) -> BacktestMetrics:
    """Calcula as quatro métricas mínimas a partir de um `BacktestResult`.

    - `total_pnl = final_equity - capital_inicial` (absoluto).
    - `trade_count = len(result.trades)` (só trades fechados).
    - `hit_rate = (# trades com pnl>0) / trade_count`, ou `None` se sem trades.
    - `max_drawdown = max(1 - equity / running_max)`, ∈ [0, 1], 0 se monotônica.
    """
    total_pnl = result.final_equity - capital_inicial
    trade_count = len(result.trades)
    hit_rate = (
        sum(1 for t in result.trades if t.pnl > 0) / trade_count
        if trade_count > 0
        else None
    )
    max_drawdown = _max_drawdown([v for _, v in result.equity_curve])

    return BacktestMetrics(
        total_pnl=total_pnl,
        trade_count=trade_count,
        hit_rate=hit_rate,
        max_drawdown=max_drawdown,
    )


def _max_drawdown(equity: list[float]) -> float:
    if not equity:
        return 0.0
    running_max = equity[0]
    worst = 0.0
    for v in equity:
        if v > running_max:
            running_max = v
        if running_max <= 0.0:
            continue
        dd = 1.0 - (v / running_max)
        if dd > 1.0:
            dd = 1.0
        if dd > worst:
            worst = dd
    return worst
