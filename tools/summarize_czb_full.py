"""Resumir Serie CZB completa (pernas A+B)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_czb_full_summary.json"

PILOTS = [
    # (tag, rid, asset, window, rsi_naked_sh, has_filter)
    ("CZB.1", "czb-dot-bollinger-short-naked-2025h2", "DOT", "2025-H2", 0.498, False),
    ("CZB.2", "czb-avax-bollinger-short-naked-2025h2", "AVAX", "2025-H2", -0.054, False),
    ("CZB.3", "czb-dot-bollinger-short-width300-2025h2", "DOT", "2025-H2", 0.498, True),
    ("CZB.4", "czb-avax-bollinger-short-width300-2025h2", "AVAX", "2025-H2", -0.054, True),
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
    final_eq = full_eq[-1]
    pnl_pct = (final_eq / 10000.0 - 1) * 100
    rets = [(full_eq[i] / full_eq[i-1] - 1) for i in range(1, len(full_eq)) if full_eq[i-1] > 0]
    sh = annual_sharpe(rets)
    peak = full_eq[0]; mdd = 0.0
    for v in full_eq:
        peak = max(peak, v)
        dd = (peak - v) / peak * 100
        mdd = max(mdd, dd)
    mc_path = p / "monte_carlo.json"
    mc_p5 = None
    if mc_path.exists():
        mc = json.loads(mc_path.read_text())["payload"]
        mc_p5 = mc["final_equity_percentiles"].get("5")
    cs_path = p / "cost_stress.json"
    cost_r = None
    if cs_path.exists():
        cs = json.loads(cs_path.read_text())["payload"]
        base_fe = cs["baseline"]["result"]["final_equity"]
        stress_fes = [s["result"]["final_equity"] for s in cs["scenarios"]]
        cost_r = min((sfe / base_fe) for sfe in stress_fes) if stress_fes and base_fe > 0 else 0.0
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, mdd_pct=mdd,
                final_eq=final_eq, cost_r=cost_r, mc_p5=mc_p5)


def verdict(m):
    fails = []
    if m["trades"] < 30: fails.append("trades<30")
    if (m["sharpe"] or 0) < 1.0: fails.append("Sh<1.0")
    if (m["mdd_pct"] or 0) > 20.0: fails.append("MDD>20")
    if m["mc_p5"] is None or m["mc_p5"] < 9500: fails.append("MCp5<9500")
    if m["cost_r"] is None or m["cost_r"] < 0.95: fails.append("costr<0.95")
    if (m["pnl_pct"] or 0) < 3.0: fails.append("PnL<3%")
    return "PASS" if not fails else "FAIL (" + ", ".join(fails) + ")"


def main():
    rows = []
    for tag, rid, asset, window, rsi_naked, has_filter in PILOTS:
        m = metrics(rid)
        row = {"tag": tag, "asset": asset, "window": window, "run_id": rid,
               "config": "filter" if has_filter else "naked",
               "rsi_naked_sh": rsi_naked, **m, "verdict": verdict(m)}
        rows.append(row)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<7} {'Asset':<5} {'Cfg':<7} {'Tr':>4} {'PnL%':>7} {'MDD%':>6} {'Sh':>7} {'MCp5':>6} {'costr':>6}  Verdict")
    for r in rows:
        mc = r['mc_p5'] if r['mc_p5'] is not None else 0
        cr = r['cost_r'] if r['cost_r'] is not None else 0
        print(f"{r['tag']:<7} {r['asset']:<5} {r['config']:<7} {r['trades']:>4} {r['pnl_pct']:>7.2f} "
              f"{r['mdd_pct']:>6.2f} {r['sharpe']:>7.3f} {mc:>6.0f} {cr:>6.4f}  {r['verdict']}")
    passes = sum(1 for r in rows if r["verdict"] == "PASS")
    print(f"\nPASS total: {passes}/4")
    # Gate 2 load-bearing: filter vs naked Bollinger
    print("\nGate 2 delta filter vs naked Bollinger:")
    naked_dot = [r['sharpe'] for r in rows if r['asset']=='DOT' and r['config']=='naked'][0]
    naked_avax = [r['sharpe'] for r in rows if r['asset']=='AVAX' and r['config']=='naked'][0]
    filter_dot = [r['sharpe'] for r in rows if r['asset']=='DOT' and r['config']=='filter'][0]
    filter_avax = [r['sharpe'] for r in rows if r['asset']=='AVAX' and r['config']=='filter'][0]
    print(f"  DOT:  naked={naked_dot:+.3f}  filter={filter_dot:+.3f}  delta={filter_dot-naked_dot:+.3f}")
    print(f"  AVAX: naked={naked_avax:+.3f}  filter={filter_avax:+.3f}  delta={filter_avax-naked_avax:+.3f}")
    # Gate 4 cross-engine CZA
    print("\nGate 4 cross-engine (CZA RSI vs CZB Bollinger):")
    print(f"  DOT RSI naked=0.498  RSI+width=0.901  ||  Bol naked={naked_dot:+.3f}  Bol+width={filter_dot:+.3f}")
    print(f"  AVAX RSI naked=-0.054 RSI+width=0.377 ||  Bol naked={naked_avax:+.3f}  Bol+width={filter_avax:+.3f}")


if __name__ == "__main__":
    main()
