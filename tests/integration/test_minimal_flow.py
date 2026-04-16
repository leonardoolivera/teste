"""Teste integration do fluxo end-to-end do núcleo mínimo.

Gera dataset sintético em diretório temporário, registra manifesto,
carrega com o loader real, roda o engine causal com a DummyAlternatingStrategy
sob um RiskBudget padrão, valida invariantes de saída.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.data.loaders import load_dataset
from alpha_forge.data.synthetic import generate_ohlcv
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.dummy import DummyAlternatingStrategy


def test_minimal_flow(tmp_path, monkeypatch) -> None:
    dataset_id = "integration_synth"
    df = generate_ohlcv(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc), periods=120, seed=7
    )
    pq_dir = tmp_path / "data" / "processed" / "SYNTH" / "1h"
    pq_dir.mkdir(parents=True, exist_ok=True)
    pq_path = pq_dir / f"{dataset_id}.parquet"
    df.to_parquet(pq_path, engine="pyarrow", compression="snappy")

    sha = hashlib.sha256(pq_path.read_bytes()).hexdigest()

    manifest_path = tmp_path / "data" / "datasets.yaml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "datasets": [
                    {
                        "dataset_id": dataset_id,
                        "symbol": "SYNTH",
                        "timeframe": "1h",
                        "path": f"SYNTH/1h/{dataset_id}.parquet",
                        "sha256": sha,
                        "row_count": len(df),
                        "start_ts": df.index[0].to_pydatetime().isoformat(),
                        "end_ts": df.index[-1].to_pydatetime().isoformat(),
                        "timezone": "UTC",
                        "declared_gaps": [],
                        "source": "synthetic",
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    _patch_processed_dir(monkeypatch, tmp_path)

    prices = load_dataset(dataset_id, manifest_path=manifest_path)
    budget = RiskBudget(
        capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
    )
    cost_model = CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=2.0)
    result = run_backtest(
        prices=prices,
        strategy=DummyAlternatingStrategy(),
        budget=budget,
        cost_model=cost_model,
        dataset_id=dataset_id,
    )

    assert result.bars == len(df)
    assert len(result.equity_curve) == len(df)
    assert result.equity_curve[0][1] == budget.capital_inicial
    assert len(result.fills) > 0, "dummy alternating deve gerar ao menos um fill"
    assert all(f.price > 0 for f in result.fills)
    assert all(f.size > 0 for f in result.fills)

    assert all(f.timestamp > f.signal_timestamp for f in result.fills), (
        "execução deve ocorrer estritamente após o sinal (ADR-0002, t+1 open)"
    )

    assert result.final_equity > 0
    assert result.metrics is not None
    assert result.metrics.trade_count >= 0
    if result.metrics.trade_count > 0:
        assert result.metrics.hit_rate is not None
    else:
        assert result.metrics.hit_rate is None
    assert 0.0 <= result.metrics.max_drawdown <= 1.0


def _patch_processed_dir(monkeypatch, tmp_path: Path) -> None:
    import alpha_forge.data.loaders as loaders_mod

    monkeypatch.setattr(
        loaders_mod, "data_processed_dir", lambda: tmp_path / "data" / "processed"
    )
