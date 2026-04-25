"""Gate 4 audit Serie CO — load-bearing test composto."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"

AUDIT = [
    ("CO.2 composto", "co-rsi-width300-trendhtf-sol-20250105_20250704-short"),
    ("CO.2 noWidth (trend-only)", "co-audit-noWidth-sol-20250105_20250704-short"),
    ("CO.2 noTrend (width-only)", "co-audit-noTrend-sol-20250105_20250704-short"),
    ("CO.3 composto", "co-rsi-width300-trendhtf-sol-20250705_20251231-short-v2"),
    ("CO.3 noWidth (trend-only)", "co-audit-noWidth-sol-20250705_20251231-short"),
    ("CO.3 noTrend (width-only)", "co-audit-noTrend-sol-20250705_20251231-short"),
]


def annual_sharpe(rets):
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
    rets = [(full_eq[i] / full_eq[i-1] - 1) for i in range(1, len(full_eq)) if full_eq[i-1] > 0]
    sh = annual_sharpe(rets)
    peak = full_eq[0]; mdd = 0.0
    for v in full_eq:
        peak = max(peak, v)
        dd = (peak - v) / peak * 100
        mdd = max(mdd, dd)
    mc = json.loads((p / "monte_carlo.json").read_text())["payload"]
    mc_p5 = mc["final_equity_percentiles"].get("5")
    cs = json.loads((p / "cost_stress.json").read_text())["payload"]
    base_fe = cs["baseline"]["result"]["final_equity"]
    stress_fes = [s["result"]["final_equity"] for s in cs["scenarios"]]
    cost_r = min((sfe / base_fe) for sfe in stress_fes) if stress_fes and base_fe > 0 else 0.0
    return dict(trades=n_trades, sharpe=sh, mdd_pct=mdd, mc_p5=mc_p5, cost_r=cost_r)


def is_pass(m):
    return (m["trades"] >= 30 and m["sharpe"] >= 1.0 and m["mdd_pct"] <= 20
            and m["mc_p5"] >= 9500 and m["cost_r"] >= 0.95)


print(f"{'Variant':<40} {'Tr':>4} {'Sh':>7} {'MDD%':>6} {'MCp5':>6} {'costr':>6}  Verdict")
for tag, rid in AUDIT:
    m = metrics(rid)
    v = "PASS" if is_pass(m) else "FAIL"
    print(f"{tag:<40} {m['trades']:>4} {m['sharpe']:>7.3f} {m['mdd_pct']:>6.2f} {m['mc_p5']:>6.0f} {m['cost_r']:>6.4f}  {v}")
