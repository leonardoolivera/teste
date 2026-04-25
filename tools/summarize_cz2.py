"""Resumir Serie CZ2 (SOL RSI short 4h cross-window, ADR-0118)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cz2_summary.json"

PROBES = [
    ("CZ2.1", "cz2-sol-rsi-short-naked-4h-2024h2", "SOL 4h 2024-H2 bull"),
    ("CZ2.2", "cz2-sol-rsi-short-naked-4h-2025h1", "SOL 4h 2025-H1 chop"),
]


def annual_sharpe_4h(rets):
    n = len(rets)
    if n < 2: return 0.0
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / n
    sd = math.sqrt(var)
    if sd == 0: return 0.0
    return (mean / sd) * math.sqrt(2190)


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
    sh = annual_sharpe_4h(rets)
    peak = full_eq[0]; mdd = 0.0
    for v in full_eq:
        peak = max(peak, v)
        dd = (peak - v) / peak * 100
        mdd = max(mdd, dd)
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, mdd_pct=mdd, final_eq=final_eq)


def classify(sh, trades, pnl):
    if sh >= 1.0 and trades >= 15: return "PASS strict"
    if sh >= 0.5 and trades >= 10: return "PASS contextual"
    if sh < 0: return "FAIL"
    return "ambiguo"


def main():
    rows = []
    for tag, rid, combo in PROBES:
        m = metrics(rid)
        v = classify(m["sharpe"], m["trades"], m["pnl_pct"])
        rows.append({"tag": tag, "combo": combo, **m, "verdict": v})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"Baseline CT.3 (2025-H2): 23 trades, Sh=2.81, PnL=+16.31%")
    print(f"{'Tag':<6} {'Combo':<24} {'Tr':>3} {'Sh':>7} {'PnL%':>7} {'MDD%':>6}  Verdict")
    for r in rows:
        print(f"{r['tag']:<6} {r['combo']:<24} "
              f"{r['trades']:>3} {r['sharpe']:>7.3f} {r['pnl_pct']:>7.2f} "
              f"{r['mdd_pct']:>6.2f}  {r['verdict']}")


if __name__ == "__main__":
    main()
