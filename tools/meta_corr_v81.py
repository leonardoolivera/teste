"""Meta-correlacao v8.1: BTC + SOL RSI short naked 2025-H2.

Computa correlacao de retornos OOS bar-a-bar entre os 2 combos ativos
do manifest v8.1 para validar diversificacao.

ADR-0098 Gate 4 nao foi executado (backlog). Agora preenchido sem LINK.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "meta_corr_v81.json"

RUNS = [
    ("BTC", "audit-v4-b-btc-20250705_20251231-nofilter"),
    ("SOL", "audit-v4-b-sol-20250705_20251231-nofilter"),
]


def load_returns(rid):
    """Retorna lista de (timestamp, return_pct) bar-a-bar do walk-forward."""
    p = RESULTS / rid
    wf = json.loads((p / "walk_forward.json").read_text())
    folds = wf["payload"]
    rets = []
    last_val = None
    last_ts = None
    for f in folds:
        ec = f["result"].get("equity_curve", [])
        for ts, val in ec:
            if last_val is not None and last_val > 0 and ts != last_ts:
                r = (val / last_val) - 1
                rets.append((ts, r))
            last_val = val
            last_ts = ts
    return rets


def pearson(xs, ys):
    n = len(xs)
    if n < 2: return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0: return 0.0
    return num / (dx * dy)


def align_by_ts(series_a, series_b):
    """Pareia por timestamp exato."""
    dict_a = dict(series_a)
    dict_b = dict(series_b)
    common_ts = sorted(set(dict_a.keys()) & set(dict_b.keys()))
    return [dict_a[t] for t in common_ts], [dict_b[t] for t in common_ts], common_ts


def main():
    series = {}
    for name, rid in RUNS:
        rets = load_returns(rid)
        series[name] = rets
        print(f"{name}: {len(rets)} bars")

    btc_rets, sol_rets, common = align_by_ts(series["BTC"], series["SOL"])
    print(f"Common bars: {len(common)}")

    corr = pearson(btc_rets, sol_rets)

    # Tambem calcula sobre retornos nao-zero (dias com exposicao)
    nz_pairs = [(b, s) for b, s in zip(btc_rets, sol_rets) if abs(b) > 1e-9 and abs(s) > 1e-9]
    if nz_pairs:
        corr_nz = pearson([p[0] for p in nz_pairs], [p[1] for p in nz_pairs])
    else:
        corr_nz = None

    # Conta periodos de exposicao conjunta
    both_exposed = sum(1 for b, s in zip(btc_rets, sol_rets) if abs(b) > 1e-9 and abs(s) > 1e-9)
    only_btc = sum(1 for b, s in zip(btc_rets, sol_rets) if abs(b) > 1e-9 and abs(s) <= 1e-9)
    only_sol = sum(1 for b, s in zip(btc_rets, sol_rets) if abs(b) <= 1e-9 and abs(s) > 1e-9)
    neither = sum(1 for b, s in zip(btc_rets, sol_rets) if abs(b) <= 1e-9 and abs(s) <= 1e-9)

    summary = {
        "manifest": "v8.1 (BTC + SOL RSI short naked 2025-H2)",
        "common_bars": len(common),
        "corr_all_bars": round(corr, 4),
        "corr_both_exposed": round(corr_nz, 4) if corr_nz is not None else None,
        "exposure_regime": {
            "both_exposed": both_exposed,
            "only_btc": only_btc,
            "only_sol": only_sol,
            "neither": neither,
        },
        "interpretation": (
            "corr_all_bars inclui barras sem exposicao (0,0) que inflam correlacao para 0. "
            "corr_both_exposed e o numero relevante: correlacao real quando ambos combos posicionados. "
            "Alvo: |corr| < 0.6 indica diversificacao razoavel; > 0.8 sugere que combos sao redundantes."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

    # Verdict
    if corr_nz is None:
        print("\nVERDICT: sem barras de exposicao conjunta (combos nunca ativos juntos)")
    elif abs(corr_nz) < 0.6:
        print(f"\nVERDICT: diversificacao OK (|corr_exposed|={abs(corr_nz):.3f} < 0.6)")
    elif abs(corr_nz) < 0.8:
        print(f"\nVERDICT: correlacao moderada ({corr_nz:.3f}); stack beneficia mas nao e ortogonal")
    else:
        print(f"\nVERDICT: correlacao alta ({corr_nz:.3f}); combos podem estar duplicando risco")


if __name__ == "__main__":
    main()
