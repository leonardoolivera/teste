"""Summary do audit do manifest bollinger_width_regime_20260418_v2."""
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


def metrics(rid: str) -> dict:
    base = Path("results/validation") / rid
    wf = json.loads((base / "walk_forward.json").read_text())["payload"]
    mc = json.loads((base / "monte_carlo.json").read_text())["payload"]
    cs = json.loads((base / "cost_stress.json").read_text())["payload"]
    all_trades = []
    full_eq = [10000.0]
    for f in wf:
        all_trades.extend(f["result"].get("trades", []))
        ec_vals = [p[1] for p in f["result"].get("equity_curve", [])]
        if ec_vals:
            be = full_eq[-1]
            fv = ec_vals[0] if ec_vals[0] != 0 else 10000.0
            for v in ec_vals:
                full_eq.append(be * v / fv)
    rets = [(full_eq[i] / full_eq[i - 1] - 1) for i in range(1, len(full_eq)) if full_eq[i - 1] > 0]
    sharpe = annual_sharpe(rets)
    peak = full_eq[0]
    mdd = 0.0
    for v in full_eq:
        peak = max(peak, v)
        mdd = max(mdd, (peak - v) / peak * 100)
    base_fe = cs["baseline"]["result"]["final_equity"]
    cost_r = min(s["result"]["final_equity"] / base_fe for s in cs["scenarios"])
    return dict(
        trades=len(all_trades),
        sharpe=sharpe,
        final_eq=full_eq[-1],
        mdd_pct=mdd,
        cost_r=cost_r,
        mc_p5=mc["final_equity_percentiles"]["5"],
        mc_p50=mc["final_equity_percentiles"]["50"],
        mc_p95=mc["final_equity_percentiles"]["95"],
    )


if __name__ == "__main__":
    print("\n=== Audit A — SOL 2024-H2 sob 3 seeds (manifest completo) ===")
    print(f'{"seed":>6}{"trd":>5}{"Sh":>7}{"fe":>9}{"MDD%":>7}{"MCp5":>8}{"MCp50":>9}{"MCp95":>9}')
    results_a = {}
    for seed in (42, 1337, 2024):
        m = metrics(f"audit-a-sol-2024h2-seed{seed}")
        results_a[seed] = m
        print(f'{seed:>6}{m["trades"]:>5}{m["sharpe"]:>7.2f}{m["final_eq"]:>9.0f}{m["mdd_pct"]:>7.2f}{m["mc_p5"]:>8.0f}{m["mc_p50"]:>9.0f}{m["mc_p95"]:>9.0f}')

    sharpes_a = [r["sharpe"] for r in results_a.values()]
    mc_p5s = [r["mc_p5"] for r in results_a.values()]
    print(f"\n  Sharpe range: [{min(sharpes_a):.2f}, {max(sharpes_a):.2f}], delta={max(sharpes_a)-min(sharpes_a):.2f}")
    print(f"  MC p5 range:  [{min(mc_p5s):.0f}, {max(mc_p5s):.0f}], delta={max(mc_p5s)-min(mc_p5s):.0f}")
    # Note: trades/sharpe/fe sao deterministicos do WF (nao dependem de seed MC).
    # Seeds trocam apenas percentis do MC.

    print("\n=== Audit B — SOL 2024-H2 com vs sem filtro ===")
    m_with = results_a[42]
    m_no = metrics("audit-b-sol-2024h2-nofilter")
    print(f'{"variant":>10}{"trd":>5}{"Sh":>7}{"fe":>9}{"MDD%":>7}{"MCp5":>8}')
    print(f'{"with_flt":>10}{m_with["trades"]:>5}{m_with["sharpe"]:>7.2f}{m_with["final_eq"]:>9.0f}{m_with["mdd_pct"]:>7.2f}{m_with["mc_p5"]:>8.0f}')
    print(f'{"no_filter":>10}{m_no["trades"]:>5}{m_no["sharpe"]:>7.2f}{m_no["final_eq"]:>9.0f}{m_no["mdd_pct"]:>7.2f}{m_no["mc_p5"]:>8.0f}')
    delta_sh = m_with["sharpe"] - m_no["sharpe"]
    delta_fe = m_with["final_eq"] - m_no["final_eq"]
    print(f"\n  Delta Sharpe (with - no): {delta_sh:+.2f}")
    print(f"  Delta fe (with - no):     {delta_fe:+.0f}")

    print("\n=== Audit C — SOL 2025-H1 com engine exata do manifest ===")
    gate_sharpe, gate_mdd, gate_fe, gate_cost_r, gate_mcp5 = 1.0, 20, 10000, 0.95, 9500
    m_c = metrics("audit-c-sol-2025h1-manifest")
    print(f'  trades={m_c["trades"]} Sharpe={m_c["sharpe"]:.2f} fe={m_c["final_eq"]:.0f} '
          f'MDD%={m_c["mdd_pct"]:.2f} cost_r={m_c["cost_r"]:.4f} MCp5={m_c["mc_p5"]:.0f}')
    fails = []
    if m_c["trades"] < 30: fails.append("trades<30")
    if m_c["sharpe"] < gate_sharpe: fails.append(f"Sharpe<{gate_sharpe}")
    if m_c["mdd_pct"] > gate_mdd: fails.append(f"MDD>{gate_mdd}")
    if m_c["final_eq"] <= gate_fe: fails.append(f"fe<={gate_fe}")
    if m_c["cost_r"] < gate_cost_r: fails.append(f"cost_r<{gate_cost_r}")
    if m_c["mc_p5"] <= gate_mcp5: fails.append(f"MCp5<={gate_mcp5}")
    verdict = "PASS gates manifest" if not fails else f"FAIL({','.join(fails)})"
    print(f"  Verdict vs gate manifest (adaptado): {verdict}")

    print("\n--- Comparativo com manifest oficial (expansion_policy excluiu com Sharpe 0.62) ---")

    out = Path("exports/diag/manifest_audit_summary.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "audit_a_seeds": {str(k): v for k, v in results_a.items()},
        "audit_a_sharpe_stability": {"min": min(sharpes_a), "max": max(sharpes_a), "delta": max(sharpes_a)-min(sharpes_a)},
        "audit_b_with_filter": m_with,
        "audit_b_no_filter": m_no,
        "audit_b_filter_contribution": {"delta_sharpe": delta_sh, "delta_fe": delta_fe},
        "audit_c_sol_2025h1": m_c,
        "audit_c_verdict": verdict,
    }, indent=2, default=float))
    print(f"-> saved {out}")
