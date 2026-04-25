"""Extrai metrics da Serie CC e avalia gates pre-registrados ADR-0044.

Gate 1-6: trades>=25, Sharpe>=1.0, MDD<=20%, fe>9800, cost_r>=0.95, MC_p5>9200 em >=6/9.
Gate 7 (lift): em >=5/9, filtered tem fe > baseline OR mdd < baseline.
"""
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
    cs_payload = json.loads(cs_p.read_text())["payload"]
    base_fe = cs_payload["baseline"]["result"]["final_equity"]
    stress_fes = [s["result"]["final_equity"] for s in cs_payload["scenarios"]]
    cost_r = min((sfe / base_fe) for sfe in stress_fes) if stress_fes and base_fe > 0 else 0.0
    return dict(trades=n_trades, sharpe=sharpe, mdd_pct=mdd,
                final_eq=final_eq, cost_r=cost_r, mc_p5=mc_p5)


def evaluate_gates_cc(m: dict) -> tuple[bool, list[str]]:
    fail = []
    if m["trades"] < 25:
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
        ("CC.1", "eth", "20230705_20231231", 105),
        ("CC.2", "btc", "20230705_20231231", 55),
        ("CC.3", "sol", "20230705_20231231", 100),
        ("CC.4", "eth", "20250105_20250704", 105),
        ("CC.5", "btc", "20250105_20250704", 55),
        ("CC.6", "sol", "20250105_20250704", 100),
        ("CC.7", "eth", "20250705_20251231", 105),
        ("CC.8", "btc", "20250705_20251231", 55),
        ("CC.9", "sol", "20250705_20251231", 100),
    ]
    print("\n=== Serie CC — Bollinger + trend_htf cross-period (ADR-0044 gate 1-6) ===")
    print(f'{"Tag":6}{"Asset":6}{"Period":20}{"variant":10}{"trd":>5}{"Sh":>7}{"MDD%":>7}{"fe":>9}{"cost_r":>8}{"MCp5":>9}  verdict')
    print("-" * 118)
    results = []
    passes_filtered = 0
    lift_count = 0
    for tag, asset, suffix, atr_bps in PILOTS:
        rid_f = f"cc-boll-20-15-{asset}-{suffix}-atr{atr_bps}-htf4h50"
        rid_b = f"cc-boll-20-15-{asset}-{suffix}-atr{atr_bps}-baseline"
        pair = {}
        for variant, rid in (("filt", rid_f), ("base", rid_b)):
            out = base / rid
            wf_p, mc_p, cs_p = out / "walk_forward.json", out / "monte_carlo.json", out / "cost_stress.json"
            if not (wf_p.exists() and mc_p.exists() and cs_p.exists()):
                print(f"{tag} {variant} MISSING")
                continue
            m = metrics(wf_p, mc_p, cs_p)
            pair[variant] = m
            if variant == "filt":
                ok, fail = evaluate_gates_cc(m)
                verdict = "PASS" if ok else "FAIL(" + ",".join(fail) + ")"
                if ok:
                    passes_filtered += 1
            else:
                verdict = "(baseline)"
            print(f'{tag:6}{asset:6}{suffix:20}{variant:10}{m["trades"]:>5}{m["sharpe"]:>7.2f}{m["mdd_pct"]:>7.2f}{m["final_eq"]:>9.0f}{m["cost_r"]:>8.4f}{m["mc_p5"]:>9.0f}  {verdict}')
        if "filt" in pair and "base" in pair:
            lift_fe = pair["filt"]["final_eq"] > pair["base"]["final_eq"]
            lift_mdd = pair["filt"]["mdd_pct"] < pair["base"]["mdd_pct"]
            has_lift = lift_fe or lift_mdd
            if has_lift:
                lift_count += 1
            results.append(dict(
                tag=tag, asset=asset, period=suffix, atr_bps=atr_bps,
                filtered=pair["filt"], baseline=pair["base"],
                lift_fe=lift_fe, lift_mdd=lift_mdd, has_lift=has_lift,
            ))
    print("-" * 118)
    print(f"\nGate 1-6 (filtered >=6/9): {passes_filtered}/9 -> {'PASS' if passes_filtered >= 6 else 'FAIL'}")
    print(f"Gate 7 lift (filt>base in fe OR mdd, >=5/9): {lift_count}/9 -> {'PASS' if lift_count >= 5 else 'FAIL'}")
    verdict_principal = "PASS" if passes_filtered >= 6 else "FAIL"
    verdict_lift = "PASS" if lift_count >= 5 else "FAIL"
    print(f"\nSERIE CC VERDICT: principal={verdict_principal}, lift={verdict_lift}")
    out_p = Path("exports/diag/cc_series_summary.json")
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps({
        "gate_adr": "0044",
        "passes_filtered": passes_filtered,
        "lift_count": lift_count,
        "verdict_principal": verdict_principal,
        "verdict_lift": verdict_lift,
        "pilots": results,
    }, indent=2, default=float))
    print(f"-> saved {out_p}")
