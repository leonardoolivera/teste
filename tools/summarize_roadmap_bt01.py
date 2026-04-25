"""Resumir Batch BT01 — BTC cross-era sweet-spot MA+ST 10m."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "roadmap_bt01_summary.json"


ENTRIES = [
    ("BT01.01", "t1ma-25-75-btc-2024h2-long-10m", "BTC 2024-H2", "MA 25/75"),
    ("BT01.02", "t1ma-25-75-btc-2025h1-long-10m", "BTC 2025-H1", "MA 25/75"),
    ("BT01.03", "t1ma-25-75-btc-2025h2-long-10m", "BTC 2025-H2", "MA 25/75"),
    ("BT01.04", "t1st-10-4-btc-2024h2-bi-10m", "BTC 2024-H2", "ST 10/4.0 bi"),
    ("BT01.05", "t1st-10-4-btc-2025h1-bi-10m", "BTC 2025-H1", "ST 10/4.0 bi"),
    ("BT01.06", "t1st-10-4-btc-2025h2-bi-10m", "BTC 2025-H2", "ST 10/4.0 bi"),
    ("BT01.07", "t1st-14-3-btc-2024h2-bi-10m", "BTC 2024-H2", "ST 14/3.0 bi"),
    ("BT01.08", "t1st-14-3-btc-2025h1-bi-10m", "BTC 2025-H1", "ST 14/3.0 bi"),
    ("BT01.09", "t1st-14-3-btc-2025h2-bi-10m", "BTC 2025-H2", "ST 14/3.0 bi"),
    ("BT01.10", "t1ma-30-90-btc-2025h1-long-10m", "BTC 2025-H1", "MA 30/90"),
]


BH_APPROX = {
    "BTC 2024-H2": 70.0, "ETH 2024-H2": 0.0, "SOL 2024-H2": 46.0,
    "BTC 2025-H1": -8.0, "ETH 2025-H1": -47.0, "SOL 2025-H1": -40.0,
    "BTC 2025-H2": 12.0, "ETH 2025-H2": 70.0, "SOL 2025-H2": 35.0,
}


def annual_sharpe_10m(rets):
    n = len(rets)
    if n < 2:
        return 0.0
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / n
    sd = math.sqrt(var)
    if sd == 0:
        return 0.0
    return (mean / sd) * math.sqrt(144 * 365)


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
    return dict(trades=len(all_trades), pnl_pct=pnl_pct, sharpe=annual_sharpe_10m(rets), final_eq=final_eq)


def main():
    out_all = []
    print(f"\n{'=' * 90}\nBatch BT01 — BTC cross-era sweet-spot MA+ST 10m\n{'=' * 90}")
    print(f"{'Tag':<9} {'Params':<14} {'Label':<14} {'Tr':>5} {'Sh':>7} {'PnL%':>8}  {'B&H%':>6}  {'alfa':>7}  Gates")
    for tag, rid, label, params in ENTRIES:
        try:
            m = metrics(rid)
        except FileNotFoundError:
            print(f"{tag:<9} {params:<14} {label:<14}  MISSING ({rid})")
            continue
        bh = BH_APPROX.get(label, float("nan"))
        alpha = m["pnl_pct"] - bh / 2.0 if not math.isnan(bh) else float("nan")
        gate_sh = m["sharpe"] >= 1.5 and m["trades"] >= 30
        gate_alfa = not math.isnan(alpha) and alpha > 0
        gates = ("Sh+" if gate_sh else "Sh-") + " " + ("A+" if gate_alfa else "A-")
        out_all.append({"tag": tag, "rid": rid, "label": label, "params": params, "bh_pct": bh, "alpha": alpha, "gate_sh": gate_sh, "gate_alfa": gate_alfa, **m})
        print(
            f"{tag:<9} {params:<14} {label:<14} {m['trades']:>5} "
            f"{m['sharpe']:>7.3f} {m['pnl_pct']:>8.2f}  {bh:>6.1f}  {alpha:>7.2f}  {gates}"
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_all, indent=2))

    total_sh = [r for r in out_all if r["gate_sh"]]
    total_alfa = [r for r in out_all if r["gate_alfa"]]
    both = [r for r in out_all if r["gate_sh"] and r["gate_alfa"]]
    print(f"\n{'=' * 90}\nAGREGADO BT01\n{'=' * 90}")
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
    print("\n  alfa-only (sem Sh):")
    for r in total_alfa:
        if not r["gate_sh"]:
            print(f"    {r['tag']} {r['params']} {r['label']}: Sh={r['sharpe']:.2f} PnL={r['pnl_pct']:.2f}% alfa={r['alpha']:+.2f}")


if __name__ == "__main__":
    main()
