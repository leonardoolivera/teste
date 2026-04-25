"""Resumir Serie CW (RSI long + width 300, 9 runs)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cw_summary.json"

PILOTS = [
    ("CW.1", "cw-btc-rsi-long-width300-2024h2", "BTC", "2024-H2"),
    ("CW.2", "cw-eth-rsi-long-width300-2024h2", "ETH", "2024-H2"),
    ("CW.3", "cw-sol-rsi-long-width300-2024h2", "SOL", "2024-H2"),
    ("CW.4", "cw-btc-rsi-long-width300-2025h1", "BTC", "2025-H1"),
    ("CW.5", "cw-eth-rsi-long-width300-2025h1", "ETH", "2025-H1"),
    ("CW.6", "cw-sol-rsi-long-width300-2025h1", "SOL", "2025-H1"),
    ("CW.7", "cw-btc-rsi-long-width300-2025h2", "BTC", "2025-H2"),
    ("CW.8", "cw-eth-rsi-long-width300-2025h2", "ETH", "2025-H2"),
    ("CW.9", "cw-sol-rsi-long-width300-2025h2", "SOL", "2025-H2"),
]

NAKED_SH = {
    ("BTC","2024-H2"):+0.886, ("ETH","2024-H2"):+0.651, ("SOL","2024-H2"):-0.103,
    ("BTC","2025-H1"):+0.829, ("ETH","2025-H1"):-0.535, ("SOL","2025-H1"):+0.074,
    ("BTC","2025-H2"):-2.343, ("ETH","2025-H2"):+0.669, ("SOL","2025-H2"):+0.401,
}


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
    for tag, rid, asset, window in PILOTS:
        m = metrics(rid)
        naked = NAKED_SH[(asset, window)]
        delta = m["sharpe"] - naked
        row = {"tag": tag, "asset": asset, "window": window, "run_id": rid,
               "naked_sh": naked, "delta_vs_naked": delta, **m, "verdict": verdict(m)}
        rows.append(row)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<6} {'Asset':<5} {'Win':<8} {'Tr':>4} {'PnL%':>7} {'Sh':>7} {'Naked':>7} {'Delta':>7} {'MCp5':>6}  Verdict")
    for r in rows:
        mc = r['mc_p5'] if r['mc_p5'] is not None else 0
        print(f"{r['tag']:<6} {r['asset']:<5} {r['window']:<8} {r['trades']:>4} {r['pnl_pct']:>7.2f} "
              f"{r['sharpe']:>7.3f} {r['naked_sh']:>+7.3f} {r['delta_vs_naked']:>+7.3f} {mc:>6.0f}  {r['verdict']}")
    passes = sum(1 for r in rows if r["verdict"] == "PASS")
    print(f"\nPASS count: {passes}/9")


if __name__ == "__main__":
    main()
