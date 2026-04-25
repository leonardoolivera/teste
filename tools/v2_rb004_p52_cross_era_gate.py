"""V2 RB004 — Cross-era validation P52 BTC 18/60 (gate pré-export ADR-0030).

P52 SURVIVOR + Candidate for ADR após PF024 PASS (Ciclo 4). Gate hard pra
qualquer export BotBinance: cross-era validation além do regime de discovery
(2024-H2). Datasets disponíveis: 2022-H1, 2022-H2, 2023-H2, 2024-H1, 2024-H2,
2025-H1, 2025-H2.

Janelas testadas (cross-era, fora de 2024-H2):
- 2024-H1 (continuidade próxima)
- 2023-H2 (regime distinto, recovery pós-bear 2022)
- 2022-H1 (bear extreme - LUNA collapse, FTX início)
- 2022-H2 (bear continuação - FTX collapse)

Configs: P52 BTC 18/60 long-only, sem regime filter (canonical).

Total: 4 windows × 3 assets (BTC, ETH, SOL) × 2 fee levels (5bps, 10bps) = 24 probes.

Gate per RAIO Nível 4 + ADR-0030:
- Em pelo menos 2 windows não-discovery (não-2024-H2), Sh ≥ 1.0 com fees 10bps.
- Edge cross-era preservado em pelo menos 2 dos 3 assets.
- Se passa: ADR-0219 manifest P52 v3.
- Se falha: P52 → Quarantined com escopo regime-2024.

Saída: `exports/diag/v2_rb004_p52_cross_era_gate.json`.
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
OUT = ROOT / "exports" / "diag" / "v2_rb004_p52_cross_era_gate.json"

DATASETS = {
    ("BTCUSDT", "2022-H1"): "btcusdt_1h_20220105_20220704_binance_spot",
    ("BTCUSDT", "2022-H2"): "btcusdt_1h_20220705_20221231_binance_spot",
    ("BTCUSDT", "2023-H2"): "btcusdt_1h_20230705_20231231_binance_spot",
    ("BTCUSDT", "2024-H1"): "btcusdt_1h_20240105_20240704_binance_spot",
    ("ETHUSDT", "2022-H1"): "ethusdt_1h_20220105_20220704_binance_spot",
    ("ETHUSDT", "2022-H2"): "ethusdt_1h_20220705_20221231_binance_spot",
    ("ETHUSDT", "2023-H2"): "ethusdt_1h_20230705_20231231_binance_spot",
    ("ETHUSDT", "2024-H1"): "ethusdt_1h_20240105_20240704_binance_spot",
    ("SOLUSDT", "2022-H1"): "solusdt_1h_20220105_20220704_binance_spot",
    ("SOLUSDT", "2022-H2"): "solusdt_1h_20220705_20221231_binance_spot",
    ("SOLUSDT", "2023-H2"): "solusdt_1h_20230705_20231231_binance_spot",
    ("SOLUSDT", "2024-H1"): "solusdt_1h_20240105_20240704_binance_spot",
}

FEE_LEVELS = [(5.0, "5bps"), (10.0, "10bps")]
ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
WINDOWS_NON_DISCOVERY = ["2022-H1", "2022-H2", "2023-H2", "2024-H1"]

ANN = math.sqrt(24 * 365)


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


def run_one(asset: str, window: str, fee_bps: float, fee_label: str) -> dict:
    ds = DATASETS[(asset, window)]
    run_id = f"v2-rb004-p52-{asset.lower()}-{window.lower()}-{fee_label}"
    args = base_args(fee_bps) + [
        "--run-id", run_id, "--dataset-id", ds,
        "--strategy", "ma_crossover", "--long-only",
        "--short-window", "18", "--long-window", "60",
    ]
    code = f"import sys; sys.argv = {args!r}; from alpha_forge.cli.app import main; main()"
    t0 = time.time()
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=600)
        ok = proc.returncode == 0
    except subprocess.TimeoutExpired:
        ok = False
    metrics = compute_metrics(run_id) if ok else {}
    return {"asset": asset, "window": window, "fee_bps": fee_bps, "fee_label": fee_label,
            "run_id": run_id, "ok": ok, "elapsed": round(time.time() - t0, 1), "metrics": metrics}


def main() -> int:
    jobs = [(a, w, f, l) for a in ASSETS for w in WINDOWS_NON_DISCOVERY for f, l in FEE_LEVELS]
    print(f"[V2-RB004 P52 cross-era gate] {len(jobs)} probes (3 assets × 4 windows × 2 fees)")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run_one, a, w, f, l): (a, w, f, l) for (a, w, f, l) in jobs}
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            m = r.get("metrics") or {}
            sh, tr = m.get("sharpe"), m.get("trades")
            print(f"  {r['asset']:<8} {r['window']:<8} fee={r['fee_label']:<6} sh={sh} tr={tr} elapsed={r['elapsed']}s", flush=True)
    print(f"\n  wall={time.time() - t0:.0f}s")

    # Analysis
    print(f"\n{'='*70}\nP52 BTC 18/60 cross-era gate (fee-sensitive 10bps screening default)\n{'='*70}")
    print(f"\n{'Window':<10} {'Asset':<8} {'Sh@5':>7} {'Sh@10':>7} {'Tr':>5} {'PnL%':>7} {'MDD%':>6} | Pass@10")
    n_pass = 0
    n_total = 0
    by_window = {}
    for w in WINDOWS_NON_DISCOVERY:
        by_window[w] = []
        for a in ASSETS:
            r5 = next((r for r in results if r["asset"] == a and r["window"] == w and r["fee_label"] == "5bps"), None)
            r10 = next((r for r in results if r["asset"] == a and r["window"] == w and r["fee_label"] == "10bps"), None)
            sh5 = (r5.get("metrics") or {}).get("sharpe") if r5 else None
            sh10 = (r10.get("metrics") or {}).get("sharpe") if r10 else None
            tr = (r10.get("metrics") or {}).get("trades") if r10 else None
            pnl = (r10.get("metrics") or {}).get("pnl_pct") if r10 else None
            mdd = (r10.get("metrics") or {}).get("mdd_pct") if r10 else None
            pass_10 = bool(sh10 is not None and tr is not None and sh10 >= 1.0 and tr >= 30)
            n_total += 1
            if pass_10:
                n_pass += 1
                by_window[w].append(a)
            print(f"{w:<10} {a:<8} {sh5 if sh5 is not None else 'NA':>7} {sh10 if sh10 is not None else 'NA':>7} "
                  f"{tr or 0:>5} {pnl if pnl is not None else 0:>7} {mdd if mdd is not None else 0:>6} | {pass_10}")

    # Gate ADR-0030: ≥ 2 windows non-discovery com Sh ≥ 1.0 fees 10bps em ≥ 2 assets cada window
    windows_passing = sum(1 for w in WINDOWS_NON_DISCOVERY if len(by_window[w]) >= 2)
    gate_adr0030 = windows_passing >= 2

    print(f"\n{'='*70}")
    print(f"Pass count (Sh ≥ 1.0 ∧ tr ≥ 30 com fees 10bps): {n_pass}/{n_total} ({n_pass/n_total*100:.0f}%)")
    print(f"Windows com ≥ 2 assets passando: {windows_passing} de {len(WINDOWS_NON_DISCOVERY)}")
    for w in WINDOWS_NON_DISCOVERY:
        passes = by_window[w]
        print(f"  {w}: {len(passes)} assets pass — {passes}")
    print(f"\nGate ADR-0030 (cross-era ≥ 2 windows × ≥ 2 assets): {'PASS' if gate_adr0030 else 'FAIL'}")
    if gate_adr0030:
        print("  -> P52 PROMOVIDO a manifest-ready. Próximo: ADR-0219 Manifest P52 v3 + export.")
    else:
        print("  -> P52 mantém Candidate-for-ADR mas NÃO export. Regime-2024 dependent.")

    OUT.write_text(json.dumps({
        "n_probes": n_total, "n_pass": n_pass,
        "windows_passing": windows_passing,
        "gate_adr0030": gate_adr0030,
        "by_window": {w: by_window[w] for w in WINDOWS_NON_DISCOVERY},
        "results": results,
    }, indent=2, default=str))
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
