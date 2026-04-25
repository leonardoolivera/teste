"""Resumir Serie CT (RSI short 4h cross-timeframe, ADR-0114)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_ct_summary.json"

PROBES = [
    ("CT.1", "ct-v4a-btc-rsi-short-width-4h-2025h1", "v4a BTC short+width 4h", 1.688),
    ("CT.2", "ct-v81-btc-rsi-short-naked-4h-2025h2", "v8.1 BTC short naked 4h", 1.640),
    ("CT.3", "ct-v81-sol-rsi-short-naked-4h-2025h2", "v8.1 SOL short naked 4h", 2.300),
]


def annual_sharpe_4h(rets):
    n = len(rets)
    if n < 2: return 0.0
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / n
    sd = math.sqrt(var)
    if sd == 0: return 0.0
    # 4h bars: 6 per day * 365 = 2190
    return (mean / sd) * math.sqrt(2190)


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
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, mdd_pct=mdd, final_eq=final_eq)


def classify(sh, trades, pnl):
    if sh >= 1.0 and trades >= 15 and pnl > 0: return "replicacao forte"
    if sh >= 0.5 and trades >= 10 and pnl > 0: return "replicacao fraca"
    if sh < 0 or trades < 5: return "refutacao"
    return "ambiguo"


def main():
    rows = []
    for tag, rid, combo, base_sh in PROBES:
        m = metrics(rid)
        v = classify(m["sharpe"], m["trades"], m["pnl_pct"])
        rows.append({"tag": tag, "combo": combo, "baseline_1h_sh": base_sh, **m, "verdict": v})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<5} {'Combo':<26} {'Base1h':>6} {'Tr':>3} {'Sh':>7} {'PnL%':>7} {'MDD%':>6}  Verdict")
    for r in rows:
        print(f"{r['tag']:<5} {r['combo']:<26} {r['baseline_1h_sh']:>6.2f} "
              f"{r['trades']:>3} {r['sharpe']:>7.3f} {r['pnl_pct']:>7.2f} "
              f"{r['mdd_pct']:>6.2f}  {r['verdict']}")


if __name__ == "__main__":
    main()
