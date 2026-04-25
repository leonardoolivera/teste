"""V2 RB014/RB015 — Deflated Sharpe Ratio (DSR) + Probabilistic Sharpe Ratio (PSR) sobre P52 family.

Padrão 52 family = ma_crossover variantes em (BTC, ETH, SOL × 2024-H2). Com Sensitivity
test rodando 48 perturbações vizinhas, multiple testing correction é necessária para
validar que o Sharpe observado não é artefato de busca em N vizinhos correlacionados.

Implementação:

PSR (Bailey & López de Prado 2014):
  PSR(SR*) = Phi(((SR_obs - SR*) * sqrt(N - 1)) / sqrt(1 - skew*SR_obs + (kurt-1)/4 * SR_obs^2))

  PSR > 0.95 = >95% de confiança que verdadeiro Sharpe > SR* (default SR* = 0).

DSR (Bailey & López de Prado 2014):
  Deflate o threshold SR* baseado no número de trials independentes N e skew/kurt:
  SR_0 = sqrt(V[{SR_n}]) * ((1-gamma) * Phi^-1(1 - 1/N) + gamma * Phi^-1(1 - 1/N * exp(-1)))
  onde gamma é Euler-Mascheroni.

  Então DSR(SR_obs) = PSR(SR_obs; threshold=SR_0).

Aplicação a P52: para cada combo (asset, short, long), pegar a série de retornos dos
trades + computar PSR e DSR. Validate sobreviventes.

Saída: `exports/diag/v2_rb014_dsr_psr_p52.json` + stdout.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import norm, skew, kurtosis

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
PROGRESS = ROOT / "exports" / "diag" / "v2_rb012_sensitivity_p52_progress.json"
OUT = ROOT / "exports" / "diag" / "v2_rb014_dsr_psr_p52.json"

EULER_MASCHERONI = 0.5772156649

# Annual factor for 1h bars
ANN = math.sqrt(24 * 365)


def returns_from_walk_forward(run_id: str) -> list[float]:
    """Extract bar-level returns from concatenated equity_curve."""
    p = RESULTS / run_id / "walk_forward.json"
    if not p.exists(): return []
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
    rets = [(full_eq[i] / full_eq[i - 1] - 1) for i in range(1, len(full_eq)) if full_eq[i - 1] > 0]
    return rets


def annualized_sharpe(rets: np.ndarray) -> float:
    if len(rets) < 2: return 0.0
    mu = float(rets.mean())
    sd = float(rets.std(ddof=0))
    if sd == 0: return 0.0
    return mu / sd * ANN


def psr(sr_obs: float, sr_star: float, n: int, sk: float, kt: float, ann: float) -> float:
    """Probabilistic Sharpe Ratio (Bailey & Lopez de Prado 2014).

    sr_obs and sr_star are annualized (per the paper). We compute the bar-level
    quantities by dividing by sqrt(ann).
    """
    if n < 2: return 0.0
    sr_obs_bar = sr_obs / ann
    sr_star_bar = sr_star / ann
    denom = math.sqrt(1 - sk * sr_obs_bar + (kt - 1) / 4.0 * sr_obs_bar * sr_obs_bar)
    if denom <= 0: return 0.0
    z = (sr_obs_bar - sr_star_bar) * math.sqrt(n - 1) / denom
    return float(norm.cdf(z))


def dsr_threshold(sharpes: np.ndarray) -> float:
    """Deflated Sharpe Ratio threshold given a family of trials' annualized Sharpes.

    Returns SR_0 (annualized) that should be exceeded for significance.
    """
    n = len(sharpes)
    if n < 2: return 0.0
    var_sr = float(np.var(sharpes, ddof=1))
    sd_sr = math.sqrt(var_sr) if var_sr > 0 else 0.0
    if sd_sr == 0: return 0.0
    inv1 = norm.ppf(1 - 1.0 / n)
    inv2 = norm.ppf(1 - 1.0 / n * math.exp(-1))
    sr_0 = sd_sr * ((1 - EULER_MASCHERONI) * inv1 + EULER_MASCHERONI * inv2)
    return float(sr_0)


def main() -> None:
    progress = json.loads(PROGRESS.read_text())
    family = []
    for k, r in progress.items():
        if r.get("skip") or not r.get("ok"): continue
        rets = returns_from_walk_forward(r["run_id"])
        if len(rets) < 30: continue
        arr = np.array(rets)
        sr = annualized_sharpe(arr)
        sk = float(skew(arr))
        kt = float(kurtosis(arr, fisher=False))  # excess+3
        family.append({
            "key": k, "asset": r["asset"], "short": r["short"], "long": r["long"],
            "n": len(rets), "sharpe": round(sr, 4), "skew": round(sk, 4), "kurt": round(kt, 4),
        })
    if not family:
        print("no valid runs")
        return

    sharpes = np.array([x["sharpe"] for x in family])
    sr0 = dsr_threshold(sharpes)
    print(f"\n{'='*70}\nRB014/RB015 — DSR/PSR sobre P52 family ({len(family)} configs)\n{'='*70}")
    print(f"Annualized Sharpes: min={sharpes.min():.2f} med={np.median(sharpes):.2f} max={sharpes.max():.2f}")
    print(f"Variance of family Sharpes: {np.var(sharpes, ddof=1):.4f}")
    print(f"DSR threshold (SR_0 annualized) = {sr0:.4f}")
    print(f"  -> Para passar DSR test: Sharpe observado > {sr0:.2f} (annualized) com PSR > 0.95")

    # Compute PSR vs SR_0 (DSR threshold) and PSR vs 0
    print(f"\n{'Asset':<5} {'S':>3} {'L':>3} {'N':>5} {'SR_ann':>7} {'skew':>6} {'kurt':>6} {'PSR(0)':>8} {'PSR(DSR)':>10} {'verdict':<10}")
    survivors = []
    for x in family:
        psr_zero = psr(x["sharpe"], 0.0, x["n"], x["skew"], x["kurt"], ANN)
        psr_dsr = psr(x["sharpe"], sr0, x["n"], x["skew"], x["kurt"], ANN)
        verdict = "DSR-PASS" if psr_dsr > 0.95 else ("MARGINAL" if psr_dsr > 0.50 else "FAIL")
        if psr_dsr > 0.95: survivors.append(x)
        x["psr_zero"] = round(psr_zero, 4)
        x["psr_dsr"] = round(psr_dsr, 4)
        x["verdict"] = verdict
        print(f"{x['asset']:<5} {x['short']:>3} {x['long']:>3} {x['n']:>5} {x['sharpe']:>7.2f} "
              f"{x['skew']:>6.2f} {x['kurt']:>6.2f} {psr_zero:>8.4f} {psr_dsr:>10.4f} {verdict}")
    print(f"\nDSR-PASS: {len(survivors)}/{len(family)} ({len(survivors)/len(family)*100:.0f}%)")

    OUT.write_text(json.dumps({
        "n_configs": len(family),
        "dsr_threshold_sr0": sr0,
        "family": family,
        "survivors_dsr": [s["key"] for s in survivors],
    }, indent=2, default=str))
    print(f"\nOutput: {OUT}")


if __name__ == "__main__":
    main()
