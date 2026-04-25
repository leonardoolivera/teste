"""V2 Cycle 14 — EX009 BE-after-MFE scout + cumulative S12+trail40+BE.

EX009 standalone (S12 base):
- raw, BE 0.5×ATR, BE 1.0×ATR, BE 1.5×ATR sobre 3 assets = 12 probes.

EX009 cumulative (S12+trail40+BE), apenas SOL (único survivor):
- S12 raw (baseline Cycle 13)
- S12 + trail40 (Cycle 13 best: Sh=1.37)
- S12 + trail40 + BE 0.5
- S12 + trail40 + BE 1.0
- S12 + trail40 + BE 1.5

Total: 12 + 5 = 17 probes, ~5min wall-clock.

Decision RAIO Nível 5:
- Se cumulative atinge Sh ≥ 1.5 → S12+trail40+BE = primeira candidate-for-manifest V2.
- Se Sh entre 1.37 e 1.5 → S12 + trail + BE → PROMISING+; ADR-0230 propõe gate-relax discussion.
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
OUT = ROOT / "exports" / "diag" / "v2_ex009_be_combined.json"

DATASETS_30M = {
    "BTCUSDT": "btcusdt_1h_20230705_20251231_binance_spot_concat30m",
    "ETHUSDT": "ethusdt_1h_20230705_20251231_binance_spot_concat30m",
    "SOLUSDT": "solusdt_1h_20230705_20251231_binance_spot_concat30m",
}

S12_ENGINE_ARGS = [
    "--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "25", "--rsi-overbought", "75", "--no-long-only",
]
S12_REGIME = "trend_htf:htf=4h:sma_window=50:mode=short_only"

# Standalone (S12 base + BE only) variants — 4
STANDALONE_VARIANTS = [
    ("raw", []),
    ("be05", ["--be-atr-period", "14", "--be-mfe-trigger-atr", "0.5"]),
    ("be10", ["--be-atr-period", "14", "--be-mfe-trigger-atr", "1.0"]),
    ("be15", ["--be-atr-period", "14", "--be-mfe-trigger-atr", "1.5"]),
]

# Cumulative (S12+trail40+BE) variants — only SOL — 5
CUMULATIVE_VARIANTS_SOL = [
    ("cum_raw", []),
    ("cum_t40", ["--atr-trail-period", "14", "--atr-trail-mult", "4.0"]),
    ("cum_t40_be05", ["--atr-trail-period", "14", "--atr-trail-mult", "4.0", "--be-atr-period", "14", "--be-mfe-trigger-atr", "0.5"]),
    ("cum_t40_be10", ["--atr-trail-period", "14", "--atr-trail-mult", "4.0", "--be-atr-period", "14", "--be-mfe-trigger-atr", "1.0"]),
    ("cum_t40_be15", ["--atr-trail-period", "14", "--atr-trail-mult", "4.0", "--be-atr-period", "14", "--be-mfe-trigger-atr", "1.5"]),
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


def run_one(asset: str, variant: str, extra_args: list[str], category: str) -> dict:
    ds = DATASETS_30M[asset]
    run_id = f"v2-ex009-{category}-{asset.lower()}-{variant}-30m"
    args = base_args() + ["--run-id", run_id, "--dataset-id", ds] + S12_ENGINE_ARGS + ["--regime-filter", S12_REGIME] + extra_args
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    metrics = compute_metrics(run_id) if ok else {}
    return {"asset": asset, "variant": variant, "category": category,
            "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1), "metrics": metrics}


def main() -> int:
    jobs = []
    for a in DATASETS_30M:
        for (v, ea) in STANDALONE_VARIANTS:
            jobs.append((a, v, ea, "standalone"))
    for (v, ea) in CUMULATIVE_VARIANTS_SOL:
        jobs.append(("SOLUSDT", v, ea, "cumulative"))

    print(f"[V2 EX009 BE scout] {len(jobs)} probes (12 standalone + 5 cumulative SOL)")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, a, v, ea, c): (a, v, ea, c) for (a, v, ea, c) in jobs}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            mt = r.get("metrics") or {}
            print(f"  {r['category']:<11} {r['asset']:<8} {r['variant']:<14} sh={mt.get('sharpe')} tr={mt.get('trades')} mdd={mt.get('mdd_pct')}% pnl={mt.get('pnl_pct')}% el={r['elapsed']}s", flush=True)
    print(f"  wall={time.time() - t0:.0f}s")

    print(f"\n{'='*80}\nEX009 standalone (S12 + BE only)\n{'='*80}")
    print(f"{'Asset':<8} {'Variant':<6} {'Sh':>7} {'Tr':>5} {'MDD%':>6} {'PnL%':>8} | Pass60 | Pass15")
    for a in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        for (v, _) in STANDALONE_VARIANTS:
            r = next((r for r in results if r["asset"] == a and r["variant"] == v and r["category"] == "standalone"), None)
            if not r: continue
            mt = r.get("metrics") or {}
            sh, tr, mdd, pnl = mt.get("sharpe"), mt.get("trades"), mt.get("mdd_pct"), mt.get("pnl_pct")
            p60 = bool(sh and tr and mdd is not None and sh >= 1.0 and tr >= 30 and mdd <= 10)
            p15 = bool(sh and tr and mdd is not None and sh >= 1.5 and tr >= 30 and mdd <= 10)
            print(f"{a:<8} {v:<6} {sh if sh is not None else 'NA':>7} {tr or 0:>5} "
                  f"{mdd if mdd is not None else 0:>6} {pnl if pnl is not None else 0:>8} | {p60} | {p15}")

    print(f"\n{'='*80}\nEX009 cumulative SOL (S12 + trail40 + BE)\n{'='*80}")
    print(f"{'Variant':<14} {'Sh':>7} {'Tr':>5} {'MDD%':>6} {'PnL%':>8} | Pass60 | Pass15")
    for (v, _) in CUMULATIVE_VARIANTS_SOL:
        r = next((r for r in results if r["asset"] == "SOLUSDT" and r["variant"] == v and r["category"] == "cumulative"), None)
        if not r: continue
        mt = r.get("metrics") or {}
        sh, tr, mdd, pnl = mt.get("sharpe"), mt.get("trades"), mt.get("mdd_pct"), mt.get("pnl_pct")
        p60 = bool(sh and tr and mdd is not None and sh >= 1.0 and tr >= 30 and mdd <= 10)
        p15 = bool(sh and tr and mdd is not None and sh >= 1.5 and tr >= 30 and mdd <= 10)
        print(f"{v:<14} {sh if sh is not None else 'NA':>7} {tr or 0:>5} "
              f"{mdd if mdd is not None else 0:>6} {pnl if pnl is not None else 0:>8} | {p60} | {p15}")

    OUT.write_text(json.dumps({"results": results}, indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
