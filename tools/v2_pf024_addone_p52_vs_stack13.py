"""V2 PF024 — Add-one candidate P52 vs stack 13 (RAIO Nível 5 Portfolio Integration).

Roda cada combo do stack 13 + P52 BTC 18/60 sobre janela comum (cada combo no
asset original mas window=2024-H2, onde P52 prova edge), extrai equity curves
alinhadas, e compara:

A) Stack 13 equal weight (1/13 cada).
B) Stack 14 equal weight (1/14 cada, incluindo P52).
C) P52 standalone.

Métricas:
- Sharpe annualized
- Calmar (CAGR/MDD)
- MDD %
- Correlação P52 vs cada combo
- Marginal contribution P52 (Sharpe diff B - A)

Critério PF024 (RAIO Nível 5):
- Add-one P52 deve **melhorar** Sharpe ou Calmar do portfolio sem aumentar MDD.
- Se piora qualquer das 3 → P52 fica SURVIVOR mas não promove a Nível 6 ADR.

Nota: usa janela 2024-H2 (overlap dos combos via window=2024-H2 forçada). Combos
originalmente aprovados em outras windows são re-rodados aqui apenas para
alignment temporal — não para promoção/retirada do stack.

Saída: `exports/diag/v2_pf024_addone_p52.json`.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "v2_pf024_addone_p52.json"

DATASETS_2024_H2 = {
    "BTCUSDT": "btcusdt_1h_20240705_20241231_binance_spot",
    "ETHUSDT": "ethusdt_1h_20240705_20241231_binance_spot",
    "SOLUSDT": "solusdt_1h_20240705_20241231_binance_spot",
}

# 13 combos + P52 — todos forçados em 2024-H2 do asset original
PORTFOLIO = [
    {"id": "S01", "symbol": "ETHUSDT", "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5", "--long-only"], "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    {"id": "S02", "symbol": "ETHUSDT", "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5", "--long-only"], "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    {"id": "S03", "symbol": "BTCUSDT", "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5", "--long-only"], "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    {"id": "S04", "symbol": "SOLUSDT", "engine_args": ["--strategy", "bollinger", "--bollinger-window", "30", "--bollinger-num-std", "1.5", "--long-only"], "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=250"},
    {"id": "S05", "symbol": "SOLUSDT", "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5", "--no-long-only"], "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S06", "symbol": "BTCUSDT", "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5", "--no-long-only"], "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S07", "symbol": "ETHUSDT", "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5", "--no-long-only"], "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S08", "symbol": "SOLUSDT", "engine_args": ["--strategy", "bollinger", "--bollinger-window", "20", "--bollinger-num-std", "1.5", "--no-long-only"], "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S09", "symbol": "ETHUSDT", "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70", "--long-only"], "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "S10", "symbol": "BTCUSDT", "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70", "--no-long-only"], "regime": None},
    {"id": "S11", "symbol": "SOLUSDT", "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70", "--no-long-only"], "regime": None},
    {"id": "S12", "symbol": "SOLUSDT", "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "25", "--rsi-overbought", "75", "--no-long-only"], "regime": "trend_htf:htf=4h:sma_window=50:mode=short_only"},
    {"id": "S13", "symbol": "BTCUSDT", "engine_args": ["--strategy", "rsi", "--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70", "--no-long-only"], "regime": "bollinger_width:window=30:num_std=1.5:min_width_bps=300"},
    {"id": "P52", "symbol": "BTCUSDT", "engine_args": ["--strategy", "ma_crossover", "--long-only", "--short-window", "18", "--long-window", "60"], "regime": None},
]

ANN = math.sqrt(24 * 365)


def base_args() -> list[str]:
    return [
        "alpha-forge", "validate",
        "--capital", "10000.0", "--fracao", "0.1", "--alavancagem", "2.0",
        "--sizing-mode", "fixed_notional",
        "--taker-fee-bps", "5.0",
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--n-folds", "5", "--scheme", "rolling",
        "--train-fraction", "0.5", "--min-test-bars", "50",
        "--mc-resamples", "500", "--mc-seed", "42",
        "--log-level", "silent",
    ]


def run_one(combo: dict) -> dict:
    ds = DATASETS_2024_H2[combo["symbol"]]
    run_id = f"v2-pf024-{combo['id'].lower()}-{combo['symbol'].lower()}-2024h2"
    args = base_args() + ["--run-id", run_id, "--dataset-id", ds] + combo["engine_args"]
    if combo["regime"]:
        args += ["--regime-filter", combo["regime"]]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=600)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    return {"id": combo["id"], "symbol": combo["symbol"], "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1)}


def equity_curve_aligned(run_id: str) -> tuple[list[str], list[float]]:
    """Concatena equity curves de todos os 5 folds; retorna (timestamps, normalized equity).
    Equity normalizada com base 1.0 no início.
    """
    p = RESULTS / run_id / "walk_forward.json"
    if not p.exists(): return [], []
    wf = json.loads(p.read_text())
    folds = wf.get("payload", [])
    timestamps: list[str] = []
    eq_norm: list[float] = []
    base_eq = 1.0
    for f in folds:
        ec = f.get("result", {}).get("equity_curve", []) or []
        if not ec: continue
        first_v = ec[0][1] if ec[0][1] != 0 else 1.0
        for ts, v in ec:
            timestamps.append(ts)
            eq_norm.append(base_eq * v / first_v)
        base_eq = eq_norm[-1] if eq_norm else 1.0
    return timestamps, eq_norm


def aligned_returns_matrix(curves: dict[str, tuple[list[str], list[float]]]) -> tuple[list[str], np.ndarray, list[str]]:
    """Retorna (timestamps_intersection, returns_matrix [T, N], combo_ids).
    Returns: para cada timestamp comum, retornos por combo. Combos sem dado nesse ts contribuem 0.
    """
    if not curves: return [], np.zeros((0, 0)), []
    ts_sets = [set(c[0]) for c in curves.values()]
    common_ts = sorted(set.intersection(*ts_sets))
    combo_ids = list(curves.keys())
    eq_by_ts: dict[str, dict[str, float]] = {ts: {} for ts in common_ts}
    for cid, (tss, eqs) in curves.items():
        for t, v in zip(tss, eqs):
            if t in eq_by_ts:
                eq_by_ts[t][cid] = v
    # converter para retornos bar-by-bar
    n = len(common_ts)
    n_combos = len(combo_ids)
    rets = np.zeros((n, n_combos))
    prev_eq = {cid: None for cid in combo_ids}
    for i, ts in enumerate(common_ts):
        for j, cid in enumerate(combo_ids):
            cur = eq_by_ts[ts].get(cid)
            if cur is None or prev_eq[cid] is None or prev_eq[cid] == 0:
                rets[i, j] = 0.0
            else:
                rets[i, j] = cur / prev_eq[cid] - 1
            if cur is not None:
                prev_eq[cid] = cur
    return common_ts, rets, combo_ids


def portfolio_metrics(rets: np.ndarray, weights: np.ndarray) -> dict:
    """rets: [T, N]; weights: [N] equal weight. Retorna métricas portfolio."""
    if rets.size == 0 or weights.sum() == 0:
        return {"sharpe": 0, "calmar": 0, "mdd_pct": 0, "pnl_pct": 0, "n_bars": 0}
    pf_ret = rets @ weights
    cum = np.cumprod(1 + pf_ret)
    pnl = (cum[-1] - 1) * 100 if len(cum) > 0 else 0
    sd = pf_ret.std(ddof=0)
    sh = (pf_ret.mean() / sd * ANN) if sd > 0 else 0
    peak = np.maximum.accumulate(cum)
    dd = (peak - cum) / np.where(peak > 0, peak, 1)
    mdd = float(dd.max()) * 100 if len(dd) > 0 else 0
    # Calmar: CAGR / MDD%
    n_bars = len(pf_ret)
    cagr_factor = (n_bars / (24 * 365))
    cagr = (cum[-1] ** (1 / cagr_factor) - 1) * 100 if cum[-1] > 0 and cagr_factor > 0 else 0
    calmar = cagr / mdd if mdd > 0 else 0
    return {"sharpe": round(float(sh), 4), "calmar": round(calmar, 4),
            "mdd_pct": round(mdd, 4), "pnl_pct": round(float(pnl), 4),
            "n_bars": int(n_bars)}


def main() -> int:
    print(f"[PF024] launching {len(PORTFOLIO)} runs (stack 13 + P52) on 2024-H2 window")
    t0 = time.time()
    runs = []
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, c): c for c in PORTFOLIO}
        for fut in as_completed(futs):
            r = fut.result()
            runs.append(r)
            print(f"  {r['id']:<5} {r['symbol']:<8} ok={r['ok']} elapsed={r['elapsed']}s", flush=True)
    print(f"  wall={time.time() - t0:.0f}s")

    # Extract equity curves
    curves = {}
    for r in runs:
        if not r["ok"]: continue
        ts, eq = equity_curve_aligned(r["run_id"])
        if eq:
            curves[r["id"]] = (ts, eq)
    print(f"\nCurves extracted: {len(curves)} combos")

    common_ts, rets, combo_ids = aligned_returns_matrix(curves)
    print(f"Common timestamps: {len(common_ts)} bars")
    print(f"Combos in matrix: {combo_ids}")

    if "P52" not in combo_ids:
        print("[ERROR] P52 não está no resultado")
        return 1

    n_combos = len(combo_ids)
    p52_idx = combo_ids.index("P52")
    stack_idxs = [i for i in range(n_combos) if i != p52_idx]

    # A) Stack 13 equal weight
    w_stack = np.zeros(n_combos)
    w_stack[stack_idxs] = 1.0 / len(stack_idxs)
    metrics_a = portfolio_metrics(rets, w_stack)

    # B) Stack 14 equal weight (with P52)
    w_stack14 = np.ones(n_combos) / n_combos
    metrics_b = portfolio_metrics(rets, w_stack14)

    # C) P52 standalone
    w_p52 = np.zeros(n_combos)
    w_p52[p52_idx] = 1.0
    metrics_c = portfolio_metrics(rets, w_p52)

    # Correlations P52 vs each
    p52_rets = rets[:, p52_idx]
    corrs = {}
    for j, cid in enumerate(combo_ids):
        if cid == "P52": continue
        if rets[:, j].std() == 0 or p52_rets.std() == 0:
            corrs[cid] = 0.0
        else:
            corrs[cid] = float(np.corrcoef(p52_rets, rets[:, j])[0, 1])

    # Print
    print(f"\n{'='*70}\nPF024 Add-one P52 vs Stack 13\n{'='*70}")
    print(f"\n(A) Stack 13 equal weight:")
    for k, v in metrics_a.items(): print(f"  {k:<12} {v}")
    print(f"\n(B) Stack 14 (with P52 1/14):")
    for k, v in metrics_b.items(): print(f"  {k:<12} {v}")
    print(f"\n(C) P52 standalone:")
    for k, v in metrics_c.items(): print(f"  {k:<12} {v}")

    print(f"\n[B - A] marginal contribution of adding P52:")
    print(f"  delta sharpe: {metrics_b['sharpe'] - metrics_a['sharpe']:+.4f}")
    print(f"  delta calmar: {metrics_b['calmar'] - metrics_a['calmar']:+.4f}")
    print(f"  delta mdd_pct: {metrics_b['mdd_pct'] - metrics_a['mdd_pct']:+.4f}")
    print(f"  delta pnl_pct: {metrics_b['pnl_pct'] - metrics_a['pnl_pct']:+.4f}")

    print(f"\nCorrelations P52 vs each combo:")
    for cid, c in sorted(corrs.items(), key=lambda x: -abs(x[1])):
        print(f"  {cid:<5} corr={c:+.4f}")

    # PF024 verdict
    sh_improves = metrics_b["sharpe"] > metrics_a["sharpe"]
    calmar_improves = metrics_b["calmar"] > metrics_a["calmar"]
    mdd_worsens = metrics_b["mdd_pct"] > metrics_a["mdd_pct"] * 1.05  # 5% tolerance
    if sh_improves and calmar_improves and not mdd_worsens:
        verdict = "PF024 PASS — P52 add-one melhora portfolio"
        decision = "EXPAND para Nível 6 (Candidate for ADR)"
    elif (sh_improves or calmar_improves) and not mdd_worsens:
        verdict = "PF024 PARTIAL — P52 add-one melhora um eixo sem piorar DD"
        decision = "MAINTAIN SURVIVOR; revisar pesos não-equal"
    else:
        verdict = "PF024 FAIL — P52 não melhora portfolio em equal-weight"
        decision = "MAINTAIN SURVIVOR; explorar correlation cap ou risk parity"
    print(f"\n{verdict}")
    print(f"DECISION: {decision}")

    payload = {
        "metrics_a_stack13": metrics_a,
        "metrics_b_stack14_with_p52": metrics_b,
        "metrics_c_p52_standalone": metrics_c,
        "deltas_b_minus_a": {
            "sharpe": round(metrics_b["sharpe"] - metrics_a["sharpe"], 4),
            "calmar": round(metrics_b["calmar"] - metrics_a["calmar"], 4),
            "mdd_pct": round(metrics_b["mdd_pct"] - metrics_a["mdd_pct"], 4),
            "pnl_pct": round(metrics_b["pnl_pct"] - metrics_a["pnl_pct"], 4),
        },
        "correlations_p52": corrs,
        "n_common_bars": len(common_ts),
        "verdict": verdict,
        "decision": decision,
    }
    OUT.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
