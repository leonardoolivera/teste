"""Serie CE summary — aplica Gates 1-4 de ADR-0052 (short side cross-period)."""
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
        ("CE.1", "btc", "20240705_20241231", "2024-H2"),
        ("CE.2", "eth", "20240705_20241231", "2024-H2"),
        ("CE.3", "sol", "20240705_20241231", "2024-H2"),
        ("CE.4", "btc", "20250105_20250704", "2025-H1"),
        ("CE.5", "eth", "20250105_20250704", "2025-H1"),
        ("CE.6", "sol", "20250105_20250704", "2025-H1"),
        ("CE.7", "btc", "20250705_20251231", "2025-H2"),
        ("CE.8", "eth", "20250705_20251231", "2025-H2"),
        ("CE.9", "sol", "20250705_20251231", "2025-H2"),
    ]
    STRATEGIES = [
        ("bol", "bollinger-20-1.5", "ce-bol-20-15-{asset}-{suffix}-short"),
        ("rsi", "rsi-14-30-70", "ce-rsi-14-30-70-{asset}-{suffix}-short"),
    ]

    print("\n=== Serie CE — Bollinger + RSI short side (ADR-0052 gates) ===")
    header = f'{"Tag":6}{"Strat":7}{"Asset":6}{"Period":10}{"trd":>5}{"Sh":>7}{"MDD%":>7}{"fe":>9}{"cost_r":>8}{"MCp5":>9}  verdict'
    print(header)
    print("-" * len(header))

    pilots_out = []
    g1_passes = 0
    g2_passes_in_bull_h2 = 0  # Gate 2: 2024-H2 passes
    g3_passes_in_chop_h1 = 0  # Gate 3: 2025-H1 passes
    bol_passes = 0
    rsi_passes = 0

    for tag, asset, suffix, regime in PILOTS:
        for sk, sname, rid_tpl in STRATEGIES:
            rid = rid_tpl.format(asset=asset, suffix=suffix)
            out = base / rid
            wf_p, mc_p, cs_p = out / "walk_forward.json", out / "monte_carlo.json", out / "cost_stress.json"
            if not (wf_p.exists() and mc_p.exists() and cs_p.exists()):
                print(f"{tag:6}{sk:7}{asset:6}{regime:10} MISSING")
                continue
            m = metrics(wf_p, mc_p, cs_p)
            ok, fail = evaluate_gate1(m)
            verdict = "PASS" if ok else "FAIL(" + ",".join(fail) + ")"
            if ok:
                g1_passes += 1
                if regime == "2024-H2":
                    g2_passes_in_bull_h2 += 1
                if regime == "2025-H1":
                    g3_passes_in_chop_h1 += 1
                if sk == "bol":
                    bol_passes += 1
                else:
                    rsi_passes += 1
            pilots_out.append(dict(
                tag=tag, strategy=sk, asset=asset, period=suffix, regime=regime,
                metrics=m, pass_gate1=ok, fail_reasons=fail,
            ))
            print(f'{tag:6}{sk:7}{asset:6}{regime:10}{m["trades"]:>5}{m["sharpe"]:>7.2f}{m["mdd_pct"]:>7.2f}{m["final_eq"]:>9.0f}{m["cost_r"]:>8.4f}{m["mc_p5"]:>9.0f}  {verdict}')

    print("-" * len(header))

    g1_ok = g1_passes >= 6
    # Gate 2 é falsificacionista: <=1/6 em bull H2. Fail = >=2 passes em H2 (indica ruído).
    g2_ok = g2_passes_in_bull_h2 <= 1
    g3_ok = g3_passes_in_chop_h1 >= 3
    asymmetry = abs(bol_passes - rsi_passes)

    print(f"\nGate 1 (principal, >=6/18 passam criterio manifest): {g1_passes}/18 -> {'PASS' if g1_ok else 'FAIL'}")
    print(f"Gate 2 (falsificacionista, <=1/6 em 2024-H2 bull): {g2_passes_in_bull_h2}/6 -> {'PASS' if g2_ok else 'FAIL (investigar!)'}")
    print(f"Gate 3 (regime preferido, >=3/6 em 2025-H1 chop): {g3_passes_in_chop_h1}/6 -> {'PASS' if g3_ok else 'FAIL'}")
    print(f"Gate 4 (assimetria diagnostica): bol={bol_passes}/9, rsi={rsi_passes}/9, delta={asymmetry}")

    overall = "PASS" if (g1_ok and g2_ok) else "FAIL"
    print(f"\nSERIE CE VERDICT (Gate1 + Gate2 coerencia): {overall}")
    if g1_ok and g2_ok:
        print("  => Short side tem edge material. Proxima ADR: serie composicional (short + filtro).")
    elif not g1_ok and g2_ok:
        print("  => H2 de ADR-0049 reforcada: regime domina. Proxima ADR: vol-adjusted sizing ou ensemble regime-gated.")
    elif g1_ok and not g2_ok:
        print("  => Incoerencia: passa gate principal mas falsifica Gate 2. Investigar rotulos de regime.")
    else:
        print("  => Short side falha e Gate 2 tambem falha. Duplo alerta: possivel bug ou marcacao errada.")

    out_p = Path("exports/diag/ce_series_summary.json")
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps({
        "gate_adr": "0052",
        "g1_passes_of_18": g1_passes,
        "g2_passes_in_bull_h2": g2_passes_in_bull_h2,
        "g3_passes_in_chop_h1": g3_passes_in_chop_h1,
        "bol_passes_of_9": bol_passes,
        "rsi_passes_of_9": rsi_passes,
        "asymmetry_abs": asymmetry,
        "gate1": "PASS" if g1_ok else "FAIL",
        "gate2": "PASS" if g2_ok else "FAIL",
        "gate3": "PASS" if g3_ok else "FAIL",
        "overall": overall,
        "pilots": pilots_out,
    }, indent=2, default=float))
    print(f"-> saved {out_p}")
