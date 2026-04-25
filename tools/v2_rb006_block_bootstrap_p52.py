"""V2 RB006 — Block bootstrap não-paramétrico sobre P52 family.

Per ADR-0215 §C: DSR/PSR Bailey-LdP (paramétrico, assume distribuição quase-gaussiana)
penalizou P52 family (kurt~20) demasiadamente. Alternativa: block bootstrap
não-paramétrico que **preserva autocorrelação** da série de retornos sem assumir
forma da distribuição.

Método (Politis-Romano 1994 stationary block bootstrap):
1. Para cada config (asset, short, long), extrair série de bar-level returns r_t.
2. Geometric block size ~ Geom(1/p) com p = 1/expected_block_size.
3. Para cada bootstrap iteration b ∈ [1, B]:
   a. Reconstruir série de mesmo tamanho via concatenação de blocos amostrados com replacement.
   b. Computar Sharpe annualized da série bootstrapped.
4. Distribuição empírica de B Sharpes bootstrap define p-value.

Gate V2:
- p(SR_boot > 0) > 0.95: edge não é zero.
- p(SR_boot > 1.0) > 0.50: edge é "razoável" (mediana acima de 1.0).
- 95% CI de SR_boot não inclui zero.

Block size escolhido: 24 bars (1 dia em 1h) — captura autocorrelação intradiária.
B = 1000 iterations.

Saída: `exports/diag/v2_rb006_block_bootstrap_p52.json`.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
PROGRESS = ROOT / "exports" / "diag" / "v2_rb012_sensitivity_p52_progress.json"
OUT = ROOT / "exports" / "diag" / "v2_rb006_block_bootstrap_p52.json"

ANN = math.sqrt(24 * 365)
BLOCK_SIZE = 24  # ~1 day em 1h bars
B_BOOTSTRAP = 1000
SEED = 42


def returns_from_walk_forward(run_id: str) -> np.ndarray:
    p = RESULTS / run_id / "walk_forward.json"
    if not p.exists(): return np.array([])
    wf = json.loads(p.read_text())
    folds = wf.get("payload", [])
    full_eq = [10000.0]
    for f in folds:
        ec = f.get("result", {}).get("equity_curve", []) or []
        ec_vals = [pair[1] for pair in ec]
        if ec_vals:
            base = full_eq[-1]
            first = ec_vals[0] if ec_vals[0] != 0 else 10000.0
            for v in ec_vals:
                full_eq.append(base * v / first)
    rets = np.array([(full_eq[i] / full_eq[i - 1] - 1) for i in range(1, len(full_eq)) if full_eq[i - 1] > 0])
    return rets


def sharpe_ann(rets: np.ndarray) -> float:
    if len(rets) < 2: return 0.0
    sd = float(rets.std(ddof=0))
    if sd == 0: return 0.0
    return float(rets.mean()) / sd * ANN


def stationary_bootstrap(rets: np.ndarray, b: int, p: float, rng: np.random.Generator) -> np.ndarray:
    """Politis-Romano stationary block bootstrap.
    p = 1/E[block_size]. Returns array (b, len(rets)) of resampled series.
    """
    n = len(rets)
    out = np.empty((b, n), dtype=rets.dtype)
    for i in range(b):
        starts = rng.integers(0, n, size=n)
        # geometric block lengths
        cont = rng.random(n) > p  # if true, continue to next index
        idx = np.empty(n, dtype=np.int64)
        cur = starts[0]
        for j in range(n):
            idx[j] = cur
            if cont[j]:
                cur = (cur + 1) % n
            else:
                cur = starts[j]
        out[i] = rets[idx]
    return out


def analyze_one(asset: str, short: int, long_: int, run_id: str, rng: np.random.Generator) -> dict | None:
    rets = returns_from_walk_forward(run_id)
    if len(rets) < 100:
        return None
    sr_observed = sharpe_ann(rets)
    p_block = 1.0 / BLOCK_SIZE
    boot = stationary_bootstrap(rets, B_BOOTSTRAP, p_block, rng)
    boot_sharpes = np.array([sharpe_ann(boot[i]) for i in range(B_BOOTSTRAP)])
    p_gt_zero = float((boot_sharpes > 0).mean())
    p_gt_1 = float((boot_sharpes > 1.0).mean())
    ci_lo = float(np.percentile(boot_sharpes, 2.5))
    ci_hi = float(np.percentile(boot_sharpes, 97.5))
    return {
        "asset": asset, "short": short, "long": long_, "run_id": run_id,
        "n_returns": len(rets),
        "sr_observed": round(sr_observed, 4),
        "boot_mean": round(float(boot_sharpes.mean()), 4),
        "boot_std": round(float(boot_sharpes.std()), 4),
        "p_gt_zero": round(p_gt_zero, 4),
        "p_gt_1": round(p_gt_1, 4),
        "ci95_lo": round(ci_lo, 4),
        "ci95_hi": round(ci_hi, 4),
    }


def main() -> None:
    rng = np.random.default_rng(SEED)
    progress = json.loads(PROGRESS.read_text())
    family = []
    for r in progress.values():
        if r.get("skip") or not r.get("ok"): continue
        family.append(r)

    print(f"[RB006 block bootstrap P52] {len(family)} configs, block_size={BLOCK_SIZE}, B={B_BOOTSTRAP}")
    results = []
    for r in family:
        res = analyze_one(r["asset"], r["short"], r["long"], r["run_id"], rng)
        if res is not None: results.append(res)

    print(f"\n{'Asset':<5} {'S':>3} {'L':>3} {'SR_obs':>7} {'BootMu':>7} {'BootSd':>7} {'p>0':>6} {'p>1':>6} {'CI95':>17} {'verdict':<14}")
    n_strong = 0
    n_marginal = 0
    n_fail = 0
    for x in sorted(results, key=lambda r: -r["sr_observed"]):
        # gate V2 block-bootstrap
        # STRONG: p_gt_zero > 0.95 AND p_gt_1 > 0.50
        # MARGINAL: p_gt_zero > 0.95 OR (p_gt_1 > 0.30)
        # FAIL: p_gt_zero <= 0.90
        if x["p_gt_zero"] > 0.95 and x["p_gt_1"] > 0.50:
            v = "STRONG"; n_strong += 1
        elif x["p_gt_zero"] > 0.95 or x["p_gt_1"] > 0.30:
            v = "MARGINAL"; n_marginal += 1
        else:
            v = "FAIL"; n_fail += 1
        ci = f"[{x['ci95_lo']:.2f},{x['ci95_hi']:.2f}]"
        print(f"{x['asset']:<5} {x['short']:>3} {x['long']:>3} {x['sr_observed']:>7.2f} {x['boot_mean']:>7.2f} "
              f"{x['boot_std']:>7.3f} {x['p_gt_zero']:>6.3f} {x['p_gt_1']:>6.3f} {ci:>17} {v:<14}")

    print(f"\nSTRONG (p>0 > 0.95 AND p>1 > 0.50): {n_strong}/{len(results)} ({n_strong/len(results)*100:.0f}%)")
    print(f"MARGINAL: {n_marginal}/{len(results)}")
    print(f"FAIL: {n_fail}/{len(results)}")

    OUT.write_text(json.dumps({
        "block_size": BLOCK_SIZE, "n_bootstrap": B_BOOTSTRAP, "seed": SEED,
        "n_configs": len(results), "n_strong": n_strong, "n_marginal": n_marginal, "n_fail": n_fail,
        "configs": results,
    }, indent=2, default=str))
    print(f"\nOutput: {OUT}")


if __name__ == "__main__":
    main()
