"""Meta-analise: correlacao retornos dos combos live do stack em 2025-H1.

Calcula matriz de correlacao entre 6 combos 2025-H1 ativos, usando retornos
hora-a-hora das equity curves agregadas dos folds walk-forward.

Output: exports/diag/stack_correlation_2025h1.json com matriz + interpretacao.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "stack_correlation_2025h1.json"

COMBOS = [
    ("bol_short_BTC", "cg-bol-20-15-btc-20250105_20250704-width30-300-short"),
    ("bol_short_ETH", "cg-bol-20-15-eth-20250105_20250704-width30-300-short"),
    ("bol_short_SOL", "cg-bol-20-15-sol-20250105_20250704-width30-300-short"),
    ("rsi_short_width_BTC", "ch-rsi-14-30-70-btc-20250105_20250704-width30-300-short"),
    ("rsi_short_trendhtf_SOL_2575", "cz10-sol-rsi-2575-trendhtf-1h-2025h1"),
]


def equity_timeseries(rid: str) -> dict:
    """Concatena equity curves dos folds em dict {ts -> equity_normalized}."""
    wf = json.loads((RESULTS / rid / "walk_forward.json").read_text())
    ts_to_eq = {}
    base_eq = 10000.0
    for fold in wf["payload"]:
        ec_pairs = fold["result"].get("equity_curve", [])
        if not ec_pairs:
            continue
        first = ec_pairs[0][1] if ec_pairs[0][1] != 0 else 10000.0
        for ts_str, eq in ec_pairs:
            norm = base_eq * eq / first
            ts_to_eq[ts_str] = norm
        base_eq = ts_to_eq[ec_pairs[-1][0]]
    return ts_to_eq


def to_returns(ts_eq: dict) -> dict:
    """Converte {ts -> eq} em {ts -> retorno hora-a-hora}."""
    items = sorted(ts_eq.items())
    rets = {}
    for i in range(1, len(items)):
        prev_eq = items[i - 1][1]
        cur_ts, cur_eq = items[i]
        if prev_eq > 0:
            rets[cur_ts] = (cur_eq / prev_eq) - 1.0
    return rets


def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


def main():
    returns_by_combo = {}
    for label, rid in COMBOS:
        ts_eq = equity_timeseries(rid)
        rets = to_returns(ts_eq)
        returns_by_combo[label] = rets
        print(f"{label:<35} ts_count={len(rets)}")

    # Alinhar timestamps (usar intersecao de todos)
    common_ts = set.intersection(*(set(r.keys()) for r in returns_by_combo.values()))
    common_ts = sorted(common_ts)
    print(f"\nTimestamps comuns: {len(common_ts)}")

    aligned = {label: [returns_by_combo[label][t] for t in common_ts] for label in returns_by_combo}

    # Matriz de correlacao
    labels = list(aligned.keys())
    matrix = {}
    for a in labels:
        matrix[a] = {}
        for b in labels:
            matrix[a][b] = round(pearson(aligned[a], aligned[b]), 4)

    # Imprimir matriz
    print(f"\n{'':<35} " + " ".join(f"{l[:12]:>12}" for l in labels))
    for a in labels:
        row = " ".join(f"{matrix[a][b]:>12.3f}" for b in labels)
        print(f"{a:<35} {row}")

    # Estatisticas off-diagonal
    off_diag = []
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            if i < j:
                off_diag.append((a, b, matrix[a][b]))

    off_diag.sort(key=lambda x: x[2], reverse=True)
    print("\nPares por correlacao (desc):")
    for a, b, c in off_diag:
        print(f"  {c:+.3f}  {a} <-> {b}")

    mean_corr = sum(c for _, _, c in off_diag) / len(off_diag)
    max_corr = max(c for _, _, c in off_diag)
    min_corr = min(c for _, _, c in off_diag)
    print(f"\nMean off-diag: {mean_corr:.3f}")
    print(f"Max off-diag:  {max_corr:.3f}")
    print(f"Min off-diag:  {min_corr:.3f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "combos": labels,
        "matrix": matrix,
        "pairs": [{"a": a, "b": b, "corr": c} for a, b, c in off_diag],
        "summary": {
            "mean_off_diag": round(mean_corr, 4),
            "max_off_diag": round(max_corr, 4),
            "min_off_diag": round(min_corr, 4),
            "n_timestamps_aligned": len(common_ts),
        },
    }, indent=2))
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()
