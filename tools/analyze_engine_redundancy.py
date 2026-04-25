"""Analise redundancia engine-only: 3 pares bol vs rsi-width (mesmo asset/filter/direcao).

Compara Sharpe/MDD/PnL/trades em H1 + H2 para decidir qual engine e superior
em cada (asset, filter, direcao) triplet.

Output: exports/diag/engine_redundancy_analysis.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "engine_redundancy_analysis.json"

# 3 pares engine-only redundantes (mesmo asset/filter/direcao)
PAIRS = [
    ("BTC short width", [
        ("bol", "cg-bol-20-15-btc-20250105_20250704-width30-300-short"),
        ("rsi", "ch-rsi-14-30-70-btc-20250105_20250704-width30-300-short"),
    ], "H1"),
    ("BTC short width", [
        ("bol", "cg-bol-20-15-btc-20250705_20251231-width30-300-short"),
        ("rsi", "ch-rsi-14-30-70-btc-20250705_20251231-width30-300-short"),
    ], "H2"),
    ("ETH short width", [
        ("bol", "cg-bol-20-15-eth-20250105_20250704-width30-300-short"),
        ("rsi", "ch-rsi-14-30-70-eth-20250105_20250704-width30-300-short"),
    ], "H1"),
    ("ETH short width", [
        ("bol", "cg-bol-20-15-eth-20250705_20251231-width30-300-short"),
        ("rsi", "ch-rsi-14-30-70-eth-20250705_20251231-width30-300-short"),
    ], "H2"),
    ("SOL short width", [
        ("bol", "cg-bol-20-15-sol-20250105_20250704-width30-300-short"),
        ("rsi", "ch-rsi-14-30-70-sol-20250105_20250704-width30-300-short"),
    ], "H1"),
    ("SOL short width", [
        ("bol", "cg-bol-20-15-sol-20250705_20251231-width30-300-short"),
        ("rsi", "ch-rsi-14-30-70-sol-20250705_20251231-width30-300-short"),
    ], "H2"),
    ("BTC short width", [
        ("bol", "cg-bol-20-15-btc-20240705_20241231-width30-300-short"),
        ("rsi", "ch-rsi-14-30-70-btc-20240705_20241231-width30-300-short"),
    ], "2024H2"),
    ("ETH short width", [
        ("bol", "cg-bol-20-15-eth-20240705_20241231-width30-300-short"),
        ("rsi", "ch-rsi-14-30-70-eth-20240705_20241231-width30-300-short"),
    ], "2024H2"),
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
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, mdd_pct=mdd)


def main():
    print(f"{'Triplet':<20} {'Win':<3} {'Engine':<5} {'Tr':>4} {'Sh':>7} {'PnL%':>7} {'MDD%':>6}")
    print("-" * 70)
    rows = []
    for triplet, engines, window in PAIRS:
        for eng, rid in engines:
            m = metrics(rid)
            rows.append({"triplet": triplet, "window": window, "engine": eng, **m})
            print(f"{triplet:<20} {window:<3} {eng:<5} {m['trades']:>4} "
                  f"{m['sharpe']:>7.3f} {m['pnl_pct']:>7.2f} {m['mdd_pct']:>6.2f}")
        print()

    # Agregacao por (triplet, engine) combinando H1+H2
    print("\n=== Agregado por triplet (H1+H2 media Sharpe) ===")
    agg = {}
    for r in rows:
        key = (r["triplet"], r["engine"])
        agg.setdefault(key, []).append(r["sharpe"])
    summary_agg = []
    for (triplet, engine), shs in sorted(agg.items()):
        mean_sh = sum(shs) / len(shs)
        min_sh = min(shs)
        summary_agg.append({"triplet": triplet, "engine": engine,
                            "mean_sharpe": mean_sh, "min_sharpe": min_sh, "n": len(shs)})
        print(f"{triplet:<20} {engine:<5} mean={mean_sh:+.3f} min={min_sh:+.3f}")

    # Decisao: para cada triplet, qual engine tem mean_sharpe mais alto
    print("\n=== Vencedor por triplet ===")
    winners = {}
    triplets = set(r["triplet"] for r in rows)
    for t in sorted(triplets):
        best = max([a for a in summary_agg if a["triplet"] == t], key=lambda x: x["mean_sharpe"])
        other = [a for a in summary_agg if a["triplet"] == t and a["engine"] != best["engine"]][0]
        gap = best["mean_sharpe"] - other["mean_sharpe"]
        winners[t] = {"winner": best["engine"], "loser": other["engine"],
                       "gap_mean_sh": gap,
                       "winner_mean_sh": best["mean_sharpe"],
                       "loser_mean_sh": other["mean_sharpe"]}
        print(f"  {t}: WINNER={best['engine']} ({best['mean_sharpe']:+.3f}) vs {other['engine']} ({other['mean_sharpe']:+.3f}) gap={gap:+.3f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"rows": rows, "aggregated": summary_agg, "winners": winners}, indent=2))
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()
