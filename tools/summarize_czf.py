"""Resumir Serie CZF (Padrao 26 regime-matched cross-window)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_czf_summary.json"

PROBES = [
    ("CZF.1", "czf-v7-eth-rsi-long-width-2024h1",     "v7 ETH long+width",   "2024-H2", 1.774),
    ("CZF.2", "czf-v6-sol-rsi-short-trend-2024h1",    "v6 SOL short+trend",  "2025-H1", 1.958),
    ("CZF.3", "czf-v4a-btc-rsi-short-width-2024h1",   "v4a BTC short+width", "2025-H1", 1.688),
    ("CZF.4", "czf-v3-btc-bollinger-short-width-2024h1", "v3 BTC boll+width","2025-H1", 1.243),
    ("CZF.5", "czf-v3-eth-bollinger-short-width-2024h1", "v3 ETH boll+width","2025-H1", 2.395),
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
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, mdd_pct=mdd, final_eq=final_eq)


def main():
    rows = []
    for tag, rid, combo, baseline_win, baseline_sh in PROBES:
        m = metrics(rid)
        sh = m["sharpe"]
        if sh >= 1.0:
            v = "PASS"
        elif sh >= 0.5:
            v = "PASS contextual (0.5-1.0)"
        elif sh >= 0:
            v = "FAIL marginal"
        else:
            v = "FAIL strong"
        rows.append({"tag": tag, "combo": combo, "baseline_window": baseline_win,
                     "baseline_sh": baseline_sh, "test_window": "2024-H1", **m, "verdict": v})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<6} {'Combo':<22} {'BaseSh':>6} {'Tr':>4} {'Sh':>7} {'PnL%':>7} {'MDD%':>6}  Verdict")
    for r in rows:
        print(f"{r['tag']:<6} {r['combo']:<22} {r['baseline_sh']:>6.2f} "
              f"{r['trades']:>4} {r['sharpe']:>7.3f} {r['pnl_pct']:>7.2f} "
              f"{r['mdd_pct']:>6.2f}  {r['verdict']}")

    passes = sum(1 for r in rows if r['sharpe'] >= 1.0)
    ctx = sum(1 for r in rows if 0.5 <= r['sharpe'] < 1.0)
    print(f"\nSumario CZF (regime-matched 2024-H1): {passes}/{len(rows)} PASS strict, {ctx}/{len(rows)} PASS contextual")


if __name__ == "__main__":
    main()
