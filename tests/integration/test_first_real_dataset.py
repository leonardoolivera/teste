"""Integration: pipeline completo sobre datasets reais, multi-ativo.

Roda MA crossover 20/50 e Donchian 20/10 sobre cada dataset real cadastrado
em `data/datasets.yaml` (BTCUSDT, ETHUSDT, SOLUSDT — todos 1h 2025-07-05 →
2025-12-31). Em ambiente fresco sem Parquet em disco, cada caso faz skip
limpo — a suíte inteira continua verde.

Este teste **não valida rentabilidade** de edge; valida estruturalmente que o
pipeline (loader → estratégia → engine causal → métricas) é agnóstico a
símbolo (ADR-0009 §2-bis — anti-hardcode) e se comporta dentro dos contratos
declarados (causalidade ADR-0002; métricas ADR-0007; reverse-on-signal
ADR-0012 não dispara em estratégias long-only, nenhum fill compartilha
timestamp). Se algo no pipeline quebrar com dado real (timezone divergente,
timeframe-step errado, dtype pandas diferente, ativo com preço fora do
range visto antes), é aqui que pega.
"""

from __future__ import annotations

from typing import Callable

import pytest

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import StrategyProtocol, run_backtest
from alpha_forge.data.loaders import (
    DatasetIntegrityError,
    DatasetNotFoundError,
    load_dataset,
)
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.donchian import DonchianBreakoutStrategy
from alpha_forge.strategies.families.ma_crossover import (
    MovingAverageCrossoverStrategy,
)


REAL_DATASET_IDS = (
    "btcusdt_1h_20250705_20251231_binance_spot",
    "ethusdt_1h_20250705_20251231_binance_spot",
    "solusdt_1h_20250705_20251231_binance_spot",
)


def _ma_20_50() -> StrategyProtocol:
    return MovingAverageCrossoverStrategy(short_window=20, long_window=50)


def _donchian_20_10() -> StrategyProtocol:
    return DonchianBreakoutStrategy(entry_window=20, exit_window=10)


STRATEGY_FACTORIES: tuple[tuple[str, Callable[[], StrategyProtocol]], ...] = (
    ("ma_crossover_20_50", _ma_20_50),
    ("donchian_20_10", _donchian_20_10),
)


@pytest.mark.parametrize("dataset_id", REAL_DATASET_IDS)
@pytest.mark.parametrize(
    "strategy_label,strategy_factory",
    STRATEGY_FACTORIES,
    ids=[lbl for lbl, _ in STRATEGY_FACTORIES],
)
def test_pipeline_roda_sobre_dataset_real(
    dataset_id: str,
    strategy_label: str,
    strategy_factory: Callable[[], StrategyProtocol],
) -> None:
    try:
        prices = load_dataset(dataset_id)
    except (DatasetNotFoundError, FileNotFoundError, DatasetIntegrityError) as exc:
        pytest.skip(
            f"dataset real '{dataset_id}' ausente ou inválido "
            f"(rode `uv run python scripts/ingest_binance_vision.py` para o símbolo "
            f"correspondente): {exc}"
        )

    assert prices.index.tz is not None
    assert str(prices.index.tz) == "UTC"
    assert len(prices) >= 100
    assert set(prices.columns) >= {"open", "high", "low", "close", "volume"}

    budget = RiskBudget(
        capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
    )
    cost_model = CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=2.0)

    result = run_backtest(
        prices=prices,
        strategy=strategy_factory(),
        budget=budget,
        cost_model=cost_model,
        dataset_id=dataset_id,
    )

    # Estrutural — nenhuma assert sobre PnL esperado.
    assert result.bars == len(prices)
    assert len(result.equity_curve) == len(prices)
    assert result.equity_curve[0][1] == budget.capital_inicial
    assert result.final_equity > 0
    assert result.final_equity == result.final_equity  # not NaN
    assert result.max_equity >= result.min_equity

    assert result.metrics is not None
    assert result.metrics.trade_count >= 0
    if result.metrics.trade_count > 0:
        assert result.metrics.hit_rate is not None
        assert 0.0 <= result.metrics.hit_rate <= 1.0
    else:
        assert result.metrics.hit_rate is None
    assert 0.0 <= result.metrics.max_drawdown <= 1.0

    # Causalidade estrutural (ADR-0002): toda execução ocorre estritamente depois do sinal.
    assert all(f.timestamp > f.signal_timestamp for f in result.fills)

    # Reverse-on-signal (ADR-0012) nunca dispara em estratégias long-only:
    # nenhum par consecutivo de fills compartilha timestamp.
    timestamps = [f.timestamp for f in result.fills]
    for i in range(1, len(timestamps)):
        assert timestamps[i] != timestamps[i - 1], (
            f"fills consecutivos com mesma ts_exec em estratégia long-only "
            f"({strategy_label} / {dataset_id}): idx={i}, ts={timestamps[i]!r}"
        )
