"""V2 Cycle 8 — Audit retroativo stack 13 sob Padrão 60 (janela contínua 30m).

Padrão 60 (ADR-0221): janelas curtas (≤6 meses) inflacionam Sharpe via
temporal selection bias. Manifests aprovados V1 foram validados em windows
de 6 meses. Esta auditoria retroativa testa cada combo do stack 13 sobre
janela contínua 30 meses (concat datasets criados Cycle 7) com fees 10bps
default V2.

Hipótese: alguns combos do stack 13 podem revelar-se P52-like (edge intra-window
era selection bias). Identifica candidatos para retirada de manifest.

Total: 13 combos × 1 fee level (10bps default V2) = 13 probes. ~30s wall-clock.

Gate Padrão 60:
- Sh ≥ 1.0 ∧ trades ≥ 30 ∧ MDD ≤ 10% (relax de 5% pra MR strategies)
- ROBUST: gate pass.
- MARGINAL: Sh entre 0.5-1.0 OR trade count borderline.
- FAIL: Sh < 0.5 OR negative.

Saída: `exports/diag/v2_stack13_padrao60_audit.json`.
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
OUT = ROOT / "exports" / "diag" / "v2_stack13_padrao60_audit.json"

DATASETS_30M = {
    "BTCUSDT": "btcusdt_1h_20230705_20251231_binance_spot_concat30m",
    "ETHUSDT": "ethusdt_1h_20230705_20251231_binance_spot_concat30m",
    "SOLUSDT": "solusdt_1h_20230705_20251231_binance_spot_concat30m",
}

# Stack 13 — mesmo do RB007 fixed (ADR-0216)
STACK_13 = [
    {"id": "S01", "manifest": "bollinger_width_regime_v2", "symbol": "ETHUSDT",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5", "--long-only"],
     "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    {"id": "S02", "manifest": "bollinger_width_regime_v2", "symbol": "ETHUSDT",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5", "--long-only"],
     "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    {"id": "S03", "manifest": "bollinger_width_regime_v2", "symbol": "BTCUSDT",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5", "--long-only"],
     "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    {"id": "S04", "manifest": "bollinger_width_regime_v2", "symbol": "SOLUSDT",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5", "--long-only"],
     "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    {"id": "S05", "manifest": "bollinger_short_width", "symbol": "SOLUSDT",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5", "--no-long-only"],
     "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S06", "manifest": "bollinger_short_width", "symbol": "BTCUSDT",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5", "--no-long-only"],
     "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S07", "manifest": "bollinger_short_width", "symbol": "ETHUSDT",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5", "--no-long-only"],
     "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S08", "manifest": "bollinger_short_width", "symbol": "SOLUSDT",
     "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5", "--no-long-only"],
     "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S09", "manifest": "rsi_long_width_eth_2024h2", "symbol": "ETHUSDT",
     "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70", "--long-only"],
     "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S10", "manifest": "rsi_short_pure_2025h2", "symbol": "BTCUSDT",
     "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70", "--no-long-only"],
     "regime": None},
    {"id": "S11", "manifest": "rsi_short_pure_2025h2", "symbol": "SOLUSDT",
     "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70", "--no-long-only"],
     "regime": None},
    {"id": "S12", "manifest": "rsi_short_trendhtf_sol_2025h1", "symbol": "SOLUSDT",
     "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "25", "--rsi-overbought", "75", "--no-long-only"],
     "regime": "trend_htf:htf=4h:sma_window=50:mode=short_only"},
    {"id": "S13", "manifest": "rsi_short_width_2025h1", "symbol": "BTCUSDT",
     "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70", "--no-long-only"],
     "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
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


def run_one(combo: dict) -> dict:
    ds = DATASETS_30M[combo["symbol"]]
    run_id = f"v2-stack13-p60-{combo['id'].lower()}-{combo['symbol'].lower()}-30m"
    args = base_args() + ["--run-id", run_id, "--dataset-id", ds] + combo["engine_args"]
    if combo["regime"]:
        args += ["--regime-filter", combo["regime"]]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    metrics = compute_metrics(run_id) if ok else {}
    return {"id": combo["id"], "manifest": combo["manifest"], "symbol": combo["symbol"],
            "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1), "metrics": metrics}


def main() -> int:
    print(f"[V2 stack13 Padrão 60 audit] {len(STACK_13)} combos × 30m window × fees 10bps")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, c): c for c in STACK_13}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            m = r.get("metrics") or {}
            print(f"  {r['id']:<5} {r['manifest'][:30]:<30} {r['symbol']:<8} sh={m.get('sharpe')} tr={m.get('trades')} mdd={m.get('mdd_pct')}% pnl={m.get('pnl_pct')}% elapsed={r['elapsed']}s", flush=True)
    print(f"\n  wall={time.time() - t0:.0f}s")

    # Tabela ordenada por id
    print(f"\n{'='*90}\nStack 13 sobre janela contínua 30m (Padrão 60 audit)\n{'='*90}")
    print(f"{'ID':<5} {'Manifest':<32} {'Sym':<7} {'Sh':>7} {'Tr':>5} {'MDD%':>7} {'PnL%':>8} | Verdict")
    n_robust = 0; n_marginal = 0; n_fail = 0
    verdicts = {}
    for cid in [c["id"] for c in STACK_13]:
        r = next((r for r in results if r["id"] == cid), None)
        if not r: continue
        m = r.get("metrics") or {}
        sh, tr, mdd, pnl = m.get("sharpe"), m.get("trades"), m.get("mdd_pct"), m.get("pnl_pct")
        if sh is not None and tr is not None and mdd is not None:
            if sh >= 1.0 and tr >= 30 and mdd <= 10:
                v = "ROBUST"; n_robust += 1
            elif sh >= 0.5 and tr >= 30 and mdd <= 15:
                v = "MARGINAL"; n_marginal += 1
            else:
                v = "FAIL"; n_fail += 1
        else:
            v = "INC"
        verdicts[cid] = v
        print(f"{cid:<5} {r['manifest'][:32]:<32} {r['symbol']:<7} {sh if sh is not None else 'NA':>7} {tr or 0:>5} {mdd if mdd is not None else 0:>7} {pnl if pnl is not None else 0:>8} | {v}")

    print(f"\nROBUST: {n_robust}/13  MARGINAL: {n_marginal}/13  FAIL: {n_fail}/13")
    print(f"\nCombos FAIL (candidatos a retirada do stack):")
    for cid, v in verdicts.items():
        if v == "FAIL":
            r = next(r for r in results if r["id"] == cid)
            m = r.get("metrics") or {}
            print(f"  {cid}: {r['manifest']} {r['symbol']} — Sh={m.get('sharpe')} tr={m.get('trades')} mdd={m.get('mdd_pct')}%")

    OUT.write_text(json.dumps({"results": results, "verdicts": verdicts,
                                "n_robust": n_robust, "n_marginal": n_marginal, "n_fail": n_fail},
                              indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
