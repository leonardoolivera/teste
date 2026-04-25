"""Resumir Serie CZE (auditoria Padrao 25 cross-window)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cze_summary.json"

PROBES = [
    ("CZE.1", "cze-v7-eth-rsi-long-width-2025h1",     "v7 ETH long+width",   "2024-H2", 1.774, "2025-H1"),
    ("CZE.2", "cze-v6-sol-rsi-short-trend-2024h2",    "v6 SOL short+trend",  "2025-H1", 1.958, "2024-H2"),
    ("CZE.3", "cze-v4a-btc-rsi-short-width-2024h2",   "v4a BTC short+width", "2025-H1", 1.688, "2024-H2"),
    ("CZE.4", "cze-v3-btc-bollinger-short-width-2024h2", "v3 BTC boll+width","2025-H1", 1.243, "2024-H2"),
    ("CZE.5", "cze-v3-eth-bollinger-short-width-2024h2", "v3 ETH boll+width","2025-H1", 2.395, "2024-H2"),
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


def verdict_ad0107(m):
    sh = m["sharpe"] or 0
    if sh >= 1.0:
        return "PASS (replicado cross-window)"
    elif sh >= 0:
        return f"FAIL marginal (Sh={sh:.2f}) — fragilidade, caso-a-caso"
    else:
        return f"FAIL STRONG (Sh={sh:.2f}) — regime flip, candidato rollback"


def main():
    rows = []
    for tag, rid, combo, baseline_win, baseline_sh, test_win in PROBES:
        m = metrics(rid)
        v = verdict_ad0107(m)
        rows.append({"tag": tag, "combo": combo, "baseline_window": baseline_win,
                     "baseline_sh": baseline_sh, "test_window": test_win, **m, "verdict": v})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<6} {'Combo':<22} {'Base':<8} {'BaseSh':>6} {'Test':<8} {'Tr':>4} {'Sh':>7} {'PnL%':>7} {'MDD%':>6}  Verdict")
    for r in rows:
        print(f"{r['tag']:<6} {r['combo']:<22} {r['baseline_window']:<8} {r['baseline_sh']:>6.2f} "
              f"{r['test_window']:<8} {r['trades']:>4} {r['sharpe']:>7.3f} {r['pnl_pct']:>7.2f} "
              f"{r['mdd_pct']:>6.2f}  {r['verdict']}")

    passes = sum(1 for r in rows if (r['sharpe'] or 0) >= 1.0)
    strongs = sum(1 for r in rows if (r['sharpe'] or 0) < 0)
    margs = len(rows) - passes - strongs
    print(f"\nSumario: {passes}/{len(rows)} PASS, {margs}/{len(rows)} FAIL marginal, {strongs}/{len(rows)} FAIL strong")


if __name__ == "__main__":
    main()
