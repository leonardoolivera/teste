"""Extrai metrics da Serie CB e avalia gates pre-registrados ADR-0041."""
from __future__ import annotations

import json
import math
from pathlib import Path


def annual_sharpe(returns: list[float]) -> float:
    n = len(returns)
    if n < 2:
        return 0.0
    mean = sum(returns) / n
    var = sum((r - mean) ** 2 for r in returns) / n
    sd = math.sqrt(var)
    if sd == 0:
        return 0.0
    return (mean / sd) * math.sqrt(24 * 365)


def metrics(wf_p: Path, mc_p: Path, cs_p: Path) -> dict:
    wf = json.loads(wf_p.read_text())
    folds = wf["payload"]
    all_trades = []
    full_eq = [10000.0]
    for f in folds:
        all_trades.extend(f["result"].get("trades", []))
        ec_pairs = f["result"].get("equity_curve", [])
        ec_vals = [p[1] for p in ec_pairs]
        if ec_vals:
            base_eq = full_eq[-1]
            first = ec_vals[0] if ec_vals[0] != 0 else 10000.0
            for v in ec_vals:
                full_eq.append(base_eq * v / first)
    n_trades = len(all_trades)
    final_eq = full_eq[-1]
    rets = [(full_eq[i] / full_eq[i - 1] - 1) for i in range(1, len(full_eq)) if full_eq[i - 1] > 0]
    sharpe = annual_sharpe(rets)
    peak = full_eq[0]
    mdd = 0.0
    for v in full_eq:
        peak = max(peak, v)
        dd = (peak - v) / peak * 100
        mdd = max(mdd, dd)
    mc = json.loads(mc_p.read_text())["payload"]
    mc_p5 = mc["final_equity_percentiles"]["5"]
    mc_mdd_p95 = mc["max_drawdown_percentiles"]["95"] * 100
    cs_payload = json.loads(cs_p.read_text())["payload"]
    base_fe = cs_payload["baseline"]["result"]["final_equity"]
    stress_fes = [s["result"]["final_equity"] for s in cs_payload["scenarios"]]
    cost_r = min((sfe / base_fe) for sfe in stress_fes) if stress_fes and base_fe > 0 else 0.0
    return dict(trades=n_trades, sharpe=sharpe, mdd_pct=mdd,
                final_eq=final_eq, cost_r=cost_r, mc_p5=mc_p5, mc_mdd_p95=mc_mdd_p95)


def evaluate_gates_cb(m: dict) -> tuple[bool, list[str]]:
    """Gate ADR-0041: trades>=30, Sharpe>=1.0, MDD<=20%, fe>9800, cost_r>=0.95, MC_p5>9200."""
    fail = []
    if m["trades"] < 30:
        fail.append("trades")
    if m["sharpe"] < 1.0:
        fail.append("Sharpe")
    if m["mdd_pct"] > 20:
        fail.append("MDD")
    if m["final_eq"] <= 9800:
        fail.append("fe")
    if m["cost_r"] < 0.95:
        fail.append("cost_r")
    if m["mc_p5"] <= 9200:
        fail.append("MCp5")
    return len(fail) == 0, fail


if __name__ == "__main__":
    base = Path("results/validation")
    PILOTS = [
        ("CB.1", "eth", "20230705_20231231", 105),
        ("CB.2", "btc", "20230705_20231231", 55),
        ("CB.3", "sol", "20230705_20231231", 100),
        ("CB.4", "eth", "20250105_20250704", 105),
        ("CB.5", "btc", "20250105_20250704", 55),
        ("CB.6", "sol", "20250105_20250704", 100),
        ("CB.7", "eth", "20250705_20251231", 105),
        ("CB.8", "btc", "20250705_20251231", 55),
        ("CB.9", "sol", "20250705_20251231", 100),
    ]
    print("\n=== Serie CB — RSI cross-period (ADR-0041 gate) ===")
    print(f'{"Tag":6}{"Asset":6}{"Period":20}{"atrbps":>7}{"trd":>5}{"Sh":>7}{"MDD%":>7}{"fe":>9}{"cost_r":>8}{"MCp5":>9}  verdict')
    print("-" * 114)
    results = []
    passes = 0
    for tag, asset, suffix, atr_bps in PILOTS:
        run_id = f"cb-rsi-14-30-70-{asset}-{suffix}-atrbps{atr_bps}"
        out = base / run_id
        wf_p, mc_p, cs_p = out / "walk_forward.json", out / "monte_carlo.json", out / "cost_stress.json"
        if not (wf_p.exists() and mc_p.exists() and cs_p.exists()):
            print(f"{tag} MISSING")
            continue
        m = metrics(wf_p, mc_p, cs_p)
        ok, fail = evaluate_gates_cb(m)
        verdict = "PASS" if ok else "FAIL(" + ",".join(fail) + ")"
        if ok:
            passes += 1
        print(f'{tag:6}{asset:6}{suffix:20}{atr_bps:>7}{m["trades"]:>5}{m["sharpe"]:>7.2f}{m["mdd_pct"]:>7.2f}{m["final_eq"]:>9.0f}{m["cost_r"]:>8.4f}{m["mc_p5"]:>9.0f}  {verdict}')
        results.append(dict(tag=tag, asset=asset, period=suffix, atr_bps=atr_bps,
                            **{k: round(v, 4) if isinstance(v, float) else v for k, v in m.items()},
                            verdict="PASS" if ok else "FAIL", fail_reasons=fail))
    print("-" * 114)
    print(f"\nPASS count: {passes}/9 (gate ADR-0041: >=6 required)")
    print(f"SERIE VERDICT: {'PASS' if passes >= 6 else 'FAIL'}")
    out_p = Path("exports/diag/cb_series_summary.json")
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps({"gate_adr": "0041", "passes": passes, "total": 9,
                                  "series_verdict": "PASS" if passes >= 6 else "FAIL",
                                  "pilots": results}, indent=2))
    print(f"-> saved {out_p}")
