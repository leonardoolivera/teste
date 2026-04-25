"""Resumir Serie PY Fase 2 (pyramid v4 em BB short + width proven combos)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_py2_fase2_summary.json"

PROBES = [
    ("PY.4", "py-sol-bb-short-width300-pyr-2025h1", "SOL BB+w 2025H1", 2.71, 17.47),
    ("PY.5", "py-eth-bb-short-width300-pyr-2025h1", "ETH BB+w 2025H1", 2.40, 12.16),
    ("PY.6", "py-sol-bb-short-width300-pyr-2024h2", "SOL BB+w 2024H2", 1.38,  6.64),
]


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


def _sequences(trades):
    if not trades:
        return 0
    return len({tr["exit_timestamp"] for tr in trades})


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
    n_tr = len(all_trades)
    n_seq = _sequences(all_trades)
    final_eq = full_eq[-1]
    pnl_pct = (final_eq / 10000.0 - 1) * 100
    rets = [(full_eq[i] / full_eq[i - 1] - 1) for i in range(1, len(full_eq)) if full_eq[i - 1] > 0]
    sh = annual_sharpe_1h(rets)
    return dict(trades=n_tr, seqs=n_seq, pnl_pct=pnl_pct, sharpe=sh)


def main():
    rows = []
    for tag, rid, label, b_sh, b_pnl in PROBES:
        try:
            m = metrics(rid)
        except FileNotFoundError:
            print(f"{tag} {label}: MISSING")
            continue
        rows.append({"tag": tag, "label": label, "baseline_sh": b_sh,
                     "baseline_pnl": b_pnl,
                     "lift_sh": m["sharpe"] - b_sh,
                     "lift_pnl": m["pnl_pct"] - b_pnl, **m})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<6} {'Label':<18} {'Tr':>4} {'Seq':>4} {'Sh':>7} {'bSh':>5} {'dSh':>7} {'PnL%':>8} {'bPnL':>6} {'dPnL':>7}")
    for r in rows:
        print(
            f"{r['tag']:<6} {r['label']:<18} {r['trades']:>4} {r['seqs']:>4} "
            f"{r['sharpe']:>7.3f} {r['baseline_sh']:>5.2f} {r['lift_sh']:>+7.2f} "
            f"{r['pnl_pct']:>8.2f} {r['baseline_pnl']:>6.2f} {r['lift_pnl']:>+7.2f}"
        )
    passing_min = [r for r in rows if r["sharpe"] >= 1.5 and r["seqs"] >= 10]
    preserving = [r for r in rows if r["sharpe"] >= 1.5 and r["seqs"] >= 10
                  and r["sharpe"] >= 0.9 * r["baseline_sh"]]
    print(f"\nPass Sh>=1.5 AND seqs>=10: {len(passing_min)}/{len(rows)}")
    print(f"Pass AND Sh >= 0.9x baseline (preserva edge): {len(preserving)}/{len(rows)}")
    for r in preserving:
        print(f"  {r['tag']} {r['label']}: Sh={r['sharpe']:.2f} vs base {r['baseline_sh']:.2f} (seq={r['seqs']}, PnL {r['pnl_pct']:.1f}% vs {r['baseline_pnl']:.1f}%)")


if __name__ == "__main__":
    main()
