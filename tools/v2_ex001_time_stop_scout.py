"""V2 Cycle 11 — EX001 Scout: time stop curto melhora MR (RAIO Nível 1).

Hipótese V2 EX001 (Top 6 V2): MR (bollinger canonical) que não reverte rápido
tende a virar drift adverso. Time stop curto (6/12/24 bars) deve melhorar
expectancy ao cortar trades quebrados antes de stop maior do signal natural.

Configs:
- Baseline: bollinger 20/2.0 long_only sobre 30m (3 assets)
- Variants: + time_stop_bars ∈ {6, 12, 24, 48}

3 assets × 5 variants (raw + 4 ts) = 15 probes em ~3min wall-clock.

Gate Padrão 60: Sh ≥ 1.0 ∧ trades ≥ 30 ∧ MDD ≤ 10%.

Decision RAIO Nível 1 Scout: se variant time_stop melhora Sharpe sem destruir
trade count em ≥2 assets → EXPAND para Nível 2 Replication.
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
OUT = ROOT / "exports" / "diag" / "v2_ex001_time_stop_scout.json"

DATASETS_30M = {
    "BTCUSDT": "btcusdt_1h_20230705_20251231_binance_spot_concat30m",
    "ETHUSDT": "ethusdt_1h_20230705_20251231_binance_spot_concat30m",
    "SOLUSDT": "solusdt_1h_20230705_20251231_binance_spot_concat30m",
}

VARIANTS = [
    ("raw", 0),
    ("ts06", 6),
    ("ts12", 12),
    ("ts24", 24),
    ("ts48", 48),
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


def run_one(asset: str, variant: str, ts_bars: int) -> dict:
    ds = DATASETS_30M[asset]
    run_id = f"v2-ex001-{asset.lower()}-{variant}-30m"
    args = base_args() + [
        "--run-id", run_id, "--dataset-id", ds,
        "--strategy", "bollinger",
        "--bollinger-window", "20", "--bollinger-num-std", "2.0",
        "--long-only",
        "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=250",
    ]
    if ts_bars > 0:
        args += ["--time-stop-bars", str(ts_bars)]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    metrics = compute_metrics(run_id) if ok else {}
    return {"asset": asset, "variant": variant, "ts_bars": ts_bars,
            "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1), "metrics": metrics}


def main() -> int:
    jobs = [(a, v, ts) for a in DATASETS_30M for (v, ts) in VARIANTS]
    print(f"[V2 EX001 time stop scout] {len(jobs)} probes (3 assets × 5 variants), 30m window, fees 10bps")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, a, v, ts): (a, v, ts) for (a, v, ts) in jobs}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            m = r.get("metrics") or {}
            print(f"  {r['asset']:<8} {r['variant']:<6} sh={m.get('sharpe')} tr={m.get('trades')} mdd={m.get('mdd_pct')}% pnl={m.get('pnl_pct')}% elapsed={r['elapsed']}s", flush=True)
    print(f"  wall={time.time() - t0:.0f}s")

    print(f"\n{'='*80}\nEX001 Scout: bollinger 20/2.0 long_only + width filter + time_stop variants\n{'='*80}")
    print(f"{'Asset':<8} {'Variant':<6} {'Sh':>7} {'Tr':>5} {'MDD%':>6} {'PnL%':>8} | Pass")
    for a in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        for (v, ts) in VARIANTS:
            r = next((r for r in results if r["asset"] == a and r["variant"] == v), None)
            if not r: continue
            m = r.get("metrics") or {}
            sh, tr, mdd, pnl = m.get("sharpe"), m.get("trades"), m.get("mdd_pct"), m.get("pnl_pct")
            pass_g = bool(sh is not None and tr is not None and mdd is not None
                          and sh >= 1.0 and tr >= 30 and mdd <= 10)
            print(f"{a:<8} {v:<6} {sh if sh is not None else 'NA':>7} {tr or 0:>5} "
                  f"{mdd if mdd is not None else 0:>6} {pnl if pnl is not None else 0:>8} | {pass_g}")

    # Per-variant summary: how many assets pass
    print(f"\n{'='*80}\nPer-variant pass count\n{'='*80}")
    for (v, ts) in VARIANTS:
        n_pass = sum(1 for r in results if r["variant"] == v and (m := r.get("metrics", {}))
                     and (m.get("sharpe", 0) or 0) >= 1.0 and (m.get("trades", 0) or 0) >= 30
                     and (m.get("mdd_pct", 100) or 100) <= 10)
        print(f"  {v:<6}: {n_pass}/3 assets pass")

    OUT.write_text(json.dumps({"results": results}, indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
