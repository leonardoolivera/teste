"""Resumir Serie CZ9 (MACX 10/30 long naked, ADR-0130)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cz9_summary.json"

PROBES = [
    ("CZ9.1", "cz9-btc-macx-1030-long-1h-2024h2", "BTC 1h 2024-H2 bull"),
    ("CZ9.2", "cz9-eth-macx-1030-long-1h-2024h2", "ETH 1h 2024-H2 bull"),
    ("CZ9.3", "cz9-sol-macx-1030-long-1h-2024h2", "SOL 1h 2024-H2 bull"),
    ("CZ9.4", "cz9-btc-macx-1030-long-1h-2025h2", "BTC 1h 2025-H2 misto"),
    ("CZ9.5", "cz9-eth-macx-1030-long-1h-2025h2", "ETH 1h 2025-H2 misto"),
    ("CZ9.6", "cz9-sol-macx-1030-long-1h-2025h2", "SOL 1h 2025-H2 misto"),
]

CZ6_BASELINE = {
    "CZ9.1": 2.39, "CZ9.2": 1.88, "CZ9.3": 1.22,
    "CZ9.4": -2.17, "CZ9.5": -1.47, "CZ9.6": -2.44,
}


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
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, mdd_pct=mdd, final_eq=final_eq)


def classify(sh, trades):
    if sh >= 1.0 and trades >= 30: return "PASS strict"
    if sh >= 0.5 and trades >= 20: return "PASS contextual"
    if sh < 0: return "FAIL"
    return "ambiguo"


def main():
    rows = []
    for tag, rid, combo in PROBES:
        m = metrics(rid)
        v = classify(m["sharpe"], m["trades"])
        rows.append({"tag": tag, "combo": combo, **m, "verdict": v,
                     "cz6_2050_sharpe": CZ6_BASELINE[tag]})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<6} {'Combo':<22} {'Tr':>3} {'Sh':>7} {'PnL%':>7} {'MDD%':>6}  | CZ6 20/50  Verdict")
    for r in rows:
        print(f"{r['tag']:<6} {r['combo']:<22} "
              f"{r['trades']:>3} {r['sharpe']:>7.3f} {r['pnl_pct']:>7.2f} "
              f"{r['mdd_pct']:>6.2f}  | {r['cz6_2050_sharpe']:>5.2f}     {r['verdict']}")


if __name__ == "__main__":
    main()
