"""Compara CG/CH fixed vs snowball (ADR-0063).

Aplica gate manifest + gate adicional snowball (MDD snow <= MDD fixed * 1.5).
Emite tabela e decide promocao v3b/v4b por combo.
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
    pnl_usd = 2000.0 * (final_eq / 10000.0 - 1.0)
    return dict(trades=n_trades, sharpe=sharpe, mdd_pct=mdd,
                final_eq=final_eq, cost_r=cost_r, mc_p5=mc_p5, pnl_usd=pnl_usd)


def gate_manifest(m: dict) -> tuple[bool, list[str]]:
    fail = []
    if m["trades"] < 30:
        fail.append("trades")
    if m["sharpe"] < 1.0:
        fail.append("Sharpe")
    if m["mdd_pct"] > 20:
        fail.append("MDD")
    if m["mc_p5"] <= 9500:
        fail.append("MCp5")
    if m["cost_r"] < 0.95:
        fail.append("cost_r")
    return len(fail) == 0, fail


def load(rid: str) -> dict | None:
    base = Path("results/validation") / rid
    wf_p = base / "walk_forward.json"
    mc_p = base / "monte_carlo.json"
    cs_p = base / "cost_stress.json"
    if not (wf_p.exists() and mc_p.exists() and cs_p.exists()):
        return None
    return metrics(wf_p, mc_p, cs_p)


def compare_series(series_name: str, pilots: list[tuple[str, str, str]], fixed_rid_fn, snow_rid_fn) -> dict:
    print(f"\n=== {series_name} fixed vs snowball ===")
    header = f'{"Tag":6}{"Asset":6}{"Period":10}{"mode":6}{"trd":>5}{"Sh":>7}{"MDD%":>7}{"fe":>9}{"cost_r":>8}{"MCp5":>9}{"USD$":>10}  gate  snow_mdd_ok'
    print(header)
    print("-" * len(header))
    results = []
    snow_candidates = 0
    for tag, asset, suffix in pilots:
        m_fx = load(fixed_rid_fn(asset, suffix))
        m_sn = load(snow_rid_fn(asset, suffix))
        if m_fx is None or m_sn is None:
            print(f"{tag} MISSING")
            continue
        ok_fx, fail_fx = gate_manifest(m_fx)
        ok_sn, fail_sn = gate_manifest(m_sn)
        snow_mdd_ok = m_sn["mdd_pct"] <= m_fx["mdd_pct"] * 1.5 + 1e-9
        snow_passes_dual = ok_sn and snow_mdd_ok and m_sn["pnl_usd"] > m_fx["pnl_usd"]
        if snow_passes_dual and ok_fx:
            snow_candidates += 1
        v_fx = "PASS" if ok_fx else "FAIL(" + ",".join(fail_fx) + ")"
        v_sn = "PASS" if ok_sn else "FAIL(" + ",".join(fail_sn) + ")"
        mdd_tag = "ok" if snow_mdd_ok else "BREACH"
        print(f'{tag:6}{asset:6}{suffix[:8]:10}{"fix":6}{m_fx["trades"]:>5}{m_fx["sharpe"]:>7.2f}{m_fx["mdd_pct"]:>7.2f}{m_fx["final_eq"]:>9.0f}{m_fx["cost_r"]:>8.4f}{m_fx["mc_p5"]:>9.0f}{m_fx["pnl_usd"]:>10.2f}  {v_fx}')
        print(f'{tag:6}{"":6}{"":10}{"snow":6}{m_sn["trades"]:>5}{m_sn["sharpe"]:>7.2f}{m_sn["mdd_pct"]:>7.2f}{m_sn["final_eq"]:>9.0f}{m_sn["cost_r"]:>8.4f}{m_sn["mc_p5"]:>9.0f}{m_sn["pnl_usd"]:>10.2f}  {v_sn}  mdd={mdd_tag}')
        results.append(dict(
            tag=tag, asset=asset, period=suffix,
            fixed=m_fx, snowball=m_sn,
            fixed_pass=ok_fx, snow_pass=ok_sn, snow_mdd_ok=snow_mdd_ok,
            snow_candidate=snow_passes_dual and ok_fx,
        ))
    print(f"\n{series_name} snowball promocao candidates: {snow_candidates}/{len(pilots)}")
    return {"series": series_name, "snow_candidates": snow_candidates, "pilots": results}


if __name__ == "__main__":
    PILOTS = [
        ("CX.1", "btc", "20240705_20241231"),
        ("CX.2", "eth", "20240705_20241231"),
        ("CX.3", "sol", "20240705_20241231"),
        ("CX.4", "btc", "20250105_20250704"),
        ("CX.5", "eth", "20250105_20250704"),
        ("CX.6", "sol", "20250105_20250704"),
        ("CX.7", "btc", "20250705_20251231"),
        ("CX.8", "eth", "20250705_20251231"),
        ("CX.9", "sol", "20250705_20251231"),
    ]

    cg_pilots = [(f"CG.{t.split('.')[1]}", a, s) for t, a, s in PILOTS]
    ch_pilots = [(f"CH.{t.split('.')[1]}", a, s) for t, a, s in PILOTS]

    cg_result = compare_series(
        "CG (Bollinger short + width 300)", cg_pilots,
        fixed_rid_fn=lambda a, s: f"cg-bol-20-15-{a}-{s}-width30-300-short",
        snow_rid_fn=lambda a, s: f"cg-snow-bol-20-15-{a}-{s}-width30-300-short",
    )
    ch_result = compare_series(
        "CH (RSI short + width 300)", ch_pilots,
        fixed_rid_fn=lambda a, s: f"ch-rsi-14-30-70-{a}-{s}-width30-300-short",
        snow_rid_fn=lambda a, s: f"ch-snow-rsi-14-30-70-{a}-{s}-width30-300-short",
    )

    # Totais USD
    print("\n=== Totais USD por manifest (4 combos aprovados fixed) ===")
    def sum_for(tag_filter, pilot_results):
        total_fx = sum(p["fixed"]["pnl_usd"] for p in pilot_results if p["fixed_pass"])
        total_sn = sum(p["snowball"]["pnl_usd"] for p in pilot_results if p["fixed_pass"])
        return total_fx, total_sn

    cg_tot_fx, cg_tot_sn = sum_for("CG", cg_result["pilots"])
    ch_tot_fx, ch_tot_sn = sum_for("CH", ch_result["pilots"])
    print(f"CG (Bollinger short): fixed=${cg_tot_fx:+.2f}  snowball=${cg_tot_sn:+.2f}  delta={cg_tot_sn-cg_tot_fx:+.2f}")
    print(f"CH (RSI short):       fixed=${ch_tot_fx:+.2f}  snowball=${ch_tot_sn:+.2f}  delta={ch_tot_sn-ch_tot_fx:+.2f}")
    print(f"Combined delta: {(cg_tot_sn-cg_tot_fx) + (ch_tot_sn-ch_tot_fx):+.2f}")

    out_p = Path("exports/diag/snowball_vs_fixed_summary.json")
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps({
        "adr": "0063",
        "cg": cg_result,
        "ch": ch_result,
        "totals_usd": {
            "cg_fixed": cg_tot_fx, "cg_snowball": cg_tot_sn,
            "ch_fixed": ch_tot_fx, "ch_snowball": ch_tot_sn,
        },
    }, indent=2, default=float))
    print(f"\n-> saved {out_p}")
