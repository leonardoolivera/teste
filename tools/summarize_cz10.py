"""Resumir Serie CZ10 (RSI bounds sensibilidade, ADR-0134)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cz10_summary.json"

PROBES = [
    ("CZ10.1", "cz10-sol-rsi-2575-naked-1h-2025h2", "SOL 2025-H2 short naked", "25/75", 2.30),
    ("CZ10.2", "cz10-sol-rsi-3565-naked-1h-2025h2", "SOL 2025-H2 short naked", "35/65", 2.30),
    ("CZ10.3", "cz10-btc-rsi-2575-width-1h-2025h1", "BTC 2025-H1 short width", "25/75", 1.69),
    ("CZ10.4", "cz10-btc-rsi-3565-width-1h-2025h1", "BTC 2025-H1 short width", "35/65", 1.69),
    ("CZ10.5", "cz10-sol-rsi-2575-trendhtf-1h-2025h1", "SOL 2025-H1 short trendhtf", "25/75", 0.89),
    ("CZ10.6", "cz10-sol-rsi-3565-trendhtf-1h-2025h1", "SOL 2025-H1 short trendhtf", "35/65", 0.89),
]


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


def verdict(sh, baseline_sh, trades):
    delta = sh - baseline_sh
    if delta >= 0.3 and trades >= 25: return f"UPGRADE (+{delta:.2f})"
    if delta >= 0.1: return f"observa (+{delta:.2f}, tr={trades})"
    if delta <= -0.3: return f"WORSE ({delta:+.2f})"
    return f"neutro ({delta:+.2f})"


def main():
    rows = []
    for tag, rid, combo, bounds, baseline in PROBES:
        m = metrics(rid)
        v = verdict(m["sharpe"], baseline, m["trades"])
        rows.append({"tag": tag, "combo": combo, "bounds": bounds, "baseline_3070": baseline, **m, "verdict": v})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<7} {'Combo':<28} {'Bnd':<6} {'Tr':>3} {'Sh':>7} {'PnL%':>7}  | base 30/70  Verdict")
    for r in rows:
        print(f"{r['tag']:<7} {r['combo']:<28} {r['bounds']:<6} "
              f"{r['trades']:>3} {r['sharpe']:>7.3f} {r['pnl_pct']:>7.2f}  "
              f"| {r['baseline_3070']:>5.2f}      {r['verdict']}")


if __name__ == "__main__":
    main()
