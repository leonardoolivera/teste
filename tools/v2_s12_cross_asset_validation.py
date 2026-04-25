"""V2 Cycle 9 — Cross-asset validation S12 (rsi_short_trendhtf SOL 2025-H1 → BTC + ETH).

S12 é único ROBUST do stack 13 sob Padrão 60 (Cycle 8): SOL 2025-H1 Sh=1.20, +29% PnL,
MDD=9.0% sobre janela contínua 30 meses. Mas é SOL-only.

Hipótese causal: rsi_short com gate trend_htf (4h SMA 50, mode short_only) deve
generalizar para BTC e ETH se o mecanismo é estrutural — entrar short apenas
quando 4h trend está bear, no extremo de RSI overbought.

Total: 3 assets × 1 fee level (10bps) = 3 probes em ~30s.

Variantes a testar:
- A) Janela contínua 30m (Padrão 60 strict)
- B) Per-asset baseline (controle)

Gate Padrão 60 reformulado: Sh ≥ 1.0 ∧ trades ≥ 30 ∧ MDD ≤ 10%.

Saída: `exports/diag/v2_s12_cross_asset.json`.
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
OUT = ROOT / "exports" / "diag" / "v2_s12_cross_asset.json"

DATASETS_30M = {
    "BTCUSDT": "btcusdt_1h_20230705_20251231_binance_spot_concat30m",
    "ETHUSDT": "ethusdt_1h_20230705_20251231_binance_spot_concat30m",
    "SOLUSDT": "solusdt_1h_20230705_20251231_binance_spot_concat30m",
}

FEE_BPS = 10.0
ANN = math.sqrt(24 * 365)

# S12 config: rsi 14/25/75 short_only + trend_htf 4h SMA 50 short_only
ENGINE_ARGS = [
    "--strategy", "rsi",
    "--rsi-period", "14",
    "--rsi-oversold", "25",
    "--rsi-overbought", "75",
    "--no-long-only",
]
REGIME = "trend_htf:htf=4h:sma_window=50:mode=short_only"


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


def run_one(asset: str) -> dict:
    ds = DATASETS_30M[asset]
    run_id = f"v2-s12-cross-{asset.lower()}-30m"
    args = base_args() + ["--run-id", run_id, "--dataset-id", ds] + ENGINE_ARGS + ["--regime-filter", REGIME]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    metrics = compute_metrics(run_id) if ok else {}
    return {"asset": asset, "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1), "metrics": metrics}


def main() -> int:
    print(f"[V2 S12 cross-asset] rsi_short_trendhtf 14/25/75 + trend_htf:4h:sma=50:short_only")
    print(f"[V2 S12 cross-asset] janela contínua 30 meses, fees 10bps")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(run_one, a): a for a in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            m = r.get("metrics") or {}
            print(f"  {r['asset']:<8} sh={m.get('sharpe')} tr={m.get('trades')} mdd={m.get('mdd_pct')}% pnl={m.get('pnl_pct')}% elapsed={r['elapsed']}s", flush=True)
    print(f"  wall={time.time() - t0:.0f}s")

    # Verdict
    print(f"\n{'='*70}\nS12 cross-asset Padrão 60 verdict\n{'='*70}")
    print(f"{'Asset':<8} {'Sh':>7} {'Tr':>5} {'MDD%':>7} {'PnL%':>8} {'Pass':<6}")
    n_pass = 0
    for r in sorted(results, key=lambda r: r["asset"]):
        m = r.get("metrics") or {}
        sh, tr, mdd, pnl = m.get("sharpe"), m.get("trades"), m.get("mdd_pct"), m.get("pnl_pct")
        pass_g = bool(sh is not None and tr is not None and mdd is not None
                      and sh >= 1.0 and tr >= 30 and mdd <= 10)
        if pass_g: n_pass += 1
        print(f"{r['asset']:<8} {sh if sh is not None else 'NA':>7} {tr or 0:>5} "
              f"{mdd if mdd is not None else 0:>7} {pnl if pnl is not None else 0:>8} {pass_g}")

    print(f"\nGate Padrão 60 (Sh>=1.0 AND tr>=30 AND MDD<=10%): {n_pass}/3 assets")
    if n_pass >= 2:
        print("PASS — S12 generaliza cross-asset. Único combo V2-validated do stack.")
    elif n_pass == 1:
        print("FAIL — S12 é SOL-specific. Mecanismo não generaliza.")
    else:
        print("CRITICAL FAIL — S12 SOL passa, BTC+ETH fracassam.")

    OUT.write_text(json.dumps({"results": results, "n_pass": n_pass}, indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
