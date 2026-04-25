"""Resumir Serie CZ4 (SOL RSI short 4h + trend_htf(1d) cross-window, ADR-0120)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cz4_summary.json"

PROBES = [
    ("CZ4.1", "cz4-sol-rsi-short-trendhtf1d-4h-2024h2", "SOL 4h 2024-H2 bull"),
    ("CZ4.2", "cz4-sol-rsi-short-trendhtf1d-4h-2025h1", "SOL 4h 2025-H1 chop"),
    ("CZ4.3", "cz4-sol-rsi-short-trendhtf1d-4h-2025h2", "SOL 4h 2025-H2 misto"),
]

NAKED_BASE = {
    "CZ4.1": ("CZ2.1 naked", 13, -1.31),
    "CZ4.2": ("CZ2.2 naked", 17, 0.64),
    "CZ4.3": ("CT.3 naked", 23, 2.81),
}


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


def classify(sh, trades):
    if sh >= 1.0 and trades >= 8: return "PASS strict"
    if sh >= 0.3 and trades >= 6: return "PASS contextual"
    if sh < 0: return "FAIL"
    return "ambiguo"


def main():
    rows = []
    for tag, rid, combo in PROBES:
        m = metrics(rid)
        v = classify(m["sharpe"], m["trades"])
        naked = NAKED_BASE.get(tag, ("n/a", 0, 0.0))
        rows.append({"tag": tag, "combo": combo, **m, "verdict": v,
                     "naked_base": naked[0], "naked_trades": naked[1], "naked_sharpe": naked[2]})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<6} {'Combo':<22} {'Tr':>3} {'Sh':>7} {'PnL%':>7} {'MDD%':>6}  | naked: Tr / Sh     Verdict")
    for r in rows:
        print(f"{r['tag']:<6} {r['combo']:<22} "
              f"{r['trades']:>3} {r['sharpe']:>7.3f} {r['pnl_pct']:>7.2f} "
              f"{r['mdd_pct']:>6.2f}  | {r['naked_base']:<13} {r['naked_trades']:>3} / {r['naked_sharpe']:>5.2f}  {r['verdict']}")


if __name__ == "__main__":
    main()
