"""Resumir Série TF10m (BB+width 10m, 9 runs). Pré-reg ADR-0195.

Annualização: sqrt(144 × 365) ≈ 229.25 (144 barras 10min/dia).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_tf10m_summary.json"

PROBES = [
    ("TF10.1", "tf10-btc-bol-width-20-2-short-10m-2024h2", "BTC 2024-H2"),
    ("TF10.2", "tf10-eth-bol-width-20-2-short-10m-2024h2", "ETH 2024-H2"),
    ("TF10.3", "tf10-sol-bol-width-20-2-short-10m-2024h2", "SOL 2024-H2"),
    ("TF10.4", "tf10-btc-bol-width-20-2-short-10m-2025h1", "BTC 2025-H1"),
    ("TF10.5", "tf10-eth-bol-width-20-2-short-10m-2025h1", "ETH 2025-H1"),
    ("TF10.6", "tf10-sol-bol-width-20-2-short-10m-2025h1", "SOL 2025-H1"),
    ("TF10.7", "tf10-btc-bol-width-20-2-short-10m-2025h2", "BTC 2025-H2"),
    ("TF10.8", "tf10-eth-bol-width-20-2-short-10m-2025h2", "ETH 2025-H2"),
    ("TF10.9", "tf10-sol-bol-width-20-2-short-10m-2025h2", "SOL 2025-H2"),
]


def annual_sharpe_10m(rets: list[float]) -> float:
    """10m: sqrt(144*365) annual factor (144 barras 10min/dia)."""
    n = len(rets)
    if n < 2:
        return 0.0
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / n
    sd = math.sqrt(var)
    if sd == 0:
        return 0.0
    return (mean / sd) * math.sqrt(144 * 365)


def metrics(rid: str) -> dict:
    p = RESULTS / rid
    wf = json.loads((p / "walk_forward.json").read_text())
    folds = wf["payload"]
    all_trades: list[dict] = []
    full_eq = [10000.0]
    for f in folds:
        all_trades.extend(f["result"].get("trades", []))
        ec_pairs = f["result"].get("equity_curve", [])
        ec_vals = [pair[1] for pair in ec_pairs]
        if ec_vals:
            base_eq = full_eq[-1]
            first = ec_vals[0] if ec_vals[0] != 0 else 10000.0
            for v in ec_vals:
                full_eq.append(base_eq * v / first)
    n_trades = len(all_trades)
    final_eq = full_eq[-1]
    pnl_pct = (final_eq / 10000.0 - 1) * 100
    rets = [
        (full_eq[i] / full_eq[i - 1] - 1)
        for i in range(1, len(full_eq))
        if full_eq[i - 1] > 0
    ]
    sh = annual_sharpe_10m(rets)
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, final_eq=final_eq)


def main() -> None:
    rows: list[dict] = []
    for tag, rid, label in PROBES:
        try:
            m = metrics(rid)
        except FileNotFoundError:
            print(f"{tag} {label}: MISSING")
            continue
        rows.append({"tag": tag, "label": label, "run_id": rid, **m})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<8} {'Label':<14} {'Tr':>5} {'Sh':>7} {'PnL%':>8}  {'FE':>8}")
    for r in rows:
        print(
            f"{r['tag']:<8} {r['label']:<14} {r['trades']:>5} "
            f"{r['sharpe']:>7.3f} {r['pnl_pct']:>8.2f}  {r['final_eq']:>8.0f}"
        )
    passing = [r for r in rows if r["sharpe"] >= 1.5 and r["trades"] >= 30]
    print(f"\nGate mínimo Sh>=1.5 AND trades>=30: {len(passing)}/{len(rows)}")
    for r in passing:
        print(f"  {r['tag']} {r['label']}: Sh={r['sharpe']:.2f} trades={r['trades']}")


if __name__ == "__main__":
    main()
