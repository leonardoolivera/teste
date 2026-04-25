"""Resumir Serie DD (AVAX cross-window 2025-H2, ADR-0164)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_dd_summary.json"

PROBES = [
    ("DD.1", "dd-avax-rsi-30-70-width-short-1h-2025h2", "AVAX rsi+width 2025H2", 1.64),
    ("DD.2", "dd-avax-rsi-30-70-trendhtf-short-1h-2025h2", "AVAX rsi+trendhtf 2025H2", 1.77),
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
    for tag, rid, label, h1_sh in PROBES:
        m = metrics(rid)
        passes = m["sharpe"] >= 0.8 and m["trades"] >= 40
        rows.append({"tag": tag, "label": label, "h1_sharpe": h1_sh, "pass_gate": passes, **m})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<7} {'Label':<28} {'Tr':>3} {'H1Sh':>6} {'H2Sh':>7} {'PnL%':>7} {'Gate':>6}")
    print("-" * 70)
    for r in rows:
        mark = " PASS" if r['pass_gate'] else " FAIL"
        print(f"{r['tag']:<7} {r['label']:<28} {r['trades']:>3} "
              f"{r['h1_sharpe']:>6.2f} {r['sharpe']:>7.3f} {r['pnl_pct']:>7.2f}{mark}")


if __name__ == "__main__":
    main()
