"""Resumir Serie CP Fase 1 (composite_bb_rsi short + width 2025-H1)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cp_fase1_summary.json"

# Baselines BB short 2025-H1 (para comparar lift do AND-entry).
# BTC: sem baseline explicito 2025-H1 BB short + width; tratar baseline=None.
# ETH/SOL: baselines de ADR-0186 table.
PROBES = [
    ("CP.1", "cp-btc-composite-short-width-2025h1", "BTC composite 2025H1", None, None),
    ("CP.2", "cp-eth-composite-short-width-2025h1", "ETH composite 2025H1", 2.40, 12.16),
    ("CP.3", "cp-sol-composite-short-width-2025h1", "SOL composite 2025H1", 2.71, 17.47),
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
    return dict(trades=n_tr, seqs=n_seq, pnl_pct=pnl_pct, sharpe=sh, folds=len(folds))


def main():
    rows = []
    for tag, rid, label, b_sh, b_pnl in PROBES:
        try:
            m = metrics(rid)
        except FileNotFoundError:
            print(f"{tag} {label}: MISSING")
            continue
        rows.append({"tag": tag, "label": label, "baseline_sh": b_sh,
                     "baseline_pnl": b_pnl, **m})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<6} {'Label':<22} {'Tr':>4} {'Seq':>4} {'Sh':>7} {'bSh':>5} {'dSh':>7} {'PnL%':>8}")
    passes_min = 0
    passes_edge = 0
    for r in rows:
        b_sh = r["baseline_sh"]
        dsh_str = f"{r['sharpe']-b_sh:+7.2f}" if b_sh is not None else "   N/A "
        b_sh_str = f"{b_sh:>5.2f}" if b_sh is not None else "  -  "
        print(
            f"{r['tag']:<6} {r['label']:<22} {r['trades']:>4} {r['seqs']:>4} "
            f"{r['sharpe']:>7.3f} {b_sh_str} {dsh_str} "
            f"{r['pnl_pct']:>8.2f}"
        )
        if r["sharpe"] >= 1.5 and r["trades"] >= 30:
            passes_min += 1
            if b_sh is None or r["sharpe"] >= 0.9 * b_sh:
                passes_edge += 1
    print(f"\nPass Sh>=1.5 AND trades>=30: {passes_min}/{len(rows)}")
    print(f"Pass AND Sh >= 0.9x baseline (edge preservation): {passes_edge}/{len(rows)}")


if __name__ == "__main__":
    main()
