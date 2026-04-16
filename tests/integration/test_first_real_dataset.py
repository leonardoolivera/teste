"""Integration: MA crossover 20/50 sobre o primeiro dataset real (ADR-0009).

Este teste só roda se o dataset já foi ingerido. Em ambiente fresco (clone
novo, sem rede, sem Parquet em disco), faz skip limpo — a suíte inteira
continua verde.

O objetivo aqui **não** é validar rentabilidade da estratégia. É fechar o
loop completo: dataset real → loader → engine causal → BacktestResult com
métricas finitas e plausíveis. Se algo no pipeline quebrar com dado real
(timezone divergente, timeframe-step errado, dtype pandas diferente), é
aqui que pega.
"""

from __future__ import annotations

import pytest

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.data.loaders import (
    DatasetIntegrityError,
    DatasetNotFoundError,
    load_dataset,
)
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import (
    MovingAverageCrossoverStrategy,
)


REAL_DATASET_ID = "btcusdt_1h_20250705_20251231_binance_spot"


def test_ma_crossover_roda_sobre_dataset_real() -> None:
    try:
        prices = load_dataset(REAL_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError, DatasetIntegrityError) as exc:
        pytest.skip(
            f"dataset real '{REAL_DATASET_ID}' ausente ou inválido "
            f"(rode `uv run python scripts/ingest_binance_vision.py --symbols BTCUSDT "
            f"--timeframe 1h --start 2025-07-05 --end 2025-12-31`): {exc}"
        )

    assert prices.index.tz is not None
    assert str(prices.index.tz) == "UTC"
    assert len(prices) >= 100
    assert set(prices.columns) >= {"open", "high", "low", "close", "volume"}

    budget = RiskBudget(
        capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
    )
    cost_model = CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=2.0)
    strategy = MovingAverageCrossoverStrategy(short_window=20, long_window=50)

    result = run_backtest(
        prices=prices,
        strategy=strategy,
        budget=budget,
        cost_model=cost_model,
        dataset_id=REAL_DATASET_ID,
    )

    assert result.bars == len(prices)
    assert len(result.equity_curve) == len(prices)
    assert result.equity_curve[0][1] == budget.capital_inicial
    assert result.final_equity > 0
    assert result.metrics is not None
    assert result.metrics.trade_count >= 0
    if result.metrics.trade_count > 0:
        assert result.metrics.hit_rate is not None
        assert 0.0 <= result.metrics.hit_rate <= 1.0
    else:
        assert result.metrics.hit_rate is None
    assert 0.0 <= result.metrics.max_drawdown <= 1.0

    # Causalidade estrutural: toda execução ocorre estritamente depois do sinal.
    assert all(f.timestamp > f.signal_timestamp for f in result.fills)
