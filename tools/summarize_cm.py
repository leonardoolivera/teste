"""Resumir Serie CM (3 pilotos cross-timeframe 4h 2024-H2)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cm_summary.json"

PILOTS = [
    ("CM.1", "cm-rsi-pure-btc-20240705_20241231-4h-short", "BTC", "2024-H2-4h"),
    ("CM.2", "cm-rsi-pure-eth-20240705_20241231-4h-short", "ETH", "2024-H2-4h"),
    ("CM.3", "cm-rsi-pure-sol-20240705_20241231-4h-short", "SOL", "2024-H2-4h"),
]


def annual_sharpe_4h(rets):
    n = len(rets)
    if n < 2: return 0.0
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / n
    sd = math.sqrt(var)
    if sd == 0: return 0.0
    # 4h timeframe: 6 bars/day * 365
    return (mean / sd) * math.sqrt(6 * 365)


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
    mc = json.loads((p / "monte_carlo.json").read_text())["payload"]
    mc_p5 = mc["final_equity_percentiles"].get("5")
    cs = json.loads((p / "cost_stress.json").read_text())["payload"]
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
    return "PASS" if not fails else "FAIL (" + ", ".join(fails) + ")"


def main():
    rows = []
    for tag, rid, asset, window in PILOTS:
        m = metrics(rid)
        row = {"tag": tag, "asset": asset, "window": window, "run_id": rid, **m, "verdict": verdict(m)}
        rows.append(row)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<6} {'Asset':<4} {'Window':<14} {'Tr':>4} {'PnL%':>8} {'MDD%':>6} {'Sh':>7} {'MCp5':>6} {'costr':>6}  Verdict")
    for r in rows:
        mc = r['mc_p5'] if r['mc_p5'] is not None else 0
        cr = r['cost_r'] if r['cost_r'] is not None else 0
        print(f"{r['tag']:<6} {r['asset']:<4} {r['window']:<14} {r['trades']:>4} {r['pnl_pct']:>8.2f} "
              f"{r['mdd_pct']:>6.2f} {r['sharpe']:>7.3f} {mc:>6.0f} {cr:>6.4f}  {r['verdict']}")
    passes = sum(1 for r in rows if r["verdict"] == "PASS")
    print(f"\nPASS count: {passes}/3")


if __name__ == "__main__":
    main()
