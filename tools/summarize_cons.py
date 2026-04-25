"""Resumir Serie CONS Fase 1 (BB short max_width pyramid 1h, 3 runs)."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_cons_fase1_summary.json"

PROBES = [
    ("CONS.1", "cons-btc-bol-short-maxwidth-pyr-2025h1", "BTC 2025-H1"),
    ("CONS.2", "cons-eth-bol-short-maxwidth-pyr-2025h1", "ETH 2025-H1"),
    ("CONS.3", "cons-sol-bol-short-maxwidth-pyr-2025h1", "SOL 2025-H1"),
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


def _pyramid_sequences(trades):
    """Conta sequências de entrada distintas (ADR-0180 approval gate).

    Tranches que fecham no mesmo exit_timestamp = 1 sequência.
    """
    if not trades:
        return 0
    seqs = set()
    for tr in trades:
        seqs.add(tr["exit_timestamp"])
    return len(seqs)


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
    n_seqs = _pyramid_sequences(all_trades)
    final_eq = full_eq[-1]
    pnl_pct = (final_eq / 10000.0 - 1) * 100
    rets = [(full_eq[i] / full_eq[i - 1] - 1) for i in range(1, len(full_eq)) if full_eq[i - 1] > 0]
    sh = annual_sharpe_1h(rets)
    return dict(trades=n_trades, sequences=n_seqs, pnl_pct=pnl_pct, sharpe=sh)


def main():
    rows = []
    for tag, rid, label in PROBES:
        try:
            m = metrics(rid)
        except FileNotFoundError:
            print(f"{tag} {label}: MISSING")
            continue
        rows.append({"tag": tag, "label": label, **m})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"{'Tag':<8} {'Label':<14} {'Tr':>4} {'Seq':>4} {'Sh':>7} {'PnL%':>8}")
    for r in rows:
        print(
            f"{r['tag']:<8} {r['label']:<14} {r['trades']:>4} {r['sequences']:>4} "
            f"{r['sharpe']:>7.3f} {r['pnl_pct']:>8.2f}"
        )
    # ADR-0181 gate Fase 1: Sh>=1.5 AND sequences>=10, >= 2/3 assets
    passing = [r for r in rows if r["sharpe"] >= 1.5 and r["sequences"] >= 10]
    print(f"\nPass Sh>=1.5 AND seq>=10: {len(passing)}/{len(rows)}")
    for r in passing:
        print(f"  {r['tag']} {r['label']}: Sh={r['sharpe']:.2f} seq={r['sequences']}")


if __name__ == "__main__":
    main()
