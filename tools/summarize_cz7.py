"""Resumir Serie CZ7 (MACX 20/50 + trend_htf, ADR-0126)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cz7_summary.json"

PROBES = [
    ("CZ7.1", "cz7-btc-macx-2050-trendhtf-1h-2024h2", "BTC 1h 2024-H2 bull"),
    ("CZ7.2", "cz7-eth-macx-2050-trendhtf-1h-2024h2", "ETH 1h 2024-H2 bull"),
    ("CZ7.3", "cz7-sol-macx-2050-trendhtf-1h-2024h2", "SOL 1h 2024-H2 bull"),
    ("CZ7.4", "cz7-btc-macx-2050-trendhtf-1h-2025h2", "BTC 1h 2025-H2 misto"),
    ("CZ7.5", "cz7-eth-macx-2050-trendhtf-1h-2025h2", "ETH 1h 2025-H2 misto"),
    ("CZ7.6", "cz7-sol-macx-2050-trendhtf-1h-2025h2", "SOL 1h 2025-H2 misto"),
]

NAKED = {
    "CZ7.1": (36, 2.39), "CZ7.2": (34, 1.88), "CZ7.3": (32, 1.22),
    "CZ7.4": (29, -2.17), "CZ7.5": (34, -1.47), "CZ7.6": (36, -2.44),
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
    if sh >= 1.0 and trades >= 20: return "PASS strict"
    if sh >= 0.5 and trades >= 12: return "PASS contextual"
    if sh < 0: return "FAIL"
    return "ambiguo"


def main():
    rows = []
    for tag, rid, combo in PROBES:
        m = metrics(rid)
        v = classify(m["sharpe"], m["trades"])
        nk_t, nk_sh = NAKED[tag]
        rows.append({"tag": tag, "combo": combo, **m, "verdict": v,
                     "naked_trades": nk_t, "naked_sharpe": nk_sh})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<6} {'Combo':<22} {'Tr':>3} {'Sh':>7} {'PnL%':>7} {'MDD%':>6}  | naked Tr/Sh   Verdict")
    for r in rows:
        print(f"{r['tag']:<6} {r['combo']:<22} "
              f"{r['trades']:>3} {r['sharpe']:>7.3f} {r['pnl_pct']:>7.2f} "
              f"{r['mdd_pct']:>6.2f}  | {r['naked_trades']:>3}/{r['naked_sharpe']:>5.2f}  {r['verdict']}")


if __name__ == "__main__":
    main()
