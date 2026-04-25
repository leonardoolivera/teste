"""Monte Carlo sobre trades (ADR-0003).

Reamostra com reposição a lista de PnLs dos trades fechados; recomputa curva
de equity acumulada e `max_drawdown` em cada amostra. Não re-executa o
backtest — é resampling sobre trades já realizados.

**Limitação declarada**: assume i.i.d. de PnL por trade, o que é falso em
regimes com autocorrelação serial. Variantes que respeitam autocorrelação
(bootstrap em blocos, circular block bootstrap) são deferred (ADR-0003).
"""

from __future__ import annotations

import numpy as np

from alpha_forge.backtest.schemas import BacktestResult
from alpha_forge.validation.schemas import MonteCarloSummary
from alpha_forge.validation.walk_forward import ValidationError

_PERCENTILES = (5, 25, 50, 75, 95)


def monte_carlo_trades(
    *,
    result: BacktestResult,
    capital_inicial: float,
    n_resamples: int,
    seed: int,
) -> MonteCarloSummary:
    """Reamostra PnLs de trades e sumariza `final_equity` + `max_drawdown`.

    Reprodutibilidade: dois runs com a mesma terna `(result, n_resamples,
    seed)` produzem `MonteCarloSummary` idêntico. Usa
    `numpy.random.default_rng(seed)`.
    """
    if n_resamples < 100:
        raise ValidationError(
            f"n_resamples deve ser >= 100 (recebido {n_resamples})"
        )
    if capital_inicial <= 0.0:
        raise ValidationError(
            f"capital_inicial deve ser > 0 (recebido {capital_inicial})"
        )
    if not result.trades:
        raise ValidationError(
            "result.trades está vazio — Monte Carlo sobre trades requer ao "
            "menos 1 trade fechado"
        )

    pnls = np.asarray([t.pnl for t in result.trades], dtype=float)
    rng = np.random.default_rng(seed)

    final_equities = np.empty(n_resamples, dtype=float)
    max_drawdowns = np.empty(n_resamples, dtype=float)

    n_trades = len(pnls)
    for i in range(n_resamples):
        sampled = rng.choice(pnls, size=n_trades, replace=True)
        equity = capital_inicial + np.cumsum(sampled)
        running_max = np.maximum.accumulate(
            np.concatenate(([capital_inicial], equity))
        )
        full_equity = np.concatenate(([capital_inicial], equity))
        drawdowns = (running_max - full_equity) / running_max
        final_equities[i] = equity[-1]
        max_drawdowns[i] = float(drawdowns.max())

    final_percentiles = {
        p: float(np.percentile(final_equities, p)) for p in _PERCENTILES
    }
    dd_percentiles = {
        p: float(np.percentile(max_drawdowns, p)) for p in _PERCENTILES
    }

    original_dd = (
        result.metrics.max_drawdown if result.metrics is not None else 0.0
    )

    return MonteCarloSummary(
        n_resamples=n_resamples,
        seed=seed,
        final_equity_percentiles=final_percentiles,
        max_drawdown_percentiles=dd_percentiles,
        original_final_equity=result.final_equity,
        original_max_drawdown=original_dd,
    )
