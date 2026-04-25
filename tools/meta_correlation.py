"""Meta-analise: correlacao retornos bar-a-bar entre combos do stack approved.

Calcula correlacao Pearson entre serie de retornos hourly extraida de
walk_forward.json::payload[*].equity_curve de cada combo. Apenas combos na
mesma window sao comparaveis (ret[t] depende de bar alignment).

Output: correlacao dentro de cada window.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"

COMBOS = [
    # (label, run_id, asset, window)
    ("v3_bol_sh_SOL_24H2", "cg-bol-20-15-sol-20240705_20241231-width30-300-short", "SOL", "2024-H2"),
    ("v3_bol_sh_BTC_25H1", "cg-bol-20-15-btc-20250105_20250704-width30-300-short", "BTC", "2025-H1"),
    ("v3_bol_sh_ETH_25H1", "cg-bol-20-15-eth-20250105_20250704-width30-300-short", "ETH", "2025-H1"),
    ("v3_bol_sh_SOL_25H1", "cg-bol-20-15-sol-20250105_20250704-width30-300-short", "SOL", "2025-H1"),
    ("v4a_rsi_w_BTC_25H1", "ch-rsi-14-30-70-btc-20250105_20250704-width30-300-short", "BTC", "2025-H1"),
    ("v4b_rsi_n_BTC_25H2", "audit-v4-b-btc-20250705_20251231-nofilter", "BTC", "2025-H2"),
    ("v4b_rsi_n_SOL_25H2", "audit-v4-b-sol-20250705_20251231-nofilter", "SOL", "2025-H2"),
    ("v6_rsi_t_SOL_25H1", "co-audit-noWidth-sol-20250105_20250704-short", "SOL", "2025-H1"),
]


def equity_to_rets(rid):
    """Extrai retornos bar-a-bar concatenando folds."""
    p = RESULTS / rid / "walk_forward.json"
    if not p.exists():
        return None
    wf = json.loads(p.read_text())["payload"]
    full_eq = [10000.0]
    for f in wf:
        ec_pairs = f["result"].get("equity_curve", [])
        ec_vals = [pair[1] for pair in ec_pairs]
        if ec_vals:
            base = full_eq[-1]
            first = ec_vals[0] if ec_vals[0] != 0 else 10000.0
            for v in ec_vals:
                full_eq.append(base * v / first)
    rets = [full_eq[i]/full_eq[i-1] - 1 for i in range(1, len(full_eq)) if full_eq[i-1] > 0]
    return rets


def pearson(a, b):
    n = min(len(a), len(b))
    if n < 10: return None
    a, b = a[:n], b[:n]
    ma = sum(a)/n; mb = sum(b)/n
    va = sum((x-ma)**2 for x in a)
    vb = sum((x-mb)**2 for x in b)
    if va == 0 or vb == 0: return None
    cov = sum((a[i]-ma)*(b[i]-mb) for i in range(n))
    return cov / math.sqrt(va*vb)


def main():
    by_window = defaultdict(list)
    for label, rid, asset, win in COMBOS:
        rets = equity_to_rets(rid)
        if rets is None:
            print(f"SKIP {label} (no walk_forward.json)")
            continue
        by_window[win].append((label, asset, rets))

    for win in sorted(by_window.keys()):
        combos = by_window[win]
        if len(combos) < 2:
            print(f"\n### Window {win}: only {len(combos)} combo(s), skip correlation")
            continue
        print(f"\n### Window {win} — {len(combos)} combos, pairwise Pearson")
        labels = [c[0] for c in combos]
        print(f"{'':<22}", end="")
        for l in labels:
            print(f"{l[:18]:>20}", end="")
        print()
        for i, (li, ai, ri) in enumerate(combos):
            print(f"{li:<22}", end="")
            for j, (lj, aj, rj) in enumerate(combos):
                if i == j:
                    print(f"{'1.00':>20}", end="")
                else:
                    r = pearson(ri, rj)
                    s = f"{r:+.2f}" if r is not None else "n/a"
                    print(f"{s:>20}", end="")
            print()

    print("\n### Interpretacao:")
    print(" |r| < 0.3  -> diversificador (adicionar combo reduz risco)")
    print(" 0.3 <= |r| < 0.7 -> parcialmente correlacionado (diversificacao moderada)")
    print(" |r| >= 0.7 -> redundante (combo adicional nao traz muito)")


if __name__ == "__main__":
    main()
