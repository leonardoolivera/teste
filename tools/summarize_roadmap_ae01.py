"""Resumir Batch AE01 — asset expansion 1h DOT/LINK/AVAX."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
DATA = ROOT / "data" / "processed"
OUT = ROOT / "exports" / "diag" / "roadmap_ae01_summary.json"


ENTRIES = [
    ("AE01.01", "t3bb-20-2-dot-2025h1-bi-1h",   "DOT 2025-H1",  "BB 20/2.0",   "DOTUSDT", "20250105_20250704"),
    ("AE01.02", "t3bb-20-2-dot-2025h2-bi-1h",   "DOT 2025-H2",  "BB 20/2.0",   "DOTUSDT", "20250705_20251231"),
    ("AE01.03", "t3bb-20-2-link-2025h1-bi-1h",  "LINK 2025-H1", "BB 20/2.0",   "LINKUSDT","20250105_20250704"),
    ("AE01.04", "t3bb-20-2-link-2025h2-bi-1h",  "LINK 2025-H2", "BB 20/2.0",   "LINKUSDT","20250705_20251231"),
    ("AE01.05", "t3bb-20-2-avax-2025h1-bi-1h",  "AVAX 2025-H1", "BB 20/2.0",   "AVAXUSDT","20250105_20250704"),
    ("AE01.06", "t3bb-20-2-avax-2025h2-bi-1h",  "AVAX 2025-H2", "BB 20/2.0",   "AVAXUSDT","20250705_20251231"),
    ("AE01.07", "t3ma-20-50-dot-2025h1-long-1h","DOT 2025-H1",  "MA 20/50",    "DOTUSDT", "20250105_20250704"),
    ("AE01.08", "t3ma-20-50-link-2025h1-long-1h","LINK 2025-H1","MA 20/50",    "LINKUSDT","20250105_20250704"),
    ("AE01.09", "t3ma-20-50-avax-2025h1-long-1h","AVAX 2025-H1","MA 20/50",    "AVAXUSDT","20250105_20250704"),
    ("AE01.10", "t3st-10-3-avax-2025h1-bi-1h",  "AVAX 2025-H1", "ST 10/3.0",   "AVAXUSDT","20250105_20250704"),
]


def bh_pct(asset: str, period: str) -> float:
    sym = asset.lower()
    path = DATA / asset / "1h" / f"{sym}_1h_{period}_binance_spot.parquet"
    df = pd.read_parquet(path)
    close_col = "close" if "close" in df.columns else [c for c in df.columns if c.lower() == "close"][0]
    first = float(df[close_col].iloc[0])
    last = float(df[close_col].iloc[-1])
    return (last / first - 1) * 100


def annual_sharpe_1h(rets):
    n = len(rets)
    if n < 2:
        return 0.0
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / n
    sd = math.sqrt(var)
    if sd == 0:
        return 0.0
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
    final_eq = full_eq[-1]
    pnl_pct = (final_eq / 10000.0 - 1) * 100
    rets = [
        (full_eq[i] / full_eq[i - 1] - 1)
        for i in range(1, len(full_eq))
        if full_eq[i - 1] > 0
    ]
    return dict(trades=len(all_trades), pnl_pct=pnl_pct, sharpe=annual_sharpe_1h(rets), final_eq=final_eq)


def main():
    out_all = []
    bh_cache = {}
    print(f"\n{'=' * 90}\nBatch AE01 — asset expansion 1h DOT/LINK/AVAX\n{'=' * 90}")
    print(f"{'Tag':<9} {'Params':<12} {'Label':<14} {'Tr':>5} {'Sh':>7} {'PnL%':>8}  {'B&H%':>7}  {'alfa':>7}  Gates")
    for tag, rid, label, params, asset, period in ENTRIES:
        try:
            m = metrics(rid)
        except FileNotFoundError:
            print(f"{tag:<9} {params:<12} {label:<14}  MISSING ({rid})")
            continue
        key = (asset, period)
        if key not in bh_cache:
            try:
                bh_cache[key] = bh_pct(asset, period)
            except Exception as e:
                bh_cache[key] = float("nan")
        bh = bh_cache[key]
        alpha = m["pnl_pct"] - bh / 2.0 if not math.isnan(bh) else float("nan")
        gate_sh = m["sharpe"] >= 1.5 and m["trades"] >= 30
        gate_alfa = not math.isnan(alpha) and alpha > 0
        gates = ("Sh+" if gate_sh else "Sh-") + " " + ("A+" if gate_alfa else "A-")
        out_all.append({"tag": tag, "rid": rid, "label": label, "params": params, "bh_pct": bh, "alpha": alpha, "gate_sh": gate_sh, "gate_alfa": gate_alfa, **m})
        print(
            f"{tag:<9} {params:<12} {label:<14} {m['trades']:>5} "
            f"{m['sharpe']:>7.3f} {m['pnl_pct']:>8.2f}  {bh:>7.1f}  {alpha:>7.2f}  {gates}"
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_all, indent=2))

    total_sh = [r for r in out_all if r["gate_sh"]]
    total_alfa = [r for r in out_all if r["gate_alfa"]]
    both = [r for r in out_all if r["gate_sh"] and r["gate_alfa"]]
    print(f"\n{'=' * 90}\nAGREGADO AE01\n{'=' * 90}")
    print(f"Total: {len(out_all)}/10  |  Sh: {len(total_sh)}/10  |  alfa: {len(total_alfa)}/10  |  ambos: {len(both)}/10")
    if both:
        print("\n  Ambos os gates:")
        for r in both:
            print(f"    {r['tag']} {r['params']} {r['label']}: Sh={r['sharpe']:.2f} PnL={r['pnl_pct']:.2f}% alfa={r['alpha']:+.2f}")
    if total_sh:
        print("\n  Sh pass:")
        for r in total_sh:
            marker = "+alfa" if r["gate_alfa"] else "-alfa"
            print(f"    {r['tag']} {r['params']} {r['label']}: Sh={r['sharpe']:.2f} PnL={r['pnl_pct']:.2f}% alfa={r['alpha']:+.2f} {marker}")
    if total_alfa:
        print("\n  alfa-only (sem Sh):")
        for r in total_alfa:
            if not r["gate_sh"]:
                print(f"    {r['tag']} {r['params']} {r['label']}: Sh={r['sharpe']:.2f} PnL={r['pnl_pct']:.2f}% alfa={r['alpha']:+.2f}")


if __name__ == "__main__":
    main()
