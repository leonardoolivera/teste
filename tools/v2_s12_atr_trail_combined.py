"""V2 Cycle 13 — S12 + EX004 ATR trail (Padrão 65 application).

S12 (rsi_short_trendhtf SOL 2025-H1) é único survivor V2/RAIO sob Padrão 60:
SOL Sh=1.20, MDD=9.0%, PnL=+29% sobre janela contínua 30m.

Padrão 65 (Cycle 12): ATR trail mult≥4.0 melhora Sh sem destruir trades em base
strategies sem edge. Testar se aplicação a S12 (com edge real) **promove**
para Sh ≥ 1.5 (gate V1 strict).

Configs (todos sobre janela contínua SOL 30m, fees 10bps):
- raw S12 (baseline = Cycle 9 result Sh=1.20)
- S12 + atr_trail(14, 2.5)
- S12 + atr_trail(14, 4.0)
- S12 + atr_trail(14, 6.0) — extra frouxo

Bonus: testar também em BTC e ETH (S12 cross-asset confirmou FAIL standalone;
atr_trail pode salvar?)

3 assets × 4 variants = 12 probes em ~3min wall-clock.

Decision RAIO Nível 5 Portfolio:
- Se SOL S12 + trail atinge Sh ≥ 1.5 → primeira candidate-for-manifest V2.
- Se BTC/ETH + trail atinge Sh ≥ 1.0 → S12 generaliza cross-asset com trail (não-óbvio).
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
OUT = ROOT / "exports" / "diag" / "v2_s12_atr_trail_combined.json"

DATASETS_30M = {
    "BTCUSDT": "btcusdt_1h_20230705_20251231_binance_spot_concat30m",
    "ETHUSDT": "ethusdt_1h_20230705_20251231_binance_spot_concat30m",
    "SOLUSDT": "solusdt_1h_20230705_20251231_binance_spot_concat30m",
}

VARIANTS = [
    ("raw", 0, 0.0),
    ("trail25", 14, 2.5),
    ("trail40", 14, 4.0),
    ("trail60", 14, 6.0),
]

S12_ENGINE_ARGS = [
    "--strategy", "rsi",
    "--rsi-period", "14",
    "--rsi-oversold", "25",
    "--rsi-overbought", "75",
    "--no-long-only",
]
S12_REGIME = "trend_htf:htf=4h:sma_window=50:mode=short_only"
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
    return {"trades": n_trades, "sharpe": round(sh, 4), "pnl_pct": round(pnl, 4), "mdd_pct": round(mdd * 100, 4), "final_eq": round(final, 2)}


def run_one(asset: str, variant: str, period: int, mult: float) -> dict:
    ds = DATASETS_30M[asset]
    run_id = f"v2-s12-trail-{asset.lower()}-{variant}-30m"
    args = base_args() + [
        "--run-id", run_id, "--dataset-id", ds,
    ] + S12_ENGINE_ARGS + ["--regime-filter", S12_REGIME]
    if period > 0 and mult > 0:
        args += ["--atr-trail-period", str(period), "--atr-trail-mult", str(mult)]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    metrics = compute_metrics(run_id) if ok else {}
    return {"asset": asset, "variant": variant, "period": period, "mult": mult,
            "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1), "metrics": metrics}


def main() -> int:
    jobs = [(a, v, p, m) for a in DATASETS_30M for (v, p, m) in VARIANTS]
    print(f"[V2 S12+trail] {len(jobs)} probes (3 assets × 4 variants), 30m, fees 10bps")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, a, v, p, m): (a, v, p, m) for (a, v, p, m) in jobs}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            mt = r.get("metrics") or {}
            print(f"  {r['asset']:<8} {r['variant']:<8} sh={mt.get('sharpe')} tr={mt.get('trades')} mdd={mt.get('mdd_pct')}% pnl={mt.get('pnl_pct')}%", flush=True)
    print(f"  wall={time.time() - t0:.0f}s")

    print(f"\n{'='*80}\nS12 (rsi_short_trendhtf) + ATR trail variants — janela contínua 30m\n{'='*80}")
    print(f"{'Asset':<8} {'Variant':<8} {'Sh':>7} {'Tr':>5} {'MDD%':>6} {'PnL%':>8} | Pass60 | Pass15 (V1)")
    n_pass60 = 0
    n_pass15 = 0
    for a in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        for (v, p, m) in VARIANTS:
            r = next((r for r in results if r["asset"] == a and r["variant"] == v), None)
            if not r: continue
            mt = r.get("metrics") or {}
            sh, tr, mdd, pnl = mt.get("sharpe"), mt.get("trades"), mt.get("mdd_pct"), mt.get("pnl_pct")
            pass60 = bool(sh is not None and tr is not None and mdd is not None
                          and sh >= 1.0 and tr >= 30 and mdd <= 10)
            pass15 = bool(sh is not None and tr is not None and mdd is not None
                          and sh >= 1.5 and tr >= 30 and mdd <= 10)
            if pass60: n_pass60 += 1
            if pass15: n_pass15 += 1
            print(f"{a:<8} {v:<8} {sh if sh is not None else 'NA':>7} {tr or 0:>5} "
                  f"{mdd if mdd is not None else 0:>6} {pnl if pnl is not None else 0:>8} | {pass60} | {pass15}")

    print(f"\nPadrão 60 strict (Sh >= 1.0): {n_pass60}/12")
    print(f"V1 strict (Sh >= 1.5): {n_pass15}/12")

    # Best variant per asset
    print(f"\n{'='*80}\nBest variant per asset (highest Sh)\n{'='*80}")
    for a in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        ar = [r for r in results if r["asset"] == a]
        ar.sort(key=lambda r: -((r.get("metrics") or {}).get("sharpe") or -999))
        if ar:
            r = ar[0]
            mt = r.get("metrics") or {}
            print(f"  {a}: best={r['variant']} Sh={mt.get('sharpe')} (delta vs raw: see below)")
            raw = next((r for r in ar if r["variant"] == "raw"), None)
            if raw:
                raw_sh = (raw.get("metrics") or {}).get("sharpe")
                if raw_sh is not None and (mt.get("sharpe") is not None):
                    print(f"    raw Sh={raw_sh}, best Sh={mt.get('sharpe')}, delta={mt.get('sharpe') - raw_sh:+.4f}")

    OUT.write_text(json.dumps({"results": results}, indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
