"""V2 Cycle 16 — LQ001/LQ002 Liquidity Trap scout (RAIO Nível 1).

Mecanismo causal V2: false breakout com close back inside range gera reversão.
Primeiro engine V2/RAIO com mecanismo causal **fundamentalmente novo** (não
param tweak de bollinger/rsi/etc).

Configs:
- 3 lookbacks: 15, 20, 30
- 1 exit_mean_window: 10
- 3 assets: BTC, ETH, SOL × janela contínua 30m
- 2 variants: raw, + trail40 (Padrão 65 dominante)

Total: 3 × 3 × 2 = 18 probes ~5min wall-clock.

Gate Padrão 60 (V2 reformulado): Sh ≥ 1.0 ∧ trades ≥ 30 ∧ MDD ≤ 10%.
+ Padrão 68 (Sensitivity): se algum vizinho passa, todos vizinhos devem ≥75%.

Decision:
- Se ≥ 2 assets pass + lookback robusto (2/3 lookbacks pass mesmo asset) → SCOUTING
- Se 1 asset pass + lookback singular → QUARANTINED
- Se 0 pass → GRAVEYARD (Padrão 69 candidate)
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
OUT = ROOT / "exports" / "diag" / "v2_lq_scout.json"

DATASETS_30M = {
    "BTCUSDT": "btcusdt_1h_20230705_20251231_binance_spot_concat30m",
    "ETHUSDT": "ethusdt_1h_20230705_20251231_binance_spot_concat30m",
    "SOLUSDT": "solusdt_1h_20230705_20251231_binance_spot_concat30m",
}

LOOKBACKS = [15, 20, 30]
TRAIL_VARIANTS = [
    ("raw", []),
    ("trail40", ["--atr-trail-period", "14", "--atr-trail-mult", "4.0"]),
]
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


def run_one(asset: str, lookback: int, variant: str, extra: list) -> dict:
    ds = DATASETS_30M[asset]
    run_id = f"v2-lq-{asset.lower()}-lb{lookback}-{variant}-30m"
    args = base_args() + [
        "--run-id", run_id, "--dataset-id", ds,
        "--strategy", "liquidity_trap",
        "--lq-lookback", str(lookback),
        "--lq-exit-mean-window", "10",
        "--no-long-only",
    ] + extra
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    metrics = compute_metrics(run_id) if ok else {}
    return {"asset": asset, "lookback": lookback, "variant": variant,
            "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1), "metrics": metrics}


def main() -> int:
    jobs = [(a, lb, v, e) for a in DATASETS_30M for lb in LOOKBACKS for (v, e) in TRAIL_VARIANTS]
    print(f"[V2 LQ scout] {len(jobs)} probes (3 assets × 3 lookbacks × 2 variants), 30m, fees 10bps")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, a, lb, v, e): (a, lb, v, e) for (a, lb, v, e) in jobs}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            mt = r.get("metrics") or {}
            print(f"  {r['asset']:<8} lb{r['lookback']:>2} {r['variant']:<7} sh={mt.get('sharpe')} tr={mt.get('trades')} mdd={mt.get('mdd_pct')}% pnl={mt.get('pnl_pct')}%", flush=True)
    print(f"  wall={time.time() - t0:.0f}s")

    print(f"\n{'='*80}\nLQ scout: liquidity_trap false breakout (LQ001+LQ002 bidirectional)\n{'='*80}")
    print(f"{'Asset':<8} {'Lookback':>8} {'Variant':<7} {'Sh':>7} {'Tr':>5} {'MDD%':>6} {'PnL%':>8} | Pass60")
    n_pass = 0
    for a in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        for lb in LOOKBACKS:
            for (v, _) in TRAIL_VARIANTS:
                r = next((r for r in results if r["asset"] == a and r["lookback"] == lb and r["variant"] == v), None)
                if not r: continue
                mt = r.get("metrics") or {}
                sh, tr, mdd, pnl = mt.get("sharpe"), mt.get("trades"), mt.get("mdd_pct"), mt.get("pnl_pct")
                p = bool(sh and tr and mdd is not None and sh >= 1.0 and tr >= 30 and mdd <= 10)
                if p: n_pass += 1
                print(f"{a:<8} {lb:>8} {v:<7} {sh if sh is not None else 'NA':>7} {tr or 0:>5} "
                      f"{mdd if mdd is not None else 0:>6} {pnl if pnl is not None else 0:>8} | {p}")

    print(f"\nPadrão 60: {n_pass}/{len(results)} probes pass")
    OUT.write_text(json.dumps({"results": results, "n_pass": n_pass}, indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
