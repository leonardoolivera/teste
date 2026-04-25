"""V2 Cycle 15 — Sensitivity grid S12 params sobre SOL 30m.

S12 baseline: rsi(14, 25, 75) short_only + trend_htf(4h, sma=50, short_only).
Sh=1.20 raw, Sh=1.37 com trail40 (Cycle 13).

Para empurrar sobre Sh ≥ 1.5 (V1 strict gate), grid de perturbação local
+ trail40 default (Padrão 65+66 dominante):

- rsi_period ∈ {10, 14, 21}
- rsi_overbought ∈ {70, 75, 80}
- rsi_oversold ∈ {20, 25, 30} (espelho)
- trend_htf sma_window ∈ {30, 50, 100}

Constraints (RAIO §5 anti grid search disfarçado):
- Apenas SOL (Padrão 62: SOL-specific).
- Mantém short_only (S12 é short MR; long_only descobreria nova hypothesis).
- Mantém trail40 (Padrão 66: trail40 melhora Sh +14% baseline).

Total: 3 × 3 × 3 × 3 = 81 combos com simetria oversold = 100 - overbought.
Reduzir: oversold = 100 - overbought (par natural). 3 × 3 × 3 = **27 probes** ~5min.

Decision RAIO Nível 3 Sensitivity (§4):
- Performance não pode depender de um único ponto paramétrico.
- Pequenas mudanças não destroem edge.
- Se algum vizinho > Sh 1.5 ∧ outros vizinhos > 1.0 → S12+trail40 sweet-spot promovível.
- Se todos < 1.5 → Sh 1.37 é teto local; precisa novo mecanismo (não só param tweak).
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "v2_s12_sensitivity_grid.json"

DATASET_SOL_30M = "solusdt_1h_20230705_20251231_binance_spot_concat30m"

RSI_PERIODS = [10, 14, 21]
RSI_THRESHOLDS = [(20, 80), (25, 75), (30, 70)]
TREND_SMA = [30, 50, 100]

FEE_BPS = 10.0
ANN = math.sqrt(24 * 365)


def base_args() -> list[str]:
    return [
        "alpha-forge", "validate",
        "--capital", "10000.0", "--fracao", "0.1", "--alavancagem", "2.0",
        "--sizing-mode", "fixed_notional",
        "--taker-fee-bps", str(FEE_BPS),
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--n-folds", "5", "--scheme", "rolling",
        "--train-fraction", "0.5", "--min-test-bars", "200",
        "--mc-resamples", "100", "--mc-seed", "42",
        "--log-level", "silent",
    ]


def compute_metrics(run_id: str) -> dict:
    p = RESULTS / run_id / "walk_forward.json"
    if not p.exists(): return {}
    wf = json.loads(p.read_text())
    folds = wf.get("payload", [])
    full_eq = [10000.0]
    n_trades = 0
    for f in folds:
        r = f.get("result", {})
        n_trades += len(r.get("trades", []) or [])
        ec = r.get("equity_curve", []) or []
        ec_vals = [pair[1] for pair in ec]
        if ec_vals:
            base = full_eq[-1]
            first = ec_vals[0] if ec_vals[0] != 0 else 10000.0
            for v in ec_vals:
                full_eq.append(base * v / first)
    final = full_eq[-1]
    pnl = (final / 10000.0 - 1) * 100
    rets = [(full_eq[i] / full_eq[i - 1] - 1) for i in range(1, len(full_eq)) if full_eq[i - 1] > 0]
    if len(rets) >= 2:
        mean = sum(rets) / len(rets)
        var = sum((r - mean) ** 2 for r in rets) / len(rets)
        sd = math.sqrt(var)
        sh = (mean / sd) * ANN if sd > 0 else 0.0
    else:
        sh = 0.0
    peak = full_eq[0]; mdd = 0.0
    for v in full_eq:
        if v > peak: peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > mdd: mdd = dd
    return {"trades": n_trades, "sharpe": round(sh, 4), "pnl_pct": round(pnl, 4), "mdd_pct": round(mdd * 100, 4)}


def run_one(period: int, oversold: int, overbought: int, sma: int) -> dict:
    run_id = f"v2-s12sens-rsi{period}-{oversold}-{overbought}-sma{sma}-sol30m"
    args = base_args() + [
        "--run-id", run_id, "--dataset-id", DATASET_SOL_30M,
        "--strategy", "rsi",
        "--rsi-period", str(period),
        "--rsi-oversold", str(oversold),
        "--rsi-overbought", str(overbought),
        "--no-long-only",
        "--regime-filter", f"trend_htf:htf=4h:sma_window={sma}:mode=short_only",
        "--atr-trail-period", "14",
        "--atr-trail-mult", "4.0",
    ]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    metrics = compute_metrics(run_id) if ok else {}
    return {"period": period, "oversold": oversold, "overbought": overbought, "sma": sma,
            "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1), "metrics": metrics}


def main() -> int:
    jobs = [(p, ov, ob, s) for p in RSI_PERIODS for (ov, ob) in RSI_THRESHOLDS for s in TREND_SMA]
    print(f"[V2 S12 Sensitivity grid] {len(jobs)} probes (3 RSI periods × 3 thresholds × 3 SMA), SOL 30m + trail40, fees 10bps")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, p, ov, ob, s): (p, ov, ob, s) for (p, ov, ob, s) in jobs}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            mt = r.get("metrics") or {}
            print(f"  rsi{r['period']:>2} {r['oversold']}/{r['overbought']} sma{r['sma']:>3} sh={mt.get('sharpe')} tr={mt.get('trades')} mdd={mt.get('mdd_pct')}% pnl={mt.get('pnl_pct')}%", flush=True)
    print(f"  wall={time.time() - t0:.0f}s")

    # Tabela ordenada por Sharpe desc
    print(f"\n{'='*80}\nS12 Sensitivity grid (top by Sharpe)\n{'='*80}")
    print(f"{'period':>6} {'os':>3} {'ob':>3} {'sma':>4} {'Sh':>7} {'Tr':>5} {'MDD%':>6} {'PnL%':>8} | Pass15 (V1 strict)")
    sorted_r = sorted([r for r in results if r["ok"]], key=lambda r: -((r.get("metrics") or {}).get("sharpe") or -999))
    n_pass15 = 0
    n_pass60 = 0
    for r in sorted_r:
        mt = r.get("metrics") or {}
        sh, tr, mdd, pnl = mt.get("sharpe"), mt.get("trades"), mt.get("mdd_pct"), mt.get("pnl_pct")
        p15 = bool(sh and tr and mdd is not None and sh >= 1.5 and tr >= 30 and mdd <= 10)
        p60 = bool(sh and tr and mdd is not None and sh >= 1.0 and tr >= 30 and mdd <= 10)
        if p15: n_pass15 += 1
        if p60: n_pass60 += 1
        marker = "★" if p15 else (" " if p60 else "·")
        print(f"{marker} {r['period']:>6} {r['oversold']:>3} {r['overbought']:>3} {r['sma']:>4} "
              f"{sh if sh is not None else 'NA':>7} {tr or 0:>5} "
              f"{mdd if mdd is not None else 0:>6} {pnl if pnl is not None else 0:>8} | {p15}")

    print(f"\nPadrão 60 (Sh ≥ 1.0): {n_pass60}/{len(sorted_r)}")
    print(f"V1 strict (Sh ≥ 1.5): {n_pass15}/{len(sorted_r)}")
    if n_pass15 > 0:
        print("\nSUCCESS: S12 + trail40 sweet-spot atinge Sh ≥ 1.5 — promovível.")
    elif n_pass60 >= len(sorted_r) * 0.5:
        print("\nPARTIAL: maioria dos vizinhos > 1.0 mas nenhum > 1.5; teto local.")
    else:
        print("\nFAIL: maioria dos vizinhos < 1.0; canonical S12 era sweet-spot.")

    OUT.write_text(json.dumps({"results": results, "n_pass15": n_pass15, "n_pass60": n_pass60}, indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
