"""V2 — P52 + bh_drawdown gate sobre janela contínua estendida (30 meses).

Cycle 7: re-teste P52 BTC 18/60 + bh_drawdown(max_dd=25%, lookback=720) sobre
janela contínua 2023-H2..2025-H2 (21,672 bars). Resolve Padrão 59 (gate vs
sample size tradeoff): janela longa → trade count cumulativo ≥ 30 mesmo
com gate apertado.

Comparação:
- A) P52 raw sobre 30m window (sem gate)
- B) P52 + bh_drawdown(15%) — gate apertado
- C) P52 + bh_drawdown(25%) — gate moderado
- D) P52 + bh_drawdown(35%) — gate frouxo

Por asset (BTC/ETH/SOL). 3 × 4 = 12 probes em ~1-2min wall-clock.

Gate ADR-0030 reformulado para janela contínua:
- Sh ≥ 1.0 ∧ trades ≥ 30 ∧ MDD ≤ 5%
- Cobertura cross-asset: ≥ 2/3 assets pass.
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
OUT = ROOT / "exports" / "diag" / "v2_p52_gate_extended.json"

DATASETS_30M = {
    "BTCUSDT": "btcusdt_1h_20230705_20251231_binance_spot_concat30m",
    "ETHUSDT": "ethusdt_1h_20230705_20251231_binance_spot_concat30m",
    "SOLUSDT": "solusdt_1h_20230705_20251231_binance_spot_concat30m",
}

VARIANTS = [
    ("raw", None, None),
    ("dd15", 720, 15.0),
    ("dd25", 720, 25.0),
    ("dd35", 720, 35.0),
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


def run_one(asset: str, variant: str, lookback, max_dd) -> dict:
    ds = DATASETS_30M[asset]
    run_id = f"v2-p52-30m-{asset.lower()}-{variant}"
    args = base_args() + [
        "--run-id", run_id, "--dataset-id", ds,
        "--strategy", "ma_crossover", "--long-only",
        "--short-window", "18", "--long-window", "60",
    ]
    if max_dd is not None:
        args += ["--regime-filter", f"bh_drawdown:lookback_bars={lookback}:max_dd_pct={max_dd}"]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
        ok = proc.returncode == 0
        err = proc.stderr[-500:] if not ok else ""
    except subprocess.TimeoutExpired:
        ok, err = False, "TIMEOUT"
    metrics = compute_metrics(run_id) if ok else {}
    return {"asset": asset, "variant": variant, "max_dd": max_dd,
            "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1),
            "metrics": metrics, "error": err if not ok else None}


def main() -> int:
    jobs = [(a, v, lb, dd) for a in DATASETS_30M for (v, lb, dd) in VARIANTS]
    print(f"[V2 P52 + bh_drawdown extended 30m] {len(jobs)} probes (3 assets × 4 variants)")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, a, v, lb, dd): (a, v, lb, dd) for (a, v, lb, dd) in jobs}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            m = r.get("metrics") or {}
            print(f"  {r['asset']:<8} {r['variant']:<6} ok={r['ok']} sh={m.get('sharpe')} tr={m.get('trades')} mdd={m.get('mdd_pct')}% pnl={m.get('pnl_pct')}% elapsed={r['elapsed']}s", flush=True)
    print(f"\n  wall={time.time() - t0:.0f}s")

    # Print comparison table
    print(f"\n{'='*80}\nP52 BTC 18/60 sobre janela contínua 30 meses (2023-H2 -> 2025-H2)\n{'='*80}")
    print(f"{'Asset':<8} {'Variant':<7} {'Sh':>7} {'Tr':>5} {'MDD%':>6} {'PnL%':>7} {'Pass':<6}")
    n_pass_total = {}
    for a in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        for (v, lb, dd) in VARIANTS:
            r = next((r for r in results if r["asset"] == a and r["variant"] == v), None)
            if not r: continue
            m = r.get("metrics") or {}
            sh, tr, mdd, pnl = m.get("sharpe"), m.get("trades"), m.get("mdd_pct"), m.get("pnl_pct")
            # Gate ADR-0030 reformulado: Sh >= 1.0 AND tr >= 30 AND MDD <= 5%
            pass_g = bool(sh is not None and tr is not None and mdd is not None
                          and sh >= 1.0 and tr >= 30 and mdd <= 5.0)
            n_pass_total[(a, v)] = pass_g
            sh_s = f"{sh:.2f}" if sh is not None else "NA"
            mdd_s = f"{mdd:.2f}" if mdd is not None else "NA"
            pnl_s = f"{pnl:.2f}" if pnl is not None else "NA"
            print(f"{a:<8} {v:<7} {sh_s:>7} {tr or 0:>5} {mdd_s:>6} {pnl_s:>7} {pass_g}")

    # Verdict per variant
    print(f"\n{'='*80}\nGate ADR-0030 reformulado (Sh>=1.0 ∧ tr>=30 ∧ MDD<=5%) — verdict per variant\n{'='*80}")
    for (v, lb, dd) in VARIANTS:
        n_pass = sum(1 for a in ["BTCUSDT", "ETHUSDT", "SOLUSDT"] if n_pass_total.get((a, v)))
        gate = n_pass >= 2  # >= 2/3 assets
        print(f"  {v:<6} (max_dd={dd if dd else 'none':>4}): {n_pass}/3 assets pass — Gate: {'PASS' if gate else 'FAIL'}")

    OUT.write_text(json.dumps({"results": results, "passes": {f"{a}-{v}": p for (a, v), p in n_pass_total.items()}}, indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
