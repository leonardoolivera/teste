"""V2 RB007 — Fee stress sobre os 13 combos do stack canonical aprovado.

Re-roda cada combo do stack 13 (extraído de exports/approved/*.json) com 3 níveis
de fees: 5bps (V1 default), 10bps (2x), 15bps (3x). Detecta combos fee-fragile
análogos ao Padrão 50 — V1 promoveu manifests com fees=5bps; V2 audita.

Total: 13 combos × 3 fees = 39 probes. ~3-5min wall-clock.

Saída: `exports/diag/v2_rb007_stack13_fee_stress.json`.
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
PROGRESS = ROOT / "exports" / "diag" / "v2_rb007_stack13_progress.json"

DATASETS = {
    ("BTCUSDT", "2024-H1"): "btcusdt_1h_20240105_20240704_binance_spot",
    ("BTCUSDT", "2024-H2"): "btcusdt_1h_20240705_20241231_binance_spot",
    ("BTCUSDT", "2025-H1"): "btcusdt_1h_20250105_20250704_binance_spot",
    ("BTCUSDT", "2025-H2"): "btcusdt_1h_20250705_20251231_binance_spot",
    ("ETHUSDT", "2024-H1"): "ethusdt_1h_20240105_20240704_binance_spot",
    ("ETHUSDT", "2024-H2"): "ethusdt_1h_20240705_20241231_binance_spot",
    ("ETHUSDT", "2025-H1"): "ethusdt_1h_20250105_20250704_binance_spot",
    ("ETHUSDT", "2025-H2"): "ethusdt_1h_20250705_20251231_binance_spot",
    ("SOLUSDT", "2024-H2"): "solusdt_1h_20240705_20241231_binance_spot",
    ("SOLUSDT", "2025-H1"): "solusdt_1h_20250105_20250704_binance_spot",
    ("SOLUSDT", "2025-H2"): "solusdt_1h_20250705_20251231_binance_spot",
}

# 13 combos do stack canonical (de fixed_100_stack13_20260422.json + approved manifests)
STACK_13 = [
    # bollinger_width_regime_v2 long (4 combos)
    {"id": "S01", "manifest": "bollinger_width_regime_v2", "symbol": "ETHUSDT", "window": "2024-H1",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5"],
     "long_only": True, "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    {"id": "S02", "manifest": "bollinger_width_regime_v2", "symbol": "ETHUSDT", "window": "2025-H1",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5"],
     "long_only": True, "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    {"id": "S03", "manifest": "bollinger_width_regime_v2", "symbol": "BTCUSDT", "window": "2024-H2",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5"],
     "long_only": True, "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    {"id": "S04", "manifest": "bollinger_width_regime_v2", "symbol": "SOLUSDT", "window": "2024-H2",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5"],
     "long_only": True, "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    # bollinger_short_width (4 combos)
    {"id": "S05", "manifest": "bollinger_short_width", "symbol": "SOLUSDT", "window": "2024-H2",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5"],
     "long_only": False, "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S06", "manifest": "bollinger_short_width", "symbol": "BTCUSDT", "window": "2025-H1",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5"],
     "long_only": False, "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S07", "manifest": "bollinger_short_width", "symbol": "ETHUSDT", "window": "2025-H1",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5"],
     "long_only": False, "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S08", "manifest": "bollinger_short_width", "symbol": "SOLUSDT", "window": "2025-H1",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5"],
     "long_only": False, "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    # rsi_long_width_eth_2024h2 (1 combo)
    {"id": "S09", "manifest": "rsi_long_width_eth_2024h2", "symbol": "ETHUSDT", "window": "2024-H2",
     "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70"],
     "long_only": True, "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    # rsi_short_pure_2025h2 (2 combos)
    {"id": "S10", "manifest": "rsi_short_pure_2025h2", "symbol": "BTCUSDT", "window": "2025-H2",
     "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70"],
     "long_only": False, "regime": None},
    {"id": "S11", "manifest": "rsi_short_pure_2025h2", "symbol": "SOLUSDT", "window": "2025-H2",
     "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70"],
     "long_only": False, "regime": None},
    # rsi_short_trendhtf_sol_2025h1 (1 combo)
    {"id": "S12", "manifest": "rsi_short_trendhtf_sol_2025h1", "symbol": "SOLUSDT", "window": "2025-H1",
     "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "25", "--rsi-overbought", "75"],
     "long_only": False, "regime": "trend_htf:htf=4h:sma_window=50:mode=short_only"},
    # rsi_short_width_2025h1 (1 combo - BTCUSDT only per fixed_100 stack)
    {"id": "S13", "manifest": "rsi_short_width_2025h1", "symbol": "BTCUSDT", "window": "2025-H1",
     "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70"],
     "long_only": False, "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
]

FEE_LEVELS = [(5.0, "5bps"), (10.0, "10bps"), (15.0, "15bps")]


def base_args(fee_bps: float) -> list[str]:
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


def annual_factor() -> float:
    import math
    return math.sqrt(24 * 365)  # 1h all combos


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
    # MDD
    peak = full_eq[0]
    mdd = 0.0
    for v in full_eq:
        if v > peak: peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > mdd: mdd = dd
    return {"trades": n_trades, "sharpe": round(sh, 4), "pnl_pct": round(pnl, 4), "mdd_pct": round(mdd * 100, 4), "final_eq": round(final, 2)}


def run_one(combo: dict, fee_bps: float, fee_label: str) -> dict:
    ds = DATASETS[(combo["symbol"], combo["window"])]
    run_id = f"v2-rb007-{combo['id'].lower()}-{combo['symbol'].lower()}-{combo['window'].lower()}-{fee_label}"
    extra = list(combo["engine_args"])
    # CLI default is --long-only=True; precisamos --no-long-only para SHORT.
    extra.append("--long-only" if combo["long_only"] else "--no-long-only")
    args = base_args(fee_bps) + ["--run-id", run_id, "--dataset-id", ds] + extra
    if combo["regime"]:
        args += ["--regime-filter", combo["regime"]]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=600)
        ok = proc.returncode == 0
        err = proc.stderr[-500:] if not ok else ""
    except subprocess.TimeoutExpired:
        ok, err = False, "TIMEOUT"
    metrics = compute_metrics(run_id) if ok else {}
    return {"combo_id": combo["id"], "manifest": combo["manifest"], "symbol": combo["symbol"],
            "window": combo["window"], "fee_bps": fee_bps, "fee_label": fee_label, "run_id": run_id,
            "ok": ok, "elapsed_s": round(time.time() - t0, 1), "metrics": metrics, "error": err if not ok else None}


def main() -> int:
    jobs = [(c, fee, lbl) for c in STACK_13 for fee, lbl in FEE_LEVELS]
    print(f"[V2-RB007 stack13] total jobs: {len(jobs)} (13 combos × 3 fee levels)")
    progress = {}
    if PROGRESS.exists():
        progress = json.loads(PROGRESS.read_text())
    todo = [(c, f, l) for (c, f, l) in jobs if f"{c['id']}-{l}" not in progress]
    print(f"  done: {len(progress)} | todo: {len(todo)}")

    t0 = time.time()
    n_done = 0
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, c, f, l): (c, f, l) for (c, f, l) in todo}
        for fut in as_completed(futs):
            r = fut.result()
            progress[f"{r['combo_id']}-{r['fee_label']}"] = r
            PROGRESS.write_text(json.dumps(progress, indent=2, default=str))
            n_done += 1
            m = r.get("metrics") or {}
            sh, tr = m.get("sharpe"), m.get("trades")
            print(f"[{n_done}/{len(todo)}] {r['combo_id']:<4} {r['manifest'][:30]:<30} {r['symbol']:<8} {r['window']:<8} "
                  f"fee={r['fee_label']:<6} sh={sh} tr={tr} elapsed={r['elapsed_s']}s", flush=True)
    print(f"\nDONE wall={time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
