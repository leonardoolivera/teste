"""V2 RB004 + RB007 — Cross-era + fee stress validation dos winners V1.

Ataca Padrões 50/51/52 quarentinados (single-window risk):
- Padrão 50: bear-avoidance trend ETH 2025-H1 (5 configs supertrend/ma_crossover)
- Padrão 51: bollinger short-window ETH 2024-H2 (3 configs window=15-17)
- Padrão 52: ma_crossover canonical 20/50 ETH 2024-H2 (1 config)

Cada config replica em:
- RB004 cross-era: outras windows mesmas/outras assets (BTC, SOL, ETH × outras 2024/2025 windows)
- RB007 fee stress: mesma config baseline com taker-fee-bps=10 (2x) e 15 (3x)

Total estimado: 9 configs × (5 cross-era windows + 2 fee stress) = 63 probes ≈ 5-10min wall-clock.

Saída: `exports/diag/v2_rb004_rb007_validation.json` + `exports/diag/v2_rb004_rb007_progress.json`.
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
PROGRESS = ROOT / "exports" / "diag" / "v2_rb004_rb007_progress.json"

DATASETS = {
    "BTC": {
        "2024-H2": "btcusdt_1h_20240705_20241231_binance_spot",
        "2025-H1": "btcusdt_1h_20250105_20250704_binance_spot",
        "2025-H2": "btcusdt_1h_20250705_20251231_binance_spot",
        "10m-2024-H2": "btcusdt_10m_20240705_20241231_binance_spot_resampled",
        "10m-2025-H1": "btcusdt_10m_20250105_20250704_binance_spot_resampled",
        "10m-2025-H2": "btcusdt_10m_20250705_20251231_binance_spot_resampled",
    },
    "ETH": {
        "2024-H2": "ethusdt_1h_20240705_20241231_binance_spot",
        "2025-H1": "ethusdt_1h_20250105_20250704_binance_spot",
        "2025-H2": "ethusdt_1h_20250705_20251231_binance_spot",
        "10m-2024-H2": "ethusdt_10m_20240705_20241231_binance_spot_resampled",
        "10m-2025-H1": "ethusdt_10m_20250105_20250704_binance_spot_resampled",
        "10m-2025-H2": "ethusdt_10m_20250705_20251231_binance_spot_resampled",
    },
    "SOL": {
        "2024-H2": "solusdt_1h_20240705_20241231_binance_spot",
        "2025-H1": "solusdt_1h_20250105_20250704_binance_spot",
        "2025-H2": "solusdt_1h_20250705_20251231_binance_spot",
        "10m-2024-H2": "solusdt_10m_20240705_20241231_binance_spot_resampled",
        "10m-2025-H1": "solusdt_10m_20250105_20250704_binance_spot_resampled",
        "10m-2025-H2": "solusdt_10m_20250705_20251231_binance_spot_resampled",
    },
}


def base_args(fee_bps: float = 5.0) -> list[str]:
    return [
        "alpha-forge", "validate",
        "--capital", "10000.0", "--fracao", "0.1", "--alavancagem", "2.0",
        "--sizing-mode", "fixed_notional",
        "--taker-fee-bps", str(fee_bps),
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--n-folds", "5", "--scheme", "rolling",
        "--train-fraction", "0.5", "--min-test-bars", "50",
        "--mc-resamples", "500", "--mc-seed", "42",
        "--log-level", "silent",
    ]


# === V1 winners (Padrões 50, 51, 52) ===
P50_CONFIGS = [
    # supertrend ETH 2025-H1 (3 configs)
    {"node": "P50-001", "engine_args": ["--strategy", "supertrend", "--supertrend-atr-period", "14", "--supertrend-atr-mult", "3.0"], "engine": "supertrend", "params": "atr_period=14,atr_mult=3.0"},
    {"node": "P50-002", "engine_args": ["--strategy", "supertrend", "--supertrend-atr-period", "14", "--supertrend-atr-mult", "3.5"], "engine": "supertrend", "params": "atr_period=14,atr_mult=3.5"},
    {"node": "P50-003", "engine_args": ["--strategy", "supertrend", "--supertrend-atr-period", "20", "--supertrend-atr-mult", "3.5"], "engine": "supertrend", "params": "atr_period=20,atr_mult=3.5"},
    # ma_crossover ETH 2025-H1 (2 configs)
    {"node": "P50-004", "engine_args": ["--strategy", "ma_crossover", "--long-only", "--short-window", "20", "--long-window", "50"], "engine": "ma_crossover", "params": "20/50"},
    {"node": "P50-005", "engine_args": ["--strategy", "ma_crossover", "--long-only", "--short-window", "25", "--long-window", "75"], "engine": "ma_crossover", "params": "25/75"},
]
P51_CONFIGS = [
    {"node": "P51-001", "engine_args": ["--strategy", "bollinger", "--bollinger-window", "15", "--bollinger-num-std", "2.0"], "engine": "bollinger", "params": "15/2.0"},
    {"node": "P51-002", "engine_args": ["--strategy", "bollinger", "--bollinger-window", "17", "--bollinger-num-std", "2.0"], "engine": "bollinger", "params": "17/2.0"},
    {"node": "P51-003", "engine_args": ["--strategy", "bollinger", "--bollinger-window", "15", "--bollinger-num-std", "1.75"], "engine": "bollinger", "params": "15/1.75"},
]
P52_CONFIGS = [
    {"node": "P52-001", "engine_args": ["--strategy", "ma_crossover", "--long-only", "--short-window", "20", "--long-window", "50"], "engine": "ma_crossover", "params": "20/50"},
]

# === RB004 cross-era windows + RB007 fee stress per config ===
# P50 winners are 1h ETH 2025-H1 — replicar em outras 1h windows + outras assets
P50_REPLICATE_WINDOWS = [("ETH", "2024-H2"), ("ETH", "2025-H2"),
                          ("BTC", "2025-H1"), ("BTC", "2025-H2"),
                          ("SOL", "2025-H1"), ("SOL", "2025-H2")]
# P51/52 winners are 1h ETH 2024-H2 — replicar em outras 1h windows + outras assets
P51_52_REPLICATE_WINDOWS = [("ETH", "2025-H1"), ("ETH", "2025-H2"),
                             ("BTC", "2024-H2"), ("BTC", "2025-H1"),
                             ("SOL", "2024-H2"), ("SOL", "2025-H1")]


def build_jobs() -> list[dict]:
    jobs = []
    # P50 cross-era (ETH 2025-H1 baseline)
    for cfg in P50_CONFIGS:
        for asset, window in P50_REPLICATE_WINDOWS:
            ds = DATASETS[asset][window]
            run_id = f"v2-rb004-{cfg['node'].lower()}-{asset.lower()}-{window.lower()}"
            jobs.append({"run_id": run_id, "node": cfg["node"], "kind": "RB004", "asset": asset, "window": window,
                         "engine": cfg["engine"], "params": cfg["params"], "engine_args": cfg["engine_args"], "ds": ds, "fee_bps": 5.0})
    # P50 fee stress (ETH 2025-H1 baseline winning window, 2x and 3x fees)
    for cfg in P50_CONFIGS:
        ds = DATASETS["ETH"]["2025-H1"]
        for fee_mult, fee in [(2, 10.0), (3, 15.0)]:
            run_id = f"v2-rb007-{cfg['node'].lower()}-eth-2025-h1-fee{fee_mult}x"
            jobs.append({"run_id": run_id, "node": cfg["node"], "kind": f"RB007-fee{fee_mult}x", "asset": "ETH", "window": "2025-H1",
                         "engine": cfg["engine"], "params": cfg["params"], "engine_args": cfg["engine_args"], "ds": ds, "fee_bps": fee})
    # P51 cross-era (ETH 2024-H2 baseline)
    for cfg in P51_CONFIGS:
        for asset, window in P51_52_REPLICATE_WINDOWS:
            ds = DATASETS[asset][window]
            run_id = f"v2-rb004-{cfg['node'].lower()}-{asset.lower()}-{window.lower()}"
            jobs.append({"run_id": run_id, "node": cfg["node"], "kind": "RB004", "asset": asset, "window": window,
                         "engine": cfg["engine"], "params": cfg["params"], "engine_args": cfg["engine_args"], "ds": ds, "fee_bps": 5.0})
    # P51 fee stress
    for cfg in P51_CONFIGS:
        ds = DATASETS["ETH"]["2024-H2"]
        for fee_mult, fee in [(2, 10.0), (3, 15.0)]:
            run_id = f"v2-rb007-{cfg['node'].lower()}-eth-2024-h2-fee{fee_mult}x"
            jobs.append({"run_id": run_id, "node": cfg["node"], "kind": f"RB007-fee{fee_mult}x", "asset": "ETH", "window": "2024-H2",
                         "engine": cfg["engine"], "params": cfg["params"], "engine_args": cfg["engine_args"], "ds": ds, "fee_bps": fee})
    # P52 cross-era + fee stress
    for cfg in P52_CONFIGS:
        for asset, window in P51_52_REPLICATE_WINDOWS:
            ds = DATASETS[asset][window]
            run_id = f"v2-rb004-{cfg['node'].lower()}-{asset.lower()}-{window.lower()}"
            jobs.append({"run_id": run_id, "node": cfg["node"], "kind": "RB004", "asset": asset, "window": window,
                         "engine": cfg["engine"], "params": cfg["params"], "engine_args": cfg["engine_args"], "ds": ds, "fee_bps": 5.0})
        ds = DATASETS["ETH"]["2024-H2"]
        for fee_mult, fee in [(2, 10.0), (3, 15.0)]:
            run_id = f"v2-rb007-{cfg['node'].lower()}-eth-2024-h2-fee{fee_mult}x"
            jobs.append({"run_id": run_id, "node": cfg["node"], "kind": f"RB007-fee{fee_mult}x", "asset": "ETH", "window": "2024-H2",
                         "engine": cfg["engine"], "params": cfg["params"], "engine_args": cfg["engine_args"], "ds": ds, "fee_bps": fee})
    return jobs


def annual_factor(ds_id: str) -> float:
    import math
    if "_10m_" in ds_id: return math.sqrt(144 * 365)
    return math.sqrt(24 * 365)


def compute_metrics(run_id: str, ds_id: str) -> dict:
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
        sh = (mean / sd) * annual_factor(ds_id) if sd > 0 else 0.0
    else:
        sh = 0.0
    return {"trades": n_trades, "sharpe": round(sh, 4), "pnl_pct": round(pnl, 4), "final_eq": round(final, 2)}


def run_one(job: dict) -> dict:
    argv = base_args(job["fee_bps"]) + ["--run-id", job["run_id"], "--dataset-id", job["ds"]] + job["engine_args"]
    code = f"import sys; sys.argv = {argv!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=1800)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    dt = time.time() - t0
    metrics = compute_metrics(job["run_id"], job["ds"]) if ok else {}
    return {**job, "ok": ok, "elapsed_s": round(dt, 1), "metrics": metrics}


def main() -> int:
    jobs = build_jobs()
    print(f"[V2-RB004/RB007] total jobs: {len(jobs)}")
    progress = {}
    if PROGRESS.exists():
        progress = json.loads(PROGRESS.read_text())
    todo = [j for j in jobs if j["run_id"] not in progress]
    print(f"  done: {len(progress)} | todo: {len(todo)}")
    if not todo:
        print("  nada a fazer.")
        return 0

    t0 = time.time()
    n_done = 0
    n_pass_v2 = 0  # gate V2: Sh >= 1.0 + trades >= 30 (mais restrito que V1 1.5)
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, j): j for j in todo}
        for fut in as_completed(futs):
            r = fut.result()
            progress[r["run_id"]] = r
            PROGRESS.write_text(json.dumps(progress, indent=2, default=str))
            n_done += 1
            m = r.get("metrics") or {}
            sh, tr = m.get("sharpe"), m.get("trades")
            gate_v2 = bool(sh and tr and sh >= 1.0 and tr >= 30)
            if gate_v2:
                n_pass_v2 += 1
            print(f"[{n_done}/{len(todo)}] {r['kind']:<14} {r['node']:<8} {r['asset']:<3} {r['window']:<8} "
                  f"sh={sh} tr={tr} pass_v2={gate_v2} elapsed={r['elapsed_s']}s", flush=True)
    print(f"\nDONE wall={time.time() - t0:.0f}s  pass_v2={n_pass_v2}/{n_done}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
