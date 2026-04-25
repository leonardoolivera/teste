"""Resumir Serie CZ19 (width filter internal num_std, ADR-0154)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cz19_summary.json"

PROBES = [
    ("CZ19.1", "cz19-sol-bb-w20-ns1.5-short-filter-ns1.0-1h-2025h1", "SOL short filter ns=1.0", 2.71),
    ("CZ19.2", "cz19-sol-bb-w20-ns1.5-short-filter-ns2.0-1h-2025h1", "SOL short filter ns=2.0", 2.71),
    ("CZ19.3", "cz19-eth-bb-w20-ns1.5-short-filter-ns1.0-1h-2025h1", "ETH short filter ns=1.0", 2.40),
    ("CZ19.4", "cz19-eth-bb-w20-ns1.5-short-filter-ns2.0-1h-2025h1", "ETH short filter ns=2.0", 2.40),
    ("CZ19.5", "cz19-sol-bb-w30-ns1.5-long-filter-ns1.0-1h-2024h2", "SOL long filter ns=1.0", 2.40),
    ("CZ19.6", "cz19-sol-bb-w30-ns1.5-long-filter-ns2.0-1h-2024h2", "SOL long filter ns=2.0", 2.40),
]


def annual_sharpe_1h(rets):
    n = len(rets)
    if n < 2: return 0.0
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / n
    sd = math.sqrt(var)
    if sd == 0: return 0.0
    return (mean / sd) * math.sqrt(24 * 365)


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
    sh = annual_sharpe_1h(rets)
    peak = full_eq[0]; mdd = 0.0
    for v in full_eq:
        peak = max(peak, v)
        dd = (peak - v) / peak * 100
        mdd = max(mdd, dd)
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, mdd_pct=mdd)


def main():
    rows = []
    for tag, rid, label, baseline in PROBES:
        m = metrics(rid)
        lift = m["sharpe"] - baseline
        rows.append({"tag": tag, "label": label, "baseline_sh": baseline, "lift": lift, **m})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<7} {'Label':<28} {'Tr':>3} {'Sh':>7} {'vs base':>8} {'PnL%':>7}")
    for r in rows:
        print(f"{r['tag']:<7} {r['label']:<28} {r['trades']:>3} "
              f"{r['sharpe']:>7.3f} {r['lift']:>+8.2f} {r['pnl_pct']:>7.2f}")


if __name__ == "__main__":
    main()
