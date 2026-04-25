"""V2 RB012 — Sensitivity Test sobre P52-Q-001 (ma_crossover 20/50 long-only).

Promotion gate per RAIO §4 Nível 3: pequenas mudanças paramétricas não podem
destruir totalmente o edge. Padrão 52 confirmado em (BTC, SOL, ETH × 2024-H2)
+ fee resistant; agora testar perturbação local (±10-20% nos parâmetros).

Grid:
- short_window ∈ {18, 20, 22, 25}
- long_window ∈ {45, 50, 55, 60}
- assets: BTC, ETH, SOL × window 2024-H2 (regime onde P52 funciona)
- fees: 5bps (default V2 screening = 10bps mas mantém 5 pra comparar com baseline V1)

4 × 4 × 3 = 48 probes. ~3min wall-clock.

Decision RAIO §12:
- Se ≥ 70% dos vizinhos passam Sh ≥ 1.0 ∧ trades ≥ 30 → P52 → SURVIVOR (Nível 3 pass)
- Se 30-70% → P52 mantém PROMISING + investigar não-monotonicidade
- Se < 30% → P52 → QUARANTINED (sweet-spot frágil)
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
PROGRESS = ROOT / "exports" / "diag" / "v2_rb012_sensitivity_p52_progress.json"

DATASETS = {
    "BTC": "btcusdt_1h_20240705_20241231_binance_spot",
    "ETH": "ethusdt_1h_20240705_20241231_binance_spot",
    "SOL": "solusdt_1h_20240705_20241231_binance_spot",
}

SHORT_WINDOWS = [18, 20, 22, 25]
LONG_WINDOWS = [45, 50, 55, 60]
ASSETS = ["BTC", "ETH", "SOL"]
FEE_BPS = 5.0  # match V1 baseline para comparação direta com Padrão 52 V1


def base_args() -> list[str]:
    return [
        "alpha-forge", "validate",
        "--capital", "10000.0", "--fracao", "0.1", "--alavancagem", "2.0",
        "--sizing-mode", "fixed_notional",
        "--taker-fee-bps", str(FEE_BPS),
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--n-folds", "5", "--scheme", "rolling",
        "--train-fraction", "0.5", "--min-test-bars", "50",
        "--mc-resamples", "500", "--mc-seed", "42",
        "--log-level", "silent",
    ]


def annual_factor() -> float:
    import math
    return math.sqrt(24 * 365)


def compute_metrics(run_id: str) -> dict:
    import math
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
        sh = (mean / sd) * annual_factor() if sd > 0 else 0.0
    else:
        sh = 0.0
    return {"trades": n_trades, "sharpe": round(sh, 4), "pnl_pct": round(pnl, 4), "final_eq": round(final, 2)}


def run_one(asset: str, short: int, long_: int) -> dict:
    if short >= long_:
        return {"asset": asset, "short": short, "long": long_, "ok": False, "skip": "short>=long"}
    run_id = f"v2-rb012-p52-ma{short}-{long_}-{asset.lower()}-2024h2"
    args = base_args() + [
        "--run-id", run_id,
        "--dataset-id", DATASETS[asset],
        "--strategy", "ma_crossover", "--long-only",
        "--short-window", str(short), "--long-window", str(long_),
    ]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=600)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    metrics = compute_metrics(run_id) if ok else {}
    return {"asset": asset, "short": short, "long": long_, "run_id": run_id, "ok": ok,
            "elapsed_s": round(time.time() - t0, 1), "metrics": metrics}


def main() -> int:
    jobs = [(a, s, l) for a in ASSETS for s in SHORT_WINDOWS for l in LONG_WINDOWS if s < l]
    print(f"[V2-RB012 P52 Sensitivity] total jobs: {len(jobs)}")
    progress = {}
    if PROGRESS.exists():
        progress = json.loads(PROGRESS.read_text())
    todo = [(a, s, l) for (a, s, l) in jobs if f"{a}-{s}-{l}" not in progress]
    print(f"  done: {len(progress)} | todo: {len(todo)}")
    if not todo:
        return 0

    t0 = time.time()
    n_done = 0
    n_pass = 0
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, a, s, l): (a, s, l) for (a, s, l) in todo}
        for fut in as_completed(futs):
            r = fut.result()
            progress[f"{r['asset']}-{r['short']}-{r['long']}"] = r
            PROGRESS.write_text(json.dumps(progress, indent=2, default=str))
            n_done += 1
            m = r.get("metrics") or {}
            sh, tr = m.get("sharpe"), m.get("trades")
            gate = bool(sh and tr and sh >= 1.0 and tr >= 30)
            if gate: n_pass += 1
            print(f"[{n_done}/{len(todo)}] P52-MA{r['short']}/{r['long']} {r['asset']:<3} sh={sh} tr={tr} pass={gate}", flush=True)
    print(f"\nDONE wall={time.time() - t0:.0f}s pass={n_pass}/{n_done}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
