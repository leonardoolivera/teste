"""Roadmap 1000 — dispatcher paralelo automático.

Lê `exports/diag/roadmap_1000.json`, filtra entries imediatamente runnable
(engine no CLI, dataset conhecido, params concretos, regime_filter='none' nesta
Fase), e dispara N workers em paralelo (subprocess por probe, isolamento total).

Resumable: cada probe completado é gravado em
`exports/diag/roadmap_auto_progress.json` (append). Re-rodar pula o que já
estiver lá.

Uso:
    python tools/run_roadmap_auto.py [--workers N] [--limit M] [--filter-set X]

Default: workers=10, sem limit, filter-set='none' (Fase 1).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROADMAP = ROOT / "exports" / "diag" / "roadmap_1000.json"
PROGRESS = ROOT / "exports" / "diag" / "roadmap_auto_progress.json"
RESULTS = ROOT / "results" / "validation"

DATASETS = {
    "BTC": {
        "2024-H2": ("btcusdt_1h_20240705_20241231_binance_spot", "1h"),
        "2025-H1": ("btcusdt_1h_20250105_20250704_binance_spot", "1h"),
        "2025-H2": ("btcusdt_1h_20250705_20251231_binance_spot", "1h"),
        "10m-2024-H2": ("btcusdt_10m_20240705_20241231_binance_spot_resampled", "10m"),
        "10m-2025-H1": ("btcusdt_10m_20250105_20250704_binance_spot_resampled", "10m"),
        "10m-2025-H2": ("btcusdt_10m_20250705_20251231_binance_spot_resampled", "10m"),
    },
    "ETH": {
        "2024-H2": ("ethusdt_1h_20240705_20241231_binance_spot", "1h"),
        "2025-H1": ("ethusdt_1h_20250105_20250704_binance_spot", "1h"),
        "2025-H2": ("ethusdt_1h_20250705_20251231_binance_spot", "1h"),
        "10m-2024-H2": ("ethusdt_10m_20240705_20241231_binance_spot_resampled", "10m"),
        "10m-2025-H1": ("ethusdt_10m_20250105_20250704_binance_spot_resampled", "10m"),
        "10m-2025-H2": ("ethusdt_10m_20250705_20251231_binance_spot_resampled", "10m"),
    },
    "SOL": {
        "2024-H2": ("solusdt_1h_20240705_20241231_binance_spot", "1h"),
        "2025-H1": ("solusdt_1h_20250105_20250704_binance_spot", "1h"),
        "2025-H2": ("solusdt_1h_20250705_20251231_binance_spot", "1h"),
        "10m-2024-H2": ("solusdt_10m_20240705_20241231_binance_spot_resampled", "10m"),
        "10m-2025-H1": ("solusdt_10m_20250105_20250704_binance_spot_resampled", "10m"),
        "10m-2025-H2": ("solusdt_10m_20250705_20251231_binance_spot_resampled", "10m"),
    },
    "DOT": {
        "2025-H1": ("dotusdt_1h_20250105_20250704_binance_spot", "1h"),
        "2025-H2": ("dotusdt_1h_20250705_20251231_binance_spot", "1h"),
    },
    "LINK": {
        "2025-H1": ("linkusdt_1h_20250105_20250704_binance_spot", "1h"),
        "2025-H2": ("linkusdt_1h_20250705_20251231_binance_spot", "1h"),
    },
    "AVAX": {
        "2025-H1": ("avaxusdt_1h_20250105_20250704_binance_spot", "1h"),
        "2025-H2": ("avaxusdt_1h_20250705_20251231_binance_spot", "1h"),
    },
}

SUPPORTED_ENGINES = {
    "bollinger", "rsi", "ma_crossover", "supertrend",
    "composite_bb_rsi", "keltner", "zscore", "donchian",
}

CONCRETE_RE = re.compile(r"(\w+=[\w\d./]+)(,\w+=[\w\d./]+)*")

# Canonical stack filter (ADR-0028+) — bollinger_width 30/1.5 com min_width_bps=250.
STACK_CANONICAL_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=250"
TREND_HTF_LONG = "trend_htf:htf=4h:sma_window=50:mode=long_only"
TREND_HTF_SHORT = "trend_htf:htf=4h:sma_window=50:mode=short_only"


def translate_regime_filter(rf: str) -> str | None:
    """Mapeia roadmap_1000 regime_filter -> CLI --regime-filter SPEC.
    Retorna None para skip (filtro requer infra adicional ou n/a).
    """
    if rf in ("none", "n/a"):
        return None
    if rf in ("width_basic", "stack_canonical"):
        return STACK_CANONICAL_FILTER
    if rf.startswith("width:min="):
        bps = rf.split("=", 1)[1]
        return f"bollinger_width:window=30:num_std=1.5:min_width_bps={bps}"
    if rf == "trend_htf:4h:sma=50:long_only":
        return TREND_HTF_LONG
    if rf == "trend_htf:4h:sma=50:short_only":
        return TREND_HTF_SHORT
    if rf == "trend_htf:4h:sma=100":
        return "trend_htf:htf=4h:sma_window=100:mode=long_only"
    if rf.startswith("AND(") and rf.endswith(")"):
        # AND(width=150,trend_htf_long) -> and(bollinger_width:...,trend_htf:...)
        inner = rf[4:-1]
        parts = [p.strip() for p in inner.split(",")]
        translated = []
        for p in parts:
            if p.startswith("width="):
                bps = p.split("=", 1)[1]
                translated.append(f"bollinger_width:window=30:num_std=1.5:min_width_bps={bps}")
            elif p == "trend_htf_long":
                translated.append(TREND_HTF_LONG)
            elif p == "trend_htf_short":
                translated.append(TREND_HTF_SHORT)
            else:
                return None
        return f"and({','.join(translated)})"
    if rf.startswith("OR(") and rf.endswith(")"):
        inner = rf[3:-1]
        parts = [p.strip() for p in inner.split(",")]
        translated = []
        for p in parts:
            if p.startswith("width="):
                bps = p.split("=", 1)[1]
                translated.append(f"bollinger_width:window=30:num_std=1.5:min_width_bps={bps}")
            elif p == "trend_htf_long":
                translated.append(TREND_HTF_LONG)
            elif p == "trend_htf_short":
                translated.append(TREND_HTF_SHORT)
            else:
                return None
        return f"or({','.join(translated)})"
    # Ablations no stack_canonical: dropar componentes ou apertar.
    if rf == "ablation_no_filter":
        return None  # equivale a 'none' (sem filtro)
    if rf == "ablation_no_width":
        # stack v2 IS bollinger_width; sem width → none. Marca como ablation distinta via run-id.
        return None
    if rf == "ablation_no_trend_htf":
        # stack v2 não tem trend_htf → no-op, mantém bollinger_width canonical.
        return STACK_CANONICAL_FILTER
    if rf == "ablation_tight_width":
        return "bollinger_width:window=30:num_std=1.5:min_width_bps=300"
    if rf == "ablation_loose_width":
        return "bollinger_width:window=30:num_std=1.5:min_width_bps=150"
    # Filtros regime-meta (atr_expansion_50pct, trend_htf_4h_sma50_flat, realized_vol_percentile_70,
    # width_narrow_10m, funding_rate_extreme) requerem regime_meta engine — skip nesta fase.
    return "__UNSUPPORTED__"


def is_concrete(params: str) -> bool:
    return bool(CONCRETE_RE.fullmatch(params))


def parse_kv(params: str) -> dict[str, str]:
    return dict(kv.split("=", 1) for kv in params.split(","))


# Canonical defaults por engine (ADR-0028 stack v2 + ADR-0011/0008 baselines).
CANONICAL_DEFAULTS = {
    "bollinger": "window=20,num_std=2.0",
    "rsi": "period=14,os=30,ob=70",
    "ma_crossover": "short=20,long=50",
    "supertrend": "atr_period=10,atr_mult=3.0",
    "composite_bb_rsi": "bb_w=20,bb_ns=2.0,rsi_os=30,rsi_ob=70",
    "keltner": "window=20,atr_p=14,mult=2.5",
    "zscore": "window=20,threshold=2.5",
    # donchian usa entry/exit_window — handled em engine_args_for via override.
}


def resolve_canonical_params(engine: str, params: str) -> str | None:
    """Substitui 'canonical' pelos defaults da engine. Retorna None para skip."""
    if params != "canonical":
        return params
    return CANONICAL_DEFAULTS.get(engine)


PERTURB_RE = re.compile(r"^(\w+)\s*(\*=|\+=|-=)\s*([\d.]+)$")


def resolve_perturbation(engine: str, params: str) -> str | None:
    """Resolve perturbação relativa (`window *= 1.2`, `num_std += 0.25`) contra
    canonical defaults. Retorna params concretos ou None se não aplicável.
    """
    m = PERTURB_RE.match(params.strip())
    if not m:
        return None
    var, op, val_s = m.group(1), m.group(2), float(m.group(3))
    base = CANONICAL_DEFAULTS.get(engine)
    if not base:
        return None
    kv = parse_kv(base)
    # Map abstract perturbation var to engine's concrete key.
    target_key = None
    if var == "window":
        if "window" in kv: target_key = "window"
    elif var == "period":
        if "period" in kv: target_key = "period"
        elif "window" in kv: target_key = "window"  # bollinger: period→window alias
    elif var == "num_std":
        if "num_std" in kv: target_key = "num_std"
    if target_key is None:
        return None
    cur = float(kv[target_key])
    if op == "*=":
        new = cur * val_s
    elif op == "+=":
        new = cur + val_s
    elif op == "-=":
        new = cur - val_s
    else:
        return None
    # round int-typed keys
    if target_key in ("window", "period", "atr_p", "atr_period"):
        new = max(2, int(round(new)))
    kv[target_key] = str(new)
    return ",".join(f"{k}={v}" for k, v in kv.items())


def engine_args_for(engine: str, params: str) -> list[str] | None:
    # donchian canonical -> hard-coded entry/exit windows (ADR-0011)
    if engine == "donchian" and params == "canonical":
        return ["--strategy", "donchian", "--entry-window", "20", "--exit-window", "10"]
    kv = parse_kv(params)
    try:
        if engine == "bollinger":
            return ["--strategy", "bollinger",
                    "--bollinger-window", kv["window"],
                    "--bollinger-num-std", kv["num_std"]]
        if engine == "rsi":
            return ["--strategy", "rsi",
                    "--rsi-period", kv["period"],
                    "--rsi-oversold", kv["os"],
                    "--rsi-overbought", kv["ob"]]
        if engine == "ma_crossover":
            return ["--strategy", "ma_crossover", "--long-only",
                    "--short-window", kv["short"],
                    "--long-window", kv["long"]]
        if engine == "supertrend":
            return ["--strategy", "supertrend",
                    "--supertrend-atr-period", kv["atr_period"],
                    "--supertrend-atr-mult", kv["atr_mult"]]
        if engine == "composite_bb_rsi":
            return ["--strategy", "composite_bb_rsi",
                    "--composite-bb-window", kv["bb_w"],
                    "--composite-bb-num-std", kv["bb_ns"],
                    "--composite-rsi-period", "14",
                    "--composite-rsi-oversold", kv["rsi_os"],
                    "--composite-rsi-overbought", kv["rsi_ob"]]
        if engine == "keltner":
            return ["--strategy", "keltner",
                    "--keltner-window", kv["window"],
                    "--keltner-atr-period", kv["atr_p"],
                    "--keltner-mult", kv["mult"]]
        if engine == "zscore":
            return ["--strategy", "zscore",
                    "--zscore-window", kv["window"],
                    "--zscore-threshold", kv["threshold"]]
    except KeyError:
        return None
    return None


def resolve_dataset(asset: str, window: str, tf: str) -> str | None:
    table = DATASETS.get(asset)
    if not table:
        return None
    # window in roadmap is e.g. "2024-H2" or "10m-2024-H2"; tf is "1h" or "10m"
    key = window
    if tf == "10m" and not window.startswith("10m-"):
        key = f"10m-{window}"
    rec = table.get(key) or table.get(window)
    if not rec:
        return None
    return rec[0]


def make_run_id(entry: dict) -> str:
    e = entry["id"].lower().replace("_", "-")
    return f"r1k-{e}"[:120]


BASE_ARGS = [
    "alpha-forge", "validate",
    "--capital", "10000.0",
    "--fracao", "0.1",
    "--alavancagem", "2.0",
    "--sizing-mode", "fixed_notional",
    "--taker-fee-bps", "5.0",
    "--slippage-bps-per-notional", "2.0",
    "--spread-bps", "0.0",
    "--n-folds", "5",
    "--scheme", "rolling",
    "--train-fraction", "0.5",
    "--min-test-bars", "50",
    "--mc-resamples", "500",
    "--mc-seed", "42",
    "--log-level", "silent",
]


def build_argv(run_id: str, dataset: str, engine_args: list[str], cli_filter: str | None) -> list[str]:
    argv = BASE_ARGS + ["--run-id", run_id, "--dataset-id", dataset] + engine_args
    if cli_filter:
        argv += ["--regime-filter", cli_filter]
    return argv


def _annual_factor(tf: str) -> float:
    import math
    if tf == "10m":
        return math.sqrt(144 * 365)
    if tf == "1h":
        return math.sqrt(24 * 365)
    if tf == "15m":
        return math.sqrt(96 * 365)
    if tf == "4h":
        return math.sqrt(6 * 365)
    return math.sqrt(252)


def _compute_metrics(run_id: str, tf: str) -> dict:
    import math
    wf = json.loads((RESULTS / run_id / "walk_forward.json").read_text())
    folds = wf["payload"]
    all_trades: list[dict] = []
    full_eq = [10000.0]
    for f in folds:
        all_trades.extend(f["result"].get("trades", []) or [])
        ec_pairs = f["result"].get("equity_curve", []) or []
        ec_vals = [pair[1] for pair in ec_pairs]
        if ec_vals:
            base_eq = full_eq[-1]
            first = ec_vals[0] if ec_vals[0] != 0 else 10000.0
            for v in ec_vals:
                full_eq.append(base_eq * v / first)
    n_trades = len(all_trades)
    final_eq = full_eq[-1]
    pnl_pct = (final_eq / 10000.0 - 1) * 100
    rets = [
        (full_eq[i] / full_eq[i - 1] - 1)
        for i in range(1, len(full_eq))
        if full_eq[i - 1] > 0
    ]
    if len(rets) >= 2:
        mean = sum(rets) / len(rets)
        var = sum((r - mean) ** 2 for r in rets) / len(rets)
        sd = math.sqrt(var)
        sh = (mean / sd) * _annual_factor(tf) if sd > 0 else 0.0
    else:
        sh = 0.0
    # MDD over concatenated equity
    peak = full_eq[0]
    mdd = 0.0
    for v in full_eq:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > mdd:
            mdd = dd
    return {
        "trades": n_trades,
        "sharpe": round(sh, 4),
        "pnl_pct": round(pnl_pct, 4),
        "mdd_pct": round(mdd * 100, 4),
        "final_eq": round(final_eq, 2),
    }


def select_runnable(roadmap: list[dict], filter_set: str) -> list[dict]:
    out = []
    for e in roadmap:
        if e["engine"] not in SUPPORTED_ENGINES:
            continue
        # donchian é especial: 'canonical' direct via engine_args_for; outros params n/a aqui.
        if e["engine"] == "donchian":
            if e["params"] != "canonical":
                continue
            params = "canonical"
        else:
            params = resolve_canonical_params(e["engine"], e["params"])
            if params is None:
                continue
            if not is_concrete(params) and params != "canonical":
                resolved = resolve_perturbation(e["engine"], params)
                if resolved is None:
                    continue  # perturbação não mapeável (e.g. "threshold ± 5")
                params = resolved
            if params == "canonical":
                continue
        rf = e["regime_filter"]
        # filter_set gate
        if filter_set == "none":
            if rf != "none":
                continue
            cli_filter = None
        elif filter_set == "with_filter":
            if rf in ("none", "n/a"):
                continue
            cli_filter = translate_regime_filter(rf)
            if cli_filter is None or cli_filter == "__UNSUPPORTED__":
                continue
        elif filter_set == "all":
            cli_filter = translate_regime_filter(rf) if rf not in ("none", "n/a") else None
            if cli_filter == "__UNSUPPORTED__":
                continue
        else:
            continue
        ds = resolve_dataset(e["asset"], e["window"], e.get("timeframe", "1h"))
        if not ds:
            continue
        # Re-resolve canonical because donchian gets handled inside engine_args_for
        eargs = engine_args_for(e["engine"], e["params"] if e["engine"] == "donchian" else params)
        if eargs is None:
            continue
        out.append({**e, "_dataset": ds, "_engine_args": eargs, "_cli_filter": cli_filter, "_resolved_params": params})
    return out


def load_progress() -> dict[str, dict]:
    if not PROGRESS.exists():
        return {}
    try:
        return json.loads(PROGRESS.read_text())
    except Exception:
        return {}


def save_progress(prog: dict) -> None:
    PROGRESS.write_text(json.dumps(prog, indent=2))


def run_one(work: dict) -> dict:
    run_id = make_run_id(work)
    argv = build_argv(run_id, work["_dataset"], work["_engine_args"], work.get("_cli_filter"))
    code = (
        "import sys; "
        f"sys.argv = {argv!r}; "
        "from alpha_forge.cli.app import main; "
        "main()"
    )
    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(ROOT),
            capture_output=True, text=True, timeout=1800,
        )
        ok = proc.returncode == 0
        err = proc.stderr[-2000:] if not ok else ""
    except subprocess.TimeoutExpired:
        ok, err = False, "TIMEOUT_30min"
    dt = time.time() - t0

    metrics = {}
    if ok:
        try:
            metrics = _compute_metrics(run_id, work.get("timeframe", "1h"))
        except Exception as exc:
            metrics = {"_summary_err": str(exc)}
    return {
        "id": work["id"], "run_id": run_id, "ok": ok, "elapsed_s": round(dt, 1),
        "engine": work["engine"], "asset": work["asset"], "window": work["window"],
        "tier": work["tier"], "params": work["params"], "metrics": metrics,
        "error": err if not ok else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--filter-set", default="none", choices=["none", "with_filter", "all"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    roadmap = json.loads(ROADMAP.read_text())
    candidates = select_runnable(roadmap, args.filter_set)

    progress = load_progress()
    todo = [c for c in candidates if c["id"] not in progress]
    if args.limit:
        todo = todo[: args.limit]

    print(f"[auto] roadmap={len(roadmap)} candidates(filter={args.filter_set})={len(candidates)} "
          f"already_done={len(progress)} todo={len(todo)} workers={args.workers}",
          flush=True)
    if args.dry_run:
        for c in todo[:5]:
            print(f"  preview: {c['id']} ds={c['_dataset']} args={c['_engine_args']}")
        return 0
    if not todo:
        print("[auto] nada a fazer.")
        return 0

    t_start = time.time()
    n_done = 0
    n_pass = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_one, w): w for w in todo}
        for fut in as_completed(futs):
            res = fut.result()
            progress[res["id"]] = res
            save_progress(progress)
            n_done += 1
            sh = (res.get("metrics") or {}).get("sharpe")
            tr = (res.get("metrics") or {}).get("trades")
            gate = bool(sh and tr and sh >= 1.5 and tr >= 30)
            if gate: n_pass += 1
            elapsed = time.time() - t_start
            avg = elapsed / max(n_done, 1)
            eta_s = (len(todo) - n_done) * avg / max(args.workers, 1)
            print(f"[{n_done}/{len(todo)}] ok={res['ok']} {res['id']} "
                  f"sh={sh} tr={tr} elapsed={res['elapsed_s']}s "
                  f"wall_avg={avg:.0f}s eta={eta_s/60:.0f}min pass={n_pass}",
                  flush=True)

    print(f"[auto] DONE wall={time.time()-t_start:.0f}s pass={n_pass}/{n_done}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
