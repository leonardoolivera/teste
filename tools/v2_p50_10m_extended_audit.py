"""V2 Cycle 10.C — Padrão 50 candidates V1 sob janela contínua 10m 18 meses.

Padrão 50 V1 (ADR-0202+0211): 5 configs trend-following long-only que passaram gate
em ETH 2025-H1 10m bear-avoidance (alfa +30-35% vs B&H -47%).

Hipótese pós-Padrão 60: edge era selection bias temporal de single-window 6m
(consistent com P52 GRAVEYARD). Em janela contínua 10m de 18 meses (2024-H2 +
2025-H1 + 2025-H2), Sh deve cair próximo a zero.

5 configs × 3 assets = 15 probes em ~3min wall-clock.

Configs Padrão 50 (Cycle 1 RB004 ADR-0214):
- supertrend 14/3.0 (P50-001)
- supertrend 14/3.5 (P50-002)
- supertrend 20/3.5 (P50-003)
- ma_crossover 20/50 long (P50-004)
- ma_crossover 25/75 long (P50-005)

Annualization 10m: sqrt(144*365) ≈ 229.25.

Gate Padrão 60: Sh ≥ 1.0 ∧ trades ≥ 30 ∧ MDD ≤ 10%.
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
OUT = ROOT / "exports" / "diag" / "v2_p50_10m_extended.json"

DATASETS_18M = {
    "BTCUSDT": "btcusdt_10m_20240705_20251231_binance_spot_concat18m",
    "ETHUSDT": "ethusdt_10m_20240705_20251231_binance_spot_concat18m",
    "SOLUSDT": "solusdt_10m_20240705_20251231_binance_spot_concat18m",
}

P50_CONFIGS = [
    {"id": "P50-ST-14-3.0", "args": ["--strategy", "supertrend", "--supertrend-atr-period", "14", "--supertrend-atr-mult", "3.0"]},
    {"id": "P50-ST-14-3.5", "args": ["--strategy", "supertrend", "--supertrend-atr-period", "14", "--supertrend-atr-mult", "3.5"]},
    {"id": "P50-ST-20-3.5", "args": ["--strategy", "supertrend", "--supertrend-atr-period", "20", "--supertrend-atr-mult", "3.5"]},
    {"id": "P50-MA-20-50", "args": ["--strategy", "ma_crossover", "--long-only", "--short-window", "20", "--long-window", "50"]},
    {"id": "P50-MA-25-75", "args": ["--strategy", "ma_crossover", "--long-only", "--short-window", "25", "--long-window", "75"]},
]

FEE_BPS = 10.0
ANN_10M = math.sqrt(144 * 365)


def base_args() -> list[str]:
    return [
        "alpha-forge", "validate",
        "--capital", "10000.0", "--fracao", "0.1", "--alavancagem", "2.0",
        "--sizing-mode", "fixed_notional",
        "--taker-fee-bps", str(FEE_BPS),
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--n-folds", "5", "--scheme", "rolling",
        "--train-fraction", "0.5", "--min-test-bars", "500",
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
        sh = (mean / sd) * ANN_10M if sd > 0 else 0.0
    else:
        sh = 0.0
    peak = full_eq[0]; mdd = 0.0
    for v in full_eq:
        if v > peak: peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > mdd: mdd = dd
    return {"trades": n_trades, "sharpe": round(sh, 4), "pnl_pct": round(pnl, 4), "mdd_pct": round(mdd * 100, 4)}


def run_one(config: dict, asset: str) -> dict:
    ds = DATASETS_18M[asset]
    run_id = f"v2-p50-10m-{config['id'].lower()}-{asset.lower()}-18m"
    args = base_args() + ["--run-id", run_id, "--dataset-id", ds] + config["args"]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=1200)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    metrics = compute_metrics(run_id) if ok else {}
    return {"config": config["id"], "asset": asset, "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1), "metrics": metrics}


def main() -> int:
    jobs = [(c, a) for c in P50_CONFIGS for a in DATASETS_18M]
    print(f"[V2 P50 10m extended audit] {len(jobs)} probes (5 configs × 3 assets), 18m window, fees 10bps")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, c, a): (c, a) for (c, a) in jobs}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            m = r.get("metrics") or {}
            print(f"  {r['config']:<16} {r['asset']:<8} sh={m.get('sharpe')} tr={m.get('trades')} mdd={m.get('mdd_pct')}% pnl={m.get('pnl_pct')}% elapsed={r['elapsed']}s", flush=True)
    print(f"\n  wall={time.time() - t0:.0f}s")

    print(f"\n{'='*80}\nPadrão 50 V1 candidates sob janela contínua 10m 18m (Padrão 60 audit)\n{'='*80}")
    print(f"{'Config':<16} {'Asset':<8} {'Sh':>7} {'Tr':>5} {'MDD%':>6} {'PnL%':>8} | Pass")
    n_pass = 0
    n_total = 0
    for c in P50_CONFIGS:
        for a in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
            r = next((r for r in results if r["config"] == c["id"] and r["asset"] == a), None)
            if not r: continue
            m = r.get("metrics") or {}
            sh, tr, mdd, pnl = m.get("sharpe"), m.get("trades"), m.get("mdd_pct"), m.get("pnl_pct")
            pass_g = bool(sh is not None and tr is not None and mdd is not None
                          and sh >= 1.0 and tr >= 30 and mdd <= 10)
            n_total += 1
            if pass_g: n_pass += 1
            print(f"{c['id']:<16} {a:<8} {sh if sh is not None else 'NA':>7} {tr or 0:>5} "
                  f"{mdd if mdd is not None else 0:>6} {pnl if pnl is not None else 0:>8} | {pass_g}")

    print(f"\nPadrão 60 gate (Sh>=1.0 AND tr>=30 AND MDD<=10%): {n_pass}/{n_total} probes pass")
    if n_pass == 0:
        print("CRITICAL: 0/15 — Padrão 50 candidates V1 são selection bias temporal puro (igual P52). GRAVEYARD coletivo recomendado.")
    elif n_pass < 3:
        print(f"WEAK: apenas {n_pass}/15 — não suficiente para promoção; mantém GRAVEYARD historic.")
    else:
        print(f"SURVIVE: {n_pass}/15 — investigar quais sobrevivem.")

    OUT.write_text(json.dumps({"results": results, "n_pass": n_pass, "n_total": n_total}, indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
