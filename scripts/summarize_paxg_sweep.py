"""Resumo agregado dos runs paxg_* (re-lê artefatos já gravados)."""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

WINDOWS = ["2023h2", "2024h1", "2024h2", "2025h1", "2025h2"]
STRATS = ["rsi_long_pure", "rsi_short_pure", "bb_long_mr", "bb_short_mr"]
RESULTS = Path("results/validation")
CAPITAL = 10_000.0
BARS_PER_YEAR_1H = 24 * 365


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fold_sharpe(trades: list[dict], bars_test: int) -> float | None:
    """Sharpe aproximado dos retornos por trade (rel. ao capital), anualizado.

    Aproximação: r_i = pnl_i / capital_inicial; sharpe = mean/std * sqrt(N/T_years)
    onde N = número de trades e T_years = bars_test / bars_per_year.
    """
    if not trades:
        return None
    rets = [t["pnl"] / CAPITAL for t in trades]
    if len(rets) < 2:
        return None
    mu = statistics.mean(rets)
    sd = statistics.pstdev(rets)
    if sd == 0:
        return None
    years = bars_test / BARS_PER_YEAR_1H
    if years <= 0:
        return None
    return mu / sd * math.sqrt(len(rets) / years)


def summarize(run_dir: Path) -> dict:
    wf = load(run_dir / "walk_forward.json")["payload"]
    trades_all: list[dict] = []
    total_trades = 0
    total_pnl = 0.0
    hit_count = 0
    wins = 0
    bars_total = 0
    fold_sharpes: list[float] = []
    for f in wf:
        result = f["result"]
        m = result.get("metrics") or {}
        tn = m.get("trade_count", 0)
        total_trades += tn
        total_pnl += m.get("total_pnl", 0.0)
        ftrades = result.get("trades", [])
        trades_all.extend(ftrades)
        wins += sum(1 for t in ftrades if t["pnl"] > 0)
        bars_total += f["test_window"]["bars"]
        s = fold_sharpe(ftrades, f["test_window"]["bars"])
        if s is not None:
            fold_sharpes.append(s)
    hit_rate = wins / total_trades if total_trades else None

    # MDD: reconstrução do equity via trades aggregados OOS
    eq = CAPITAL
    peak = eq
    mdd = 0.0
    for t in sorted(trades_all, key=lambda x: x.get("exit_timestamp", x.get("entry_timestamp"))):
        eq += t["pnl"]
        peak = max(peak, eq)
        if peak > 0:
            dd = (peak - eq) / peak
            mdd = max(mdd, dd)
    mdd_pct = mdd * 100

    # Sharpe agregado sobre OOS
    oos_sharpe = fold_sharpe(trades_all, bars_total)

    # Monte Carlo
    mc_path = run_dir / "monte_carlo.json"
    mc_median = mc_p5 = None
    if mc_path.exists():
        mc = load(mc_path)["payload"]
        pcts = mc.get("final_equity_percentiles") or {}
        mc_median = pcts.get("50")
        mc_p5 = pcts.get("5")

    # Cost stress
    cs_path = run_dir / "cost_stress.json"
    cs_min_ratio = None
    baseline_total_pnl = None
    if cs_path.exists():
        cs = load(cs_path)["payload"]
        bm = cs["baseline"]["result"]["metrics"]
        baseline_total_pnl = bm.get("total_pnl")
        ratios = []
        for s in cs["scenarios"]:
            sm = s["result"]["metrics"]
            s_pnl = sm.get("total_pnl", 0.0)
            if baseline_total_pnl and baseline_total_pnl != 0:
                ratios.append(s_pnl / baseline_total_pnl)
        if ratios:
            cs_min_ratio = min(ratios)

    pnl_pct = (total_pnl / CAPITAL) * 100

    return {
        "oos_trades": total_trades,
        "oos_pnl_pct": round(pnl_pct, 3),
        "oos_hit_rate": round(hit_rate, 3) if hit_rate is not None else None,
        "oos_sharpe_agg": round(oos_sharpe, 3) if oos_sharpe is not None else None,
        "oos_mdd_pct": round(mdd_pct, 3),
        "mc_median_final": mc_median,
        "mc_p5_final": mc_p5,
        "cost_stress_min_ratio": round(cs_min_ratio, 3) if cs_min_ratio is not None else None,
        "cs_baseline_pnl": round(baseline_total_pnl, 2) if baseline_total_pnl is not None else None,
    }


def approved_gate(row: dict) -> str:
    """Regra de aprovação v3 (AGENTS §8): Sh>=1.0, MDD<=20, PnL>0, trades>=30, CS_ratio>=0.95."""
    reasons = []
    s = row["oos_sharpe_agg"]
    if s is None or s < 1.0:
        reasons.append(f"Sh={s}")
    if row["oos_mdd_pct"] > 20:
        reasons.append(f"MDD={row['oos_mdd_pct']}")
    if row["oos_pnl_pct"] <= 0:
        reasons.append(f"PnL={row['oos_pnl_pct']}")
    if row["oos_trades"] < 30:
        reasons.append(f"N={row['oos_trades']}")
    cs = row["cost_stress_min_ratio"]
    if cs is None or cs < 0.95:
        reasons.append(f"CS={cs}")
    return "PASS" if not reasons else "FAIL:" + ",".join(reasons)


def main() -> int:
    rows = []
    for win in WINDOWS:
        for st in STRATS:
            rid = f"paxg_{st}_{win}"
            d = RESULTS / rid
            if not (d / "walk_forward.json").exists():
                continue
            r = summarize(d)
            r["run_id"] = rid
            r["window"] = win
            r["strategy"] = st
            r["verdict"] = approved_gate(r)
            rows.append(r)

    out = Path("results/paxg_sweep_summary.json")
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    # Print compact table
    hdr = f"{'window':<8} {'strategy':<16} {'N':>4} {'PnL%':>8} {'HR':>6} {'Sharpe':>7} {'MDD%':>6} {'CS':>6} {'verdict':<40}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['window']:<8} {r['strategy']:<16} {r['oos_trades']:>4} "
              f"{r['oos_pnl_pct']:>8.2f} "
              f"{(r['oos_hit_rate'] or 0):>6.3f} "
              f"{(r['oos_sharpe_agg'] if r['oos_sharpe_agg'] is not None else 0):>7.2f} "
              f"{r['oos_mdd_pct']:>6.2f} "
              f"{(r['cost_stress_min_ratio'] if r['cost_stress_min_ratio'] is not None else 0):>6.2f} "
              f"{r['verdict']:<40}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
