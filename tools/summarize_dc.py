"""Resumir Serie DC (alts baseline screening, ADR-0162 Fase A)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_dc_summary.json"

PROBES = []
for asset in ["dot", "avax", "link"]:
    PROBES.append((f"DC.{asset.upper()}.1", f"dc-{asset}-bol-20-15-width-short-1h-2025h1", f"{asset.upper()} bol+width"))
    PROBES.append((f"DC.{asset.upper()}.2", f"dc-{asset}-rsi-30-70-width-short-1h-2025h1", f"{asset.upper()} rsi+width"))
    PROBES.append((f"DC.{asset.upper()}.3", f"dc-{asset}-rsi-30-70-trendhtf-short-1h-2025h1", f"{asset.upper()} rsi+trendhtf"))


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
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, mdd_pct=mdd)


def main():
    rows = []
    for tag, rid, label in PROBES:
        m = metrics(rid)
        rows.append({"tag": tag, "label": label, **m})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<12} {'Label':<22} {'Tr':>3} {'Sh':>7} {'PnL%':>7} {'MDD%':>6}")
    print("-" * 70)
    for r in rows:
        marker = " *" if r['sharpe'] >= 1.5 and r['trades'] >= 40 else ""
        print(f"{r['tag']:<12} {r['label']:<22} {r['trades']:>3} "
              f"{r['sharpe']:>7.3f} {r['pnl_pct']:>7.2f} {r['mdd_pct']:>6.2f}{marker}")
    print("\n* = survivor gate (Sh>=1.5 AND trades>=40)")


if __name__ == "__main__":
    main()
