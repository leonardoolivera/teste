"""Serie CA — Donchian SOL 1h cross-period confirmation.

10 pilotos: 5 recortes SOL 1h x 2 variantes min_atr_bps (100 original, 80 perturbacao).
Gate pre-registrado em ADR-0039. Nao mover regua post-hoc.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


RECORTES = [
    ("CA-H1", "solusdt_1h_20230705_20231231_binance_spot", "20230705_20231231"),
    ("CA-H2", "solusdt_1h_20240105_20240704_binance_spot", "20240105_20240704"),
    ("CA-H3", "solusdt_1h_20240705_20241231_binance_spot", "20240705_20241231"),
    ("CA-H4", "solusdt_1h_20250105_20250704_binance_spot", "20250105_20250704"),
    ("CA-H5", "solusdt_1h_20250705_20251231_binance_spot", "20250705_20251231"),
]

ATR_BPS_VARIANTS = [100, 80]


def run_one(tag: str, dataset_id: str, run_id: str, atr_bps: int) -> None:
    print(f"\n{'=' * 70}\n{tag}: {run_id}\n{'=' * 70}")
    sys.argv = [
        "alpha-forge", "validate",
        "--run-id", run_id,
        "--dataset-id", dataset_id,
        "--capital", "10000.0",
        "--fracao", "0.1",
        "--alavancagem", "2.0",
        "--taker-fee-bps", "5.0",
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--strategy", "donchian",
        "--long-only",
        "--entry-window", "20",
        "--exit-window", "10",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", f"atr_regime:window=14:min_atr_bps={atr_bps}",
        "--log-level", "silent",
    ]
    cli_main()


if __name__ == "__main__":
    idx = 1
    for atr_bps in ATR_BPS_VARIANTS:
        for _, ds, suffix in RECORTES:
            tag = f"CA.{idx}"
            run_id = f"ca-donchian-20-10-sol-{suffix}-atrbps{atr_bps}"
            run_one(tag, ds, run_id, atr_bps)
            idx += 1
    print("\nSerie CA rerun completo (10 pilotos).")
