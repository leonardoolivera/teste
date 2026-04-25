"""V2 RB004 — P52 BTC 18/60 + BHDrawdownFilter cross-era retest.

Cycle 5 (ADR-0219) refutou P52 standalone cross-era em bear 2022 (drawdown 6-12%).
Hipótese: BHDrawdownFilter (Padrão 58 mitigação) bloqueia entries quando
drawdown rolling >= max_dd_pct → P52 + gate só opera em bull/recovery.

Testa P52 + bh_drawdown em 3 thresholds:
- max_dd=15% (gate apertado: bloqueia em qualquer correção moderada)
- max_dd=25% (gate moderado)
- max_dd=35% (gate frouxo: só bloqueia em bear absoluto)

Lookback fixo: 720 bars = 30 dias em 1h.

Janelas: 2022-H1, 2022-H2, 2023-H2, 2024-H1, 2024-H2 × 3 assets × 3 thresholds = 45 probes.
Fees: 10bps default V2.

Gate ADR-0030 (cross-era): em pelo menos 2 windows não-discovery (não-2024-H2),
P52+gate deve preservar Sh ≥ 1.0 em ≥ 2 assets cada.

Saída: `exports/diag/v2_rb004_p52_bh_drawdown.json`.
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
OUT = ROOT / "exports" / "diag" / "v2_rb004_p52_bh_drawdown.json"

DATASETS = {
    ("BTCUSDT", "2022-H1"): "btcusdt_1h_20220105_20220704_binance_spot",
    ("BTCUSDT", "2022-H2"): "btcusdt_1h_20220705_20221231_binance_spot",
    ("BTCUSDT", "2023-H2"): "btcusdt_1h_20230705_20231231_binance_spot",
    ("BTCUSDT", "2024-H1"): "btcusdt_1h_20240105_20240704_binance_spot",
    ("BTCUSDT", "2024-H2"): "btcusdt_1h_20240705_20241231_binance_spot",
    ("ETHUSDT", "2022-H1"): "ethusdt_1h_20220105_20220704_binance_spot",
    ("ETHUSDT", "2022-H2"): "ethusdt_1h_20220705_20221231_binance_spot",
    ("ETHUSDT", "2023-H2"): "ethusdt_1h_20230705_20231231_binance_spot",
    ("ETHUSDT", "2024-H1"): "ethusdt_1h_20240105_20240704_binance_spot",
    ("ETHUSDT", "2024-H2"): "ethusdt_1h_20240705_20241231_binance_spot",
    ("SOLUSDT", "2022-H1"): "solusdt_1h_20220105_20220704_binance_spot",
    ("SOLUSDT", "2022-H2"): "solusdt_1h_20220705_20221231_binance_spot",
    ("SOLUSDT", "2023-H2"): "solusdt_1h_20230705_20231231_binance_spot",
    ("SOLUSDT", "2024-H1"): "solusdt_1h_20240105_20240704_binance_spot",
    ("SOLUSDT", "2024-H2"): "solusdt_1h_20240705_20241231_binance_spot",
}

ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
WINDOWS = ["2022-H1", "2022-H2", "2023-H2", "2024-H1", "2024-H2"]
DD_THRESHOLDS = [15.0, 25.0, 35.0]
LOOKBACK = 720  # 30 dias em 1h
FEE_BPS = 10.0  # V2 default screening

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
        "--train-fraction", "0.5", "--min-test-bars", "50",
        "--mc-resamples", "500", "--mc-seed", "42",
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


def run_one(asset: str, window: str, dd_thresh: float) -> dict:
    ds = DATASETS[(asset, window)]
    run_id = f"v2-rb004-p52gate-{asset.lower()}-{window.lower()}-dd{int(dd_thresh)}"
    args = base_args() + [
        "--run-id", run_id, "--dataset-id", ds,
        "--strategy", "ma_crossover", "--long-only",
        "--short-window", "18", "--long-window", "60",
        "--regime-filter", f"bh_drawdown:lookback_bars={LOOKBACK}:max_dd_pct={dd_thresh}",
    ]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=600)
        ok = proc.returncode == 0
        err = proc.stderr[-500:] if not ok else ""
    except subprocess.TimeoutExpired:
        ok, err = False, "TIMEOUT"
    metrics = compute_metrics(run_id) if ok else {}
    return {"asset": asset, "window": window, "dd_thresh": dd_thresh,
            "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1),
            "metrics": metrics, "error": err if not ok else None}


def main() -> int:
    jobs = [(a, w, d) for a in ASSETS for w in WINDOWS for d in DD_THRESHOLDS]
    print(f"[V2-RB004 P52+bh_drawdown] {len(jobs)} probes (3 assets × 5 windows × 3 dd thresholds)")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, a, w, d): (a, w, d) for (a, w, d) in jobs}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            m = r.get("metrics") or {}
            sh, tr = m.get("sharpe"), m.get("trades")
            print(f"  {r['asset']:<8} {r['window']:<8} dd={r['dd_thresh']:>4.0f}% sh={sh} tr={tr}", flush=True)
    print(f"\n  wall={time.time() - t0:.0f}s")

    # Per-threshold analysis
    for dd in DD_THRESHOLDS:
        print(f"\n{'='*70}\nP52 + bh_drawdown(max_dd={dd:.0f}%) cross-era\n{'='*70}")
        print(f"{'Window':<10} {'Asset':<8} {'Sh':>7} {'Tr':>5} {'PnL%':>7} {'MDD%':>6} | Pass")
        n_pass = 0
        for w in WINDOWS:
            for a in ASSETS:
                r = next((r for r in results if r["asset"] == a and r["window"] == w and r["dd_thresh"] == dd), None)
                if not r:
                    continue
                m = r.get("metrics") or {}
                sh, tr, pnl, mdd = m.get("sharpe"), m.get("trades"), m.get("pnl_pct"), m.get("mdd_pct")
                pass_g = bool(sh is not None and tr is not None and sh >= 1.0 and tr >= 30)
                if pass_g: n_pass += 1
                print(f"{w:<10} {a:<8} {sh if sh is not None else 'NA':>7} "
                      f"{tr or 0:>5} {pnl if pnl is not None else 0:>7} {mdd if mdd is not None else 0:>6} | {pass_g}")

    # Gate ADR-0030 per threshold
    summary = []
    for dd in DD_THRESHOLDS:
        non_disc = [w for w in WINDOWS if w != "2024-H2"]
        passes_per_window = {w: [a for a in ASSETS
                                  if (r := next((r for r in results
                                                  if r["asset"] == a and r["window"] == w and r["dd_thresh"] == dd), None))
                                  and (m := r.get("metrics", {}))
                                  and m.get("sharpe", 0) >= 1.0
                                  and m.get("trades", 0) >= 30] for w in WINDOWS}
        n_windows_pass_non_disc = sum(1 for w in non_disc if len(passes_per_window[w]) >= 2)
        gate = n_windows_pass_non_disc >= 2
        summary.append({"dd_thresh": dd, "non_disc_windows_pass": n_windows_pass_non_disc, "passes_per_window": passes_per_window, "gate_adr0030": gate})

    print(f"\n{'='*70}\nGate ADR-0030 verdict per dd_threshold\n{'='*70}")
    for s in summary:
        print(f"\nmax_dd={s['dd_thresh']:.0f}%:")
        for w, p in s['passes_per_window'].items():
            mark = "DISC" if w == "2024-H2" else f"non_disc"
            print(f"  {w:<10} ({mark}): {len(p)} assets pass — {p}")
        print(f"  Non-discovery windows com >=2 assets: {s['non_disc_windows_pass']}/4")
        print(f"  Gate ADR-0030: {'PASS' if s['gate_adr0030'] else 'FAIL'}")

    OUT.write_text(json.dumps({"results": results, "summary": summary}, indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
