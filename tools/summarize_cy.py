"""Resumir Serie CY (Donchian breakout exploration, ADR-0116)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cy_summary.json"

PROBES = [
    ("CY.1", "cy-donchian-btc-2024h2", "BTC 2024-H2 bull"),
    ("CY.2", "cy-donchian-eth-2024h2", "ETH 2024-H2 bull"),
    ("CY.3", "cy-donchian-sol-2024h2", "SOL 2024-H2 bull"),
    ("CY.4", "cy-donchian-btc-2025h2", "BTC 2025-H2 misto"),
    ("CY.5", "cy-donchian-eth-2025h2", "ETH 2025-H2 misto"),
    ("CY.6", "cy-donchian-sol-2025h2", "SOL 2025-H2 misto"),
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
    mc = json.loads((p / "monte_carlo.json").read_text())
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
    mc_p5 = mc.get("payload", {}).get("p5_final_equity") if isinstance(mc.get("payload"), dict) else None
    if mc_p5 is None:
        # try alternative key paths
        payload = mc.get("payload") or mc
        mc_p5 = payload.get("p5") if isinstance(payload, dict) else None
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, mdd_pct=mdd, final_eq=final_eq, mc_p5=mc_p5)


def classify(sh, trades, pnl):
    if sh >= 1.0 and trades >= 30 and pnl > 3: return "hit forte"
    if sh >= 0.5 and trades >= 15 and pnl > 0: return "hit probe"
    return "miss"


def main():
    rows = []
    for tag, rid, combo in PROBES:
        m = metrics(rid)
        v = classify(m["sharpe"], m["trades"], m["pnl_pct"])
        rows.append({"tag": tag, "combo": combo, **m, "verdict": v})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2, default=str))
    print(f"{'Tag':<5} {'Combo':<20} {'Tr':>3} {'Sh':>7} {'PnL%':>7} {'MDD%':>6}  Verdict")
    for r in rows:
        print(f"{r['tag']:<5} {r['combo']:<20} "
              f"{r['trades']:>3} {r['sharpe']:>7.3f} {r['pnl_pct']:>7.2f} "
              f"{r['mdd_pct']:>6.2f}  {r['verdict']}")
    hits = sum(1 for r in rows if r["verdict"] == "hit forte")
    probes = sum(1 for r in rows if r["verdict"] == "hit probe")
    print(f"\nSumario CY: {hits} hit forte, {probes} hit probe, {len(rows)-hits-probes} miss")


if __name__ == "__main__":
    main()
