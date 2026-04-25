"""Resumir Serie TF Fase 2 cross-window 15m (ADR-0177)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_tf_crosswindow_summary.json"

PROBES = [
    ("TF.4", "tf-btc-bol-width-20-2-short-15m-2025h1", "BTC 2025-H1"),
    ("TF.5", "tf-eth-bol-width-20-2-short-15m-2025h1", "ETH 2025-H1"),
    ("TF.6", "tf-sol-bol-width-20-2-short-15m-2025h1", "SOL 2025-H1"),
    ("TF.7", "tf-btc-bol-width-20-2-short-15m-2025h2", "BTC 2025-H2"),
    ("TF.8", "tf-eth-bol-width-20-2-short-15m-2025h2", "ETH 2025-H2"),
    ("TF.9", "tf-sol-bol-width-20-2-short-15m-2025h2", "SOL 2025-H2"),
]


def annual_sharpe_15m(rets):
    n = len(rets)
    if n < 2: return 0.0
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / n
    sd = math.sqrt(var)
    if sd == 0: return 0.0
    return (mean / sd) * math.sqrt(96 * 365)


def metrics(rid):
    p = RESULTS / rid
    wf = json.loads((p / "walk_forward.json").read_text())
    folds = wf["payload"]
    all_trades = []
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
    rets = [(full_eq[i] / full_eq[i-1] - 1) for i in range(1, len(full_eq)) if full_eq[i-1] > 0]
    sh = annual_sharpe_15m(rets)
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh)


def main():
    rows = []
    for tag, rid, label in PROBES:
        try:
            m = metrics(rid)
        except FileNotFoundError:
            print(f"{tag} {label}: MISSING")
            continue
        rows.append({"tag": tag, "label": label, **m})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<7} {'Label':<14} {'Tr':>4} {'Sh':>7} {'PnL%':>8}")
    for r in rows:
        print(f"{r['tag']:<7} {r['label']:<14} {r['trades']:>4} "
              f"{r['sharpe']:>7.3f} {r['pnl_pct']:>8.2f}")
    passing = [r for r in rows if r['sharpe'] >= 1.5 and r['trades'] >= 30]
    print(f"\nPass Sh>=1.5 AND trades>=30: {len(passing)}/{len(rows)}")
    for r in passing:
        print(f"  {r['tag']} {r['label']}: Sh={r['sharpe']:.2f}")


if __name__ == "__main__":
    main()
