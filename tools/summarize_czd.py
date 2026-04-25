"""Resumir Serie CZD (LINK cross-window replicacao)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_czd_summary.json"

PROBES = [
    ("CZ.3",  "cz-link-rsi-short-naked-2025h2",   "2025-H2 (baseline v8)"),
    ("CZD.1", "czd-link-rsi-short-2025h1",        "2025-H1"),
    ("CZD.2", "czd-link-rsi-short-2024h2",        "2024-H2"),
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
    mc_median = None
    if mc_path.exists():
        mc = json.loads(mc_path.read_text())["payload"]
        mc_p5 = mc["final_equity_percentiles"].get("5")
        mc_median = mc["final_equity_percentiles"].get("50")
    cs_path = p / "cost_stress.json"
    cost_r = None
    if cs_path.exists():
        cs = json.loads(cs_path.read_text())["payload"]
        base_fe = cs["baseline"]["result"]["final_equity"]
        stress_fes = [s["result"]["final_equity"] for s in cs["scenarios"]]
        cost_r = min((sfe / base_fe) for sfe in stress_fes) if stress_fes and base_fe > 0 else 0.0
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, mdd_pct=mdd,
                final_eq=final_eq, cost_r=cost_r, mc_p5=mc_p5, mc_median=mc_median)


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
    for tag, rid, win in PROBES:
        m = metrics(rid)
        rows.append({"tag": tag, "run_id": rid, "window": win, **m, "verdict": verdict(m)})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<6} {'Window':<22} {'Tr':>4} {'PnL%':>7} {'MDD%':>6} {'Sh':>7} {'MCp5':>6} {'MCmed':>6} {'costr':>6}  Verdict")
    for r in rows:
        mc = r['mc_p5'] if r['mc_p5'] is not None else 0
        md = r['mc_median'] if r['mc_median'] is not None else 0
        cr = r['cost_r'] if r['cost_r'] is not None else 0
        print(f"{r['tag']:<6} {r['window']:<22} {r['trades']:>4} {r['pnl_pct']:>7.2f} "
              f"{r['mdd_pct']:>6.2f} {r['sharpe']:>7.3f} {mc:>6.0f} {md:>6.0f} {cr:>6.4f}  {r['verdict']}")

    # Gate: replicacao 2+ windows (Sh >= 1.0)
    link_rows = rows
    passes = sum(1 for r in link_rows if r['sharpe'] >= 1.0)
    print(f"\nReplicacao cross-window: Sh >= 1.0 em {passes}/{len(link_rows)} janelas")
    for r in link_rows:
        tag = "OK" if r['sharpe'] >= 1.0 else "FAIL"
        print(f"  {r['window']}: Sh={r['sharpe']:.3f} {tag}")


if __name__ == "__main__":
    main()
