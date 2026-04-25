"""Serie CF summary — aplica Gates 1-3 de ADR-0054 (Bollinger short + width)."""
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


def evaluate_gate1(m: dict) -> tuple[bool, list[str]]:
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


if __name__ == "__main__":
    base = Path("results/validation")
    PILOTS = [
        ("CF.1", "btc", "20240705_20241231", "2024-H2"),
        ("CF.2", "eth", "20240705_20241231", "2024-H2"),
        ("CF.3", "sol", "20240705_20241231", "2024-H2"),
        ("CF.4", "btc", "20250105_20250704", "2025-H1"),
        ("CF.5", "eth", "20250105_20250704", "2025-H1"),
        ("CF.6", "sol", "20250105_20250704", "2025-H1"),
        ("CF.7", "btc", "20250705_20251231", "2025-H2"),
        ("CF.8", "eth", "20250705_20251231", "2025-H2"),
        ("CF.9", "sol", "20250705_20251231", "2025-H2"),
    ]
    print("\n=== Serie CF — Bollinger short + width filter (ADR-0054 gates) ===")
    header = f'{"Tag":6}{"Asset":6}{"Period":10}{"trd":>5}{"Sh":>7}{"MDD%":>7}{"fe":>9}{"cost_r":>8}{"MCp5":>9}  vs CE  verdict'
    print(header)
    print("-" * len(header))

    pilots_out = []
    g1_passes = 0
    g2_lift_cost_r = 0  # filter > CE cost_r
    g3_bull_h2_passes = 0
    for tag, asset, suffix, regime in PILOTS:
        rid_cf = f"cf-bol-20-15-{asset}-{suffix}-width30-250-short"
        rid_ce = f"ce-bol-20-15-{asset}-{suffix}-short"
        out_cf = base / rid_cf
        out_ce = base / rid_ce
        wf_p, mc_p, cs_p = out_cf / "walk_forward.json", out_cf / "monte_carlo.json", out_cf / "cost_stress.json"
        if not (wf_p.exists() and mc_p.exists() and cs_p.exists()):
            print(f"{tag} MISSING")
            continue
        m = metrics(wf_p, mc_p, cs_p)
        ce_wf, ce_mc, ce_cs = out_ce / "walk_forward.json", out_ce / "monte_carlo.json", out_ce / "cost_stress.json"
        ce_m = None
        if ce_wf.exists() and ce_mc.exists() and ce_cs.exists():
            ce_m = metrics(ce_wf, ce_mc, ce_cs)
        ok, fail = evaluate_gate1(m)
        verdict = "PASS" if ok else "FAIL(" + ",".join(fail) + ")"
        if ok:
            g1_passes += 1
            if regime == "2024-H2":
                g3_bull_h2_passes += 1
        vs_ce = ""
        if ce_m is not None:
            lift_cost_r = m["cost_r"] > ce_m["cost_r"]
            if lift_cost_r:
                g2_lift_cost_r += 1
            vs_ce = f"{'+' if lift_cost_r else '-'}cr"
        pilots_out.append(dict(
            tag=tag, asset=asset, period=suffix, regime=regime,
            cf_metrics=m, ce_metrics=ce_m, pass_gate1=ok, fail_reasons=fail,
        ))
        print(f'{tag:6}{asset:6}{regime:10}{m["trades"]:>5}{m["sharpe"]:>7.2f}{m["mdd_pct"]:>7.2f}{m["final_eq"]:>9.0f}{m["cost_r"]:>8.4f}{m["mc_p5"]:>9.0f}  {vs_ce:5}  {verdict}')

    print("-" * len(header))

    g1_ok = g1_passes >= 3
    g2_ok = g2_lift_cost_r >= 6
    g3_ok = g3_bull_h2_passes <= 1  # falsificacionista

    print(f"\nGate 1 (principal, >=3/9 passam criterio manifest): {g1_passes}/9 -> {'PASS' if g1_ok else 'FAIL'}")
    print(f"Gate 2 (lift cost_r vs CE, >=6/9): {g2_lift_cost_r}/9 -> {'PASS' if g2_ok else 'FAIL'}")
    print(f"Gate 3 (falsificacionista, <=1/3 em 2024-H2 bull): {g3_bull_h2_passes}/3 -> {'PASS' if g3_ok else 'FAIL (investigar!)'}")

    overall = "PASS" if (g1_ok and g3_ok) else "FAIL"
    print(f"\nSERIE CF VERDICT (Gate1 + Gate3 coerencia): {overall}")
    if overall == "PASS":
        print("  => Short composicional com width eh material. Proxima ADR: promocao pra manifest v3.")
    else:
        if g2_ok:
            print("  => Filtro eh load-bearing (lift cost_r OK) mas nao suficiente pra promover. Considerar num_std ou min_width alternativos em ADR futura (fora do gate atual).")
        else:
            print("  => Filtro nao eh load-bearing pra short. Mean-rev short arquivada. Pivotar pra ADR-0050 §D3/§D5.")

    out_p = Path("exports/diag/cf_series_summary.json")
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps({
        "gate_adr": "0054",
        "g1_passes_of_9": g1_passes,
        "g2_lift_cost_r": g2_lift_cost_r,
        "g3_bull_h2_passes": g3_bull_h2_passes,
        "gate1": "PASS" if g1_ok else "FAIL",
        "gate2": "PASS" if g2_ok else "FAIL",
        "gate3": "PASS" if g3_ok else "FAIL",
        "overall": overall,
        "pilots": pilots_out,
    }, indent=2, default=float))
    print(f"-> saved {out_p}")
