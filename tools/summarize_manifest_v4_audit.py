"""Summarize manifest v4 audit — aplica Gates A/B/C de ADR-0067."""
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


APPROVED = [
    ("CH.4", "btc", "20250105_20250704"),
    ("CH.6", "sol", "20250105_20250704"),
    ("CH.7", "btc", "20250705_20251231"),
    ("CH.9", "sol", "20250705_20251231"),
]

EXCLUDED_EDGE = [
    ("CH.1", "btc", "20240705_20241231"),
    ("CH.5", "eth", "20250105_20250704"),
]


def load_run(rid: str) -> dict | None:
    base = Path("results/validation") / rid
    wf_p = base / "walk_forward.json"
    mc_p = base / "monte_carlo.json"
    cs_p = base / "cost_stress.json"
    if not (wf_p.exists() and mc_p.exists() and cs_p.exists()):
        return None
    return metrics(wf_p, mc_p, cs_p)


if __name__ == "__main__":
    print("\n=== Manifest v4 audit — Gates A/B/C (ADR-0067) ===\n")

    # Audit A
    print("--- Audit A: lucky-MC (4 combos x 3 seeds) ---")
    audit_a_results = []
    a_pass = 0
    a_total = 0
    for tag, asset, suffix in APPROVED:
        row = {"tag": tag, "asset": asset, "period": suffix, "seeds": {}}
        for seed, rid in [
            (42, f"ch-rsi-14-30-70-{asset}-{suffix}-width30-300-short"),
            (1337, f"audit-v4-a-{asset}-{suffix}-seed1337"),
            (2024, f"audit-v4-a-{asset}-{suffix}-seed2024"),
        ]:
            m = load_run(rid)
            if m is None:
                row["seeds"][str(seed)] = {"status": "MISSING"}
                a_total += 1
                continue
            ok, fail = gate_manifest(m)
            row["seeds"][str(seed)] = {"metrics": m, "pass": ok, "fail": fail}
            a_total += 1
            if ok:
                a_pass += 1
            mark = "PASS" if ok else "FAIL(" + ",".join(fail) + ")"
            print(f"  {tag} seed={seed}: trd={m['trades']} Sh={m['sharpe']:.2f} MDD={m['mdd_pct']:.2f}% MCp5={m['mc_p5']:.0f} cost_r={m['cost_r']:.4f} -> {mark}")
        audit_a_results.append(row)
    a_fails = a_total - a_pass
    a_ok = a_fails <= 1
    print(f"\nGate A: {a_pass}/{a_total} (fails={a_fails}) {'PASS' if a_ok else 'FAIL'} (gate: fails<=1)")

    # Audit B
    print("\n--- Audit B: filtro load-bearing (4 combos sem filtro) ---")
    audit_b_results = []
    b_filter_load_bearing = 0
    for tag, asset, suffix in APPROVED:
        rid_with = f"ch-rsi-14-30-70-{asset}-{suffix}-width30-300-short"
        rid_without = f"audit-v4-b-{asset}-{suffix}-nofilter"
        m_with = load_run(rid_with)
        m_without = load_run(rid_without)
        if m_with is None or m_without is None:
            print(f"  {tag}: MISSING")
            audit_b_results.append({"tag": tag, "status": "MISSING"})
            continue
        ok_without, fail_without = gate_manifest(m_without)
        filter_load_bearing = not ok_without
        if filter_load_bearing:
            b_filter_load_bearing += 1
        d_sh = m_with["sharpe"] - m_without["sharpe"]
        d_cr = m_with["cost_r"] - m_without["cost_r"]
        d_mcp5 = m_with["mc_p5"] - m_without["mc_p5"]
        tag_lb = "LOAD_BEARING" if filter_load_bearing else "neutral"
        print(f"  {tag}: with_filter Sh={m_with['sharpe']:.2f} cost_r={m_with['cost_r']:.4f} MCp5={m_with['mc_p5']:.0f}  |  no_filter Sh={m_without['sharpe']:.2f} cost_r={m_without['cost_r']:.4f} MCp5={m_without['mc_p5']:.0f}  |  deltas Sh={d_sh:+.2f} cr={d_cr:+.4f} MCp5={d_mcp5:+.0f}  -> {tag_lb} (without: {'FAIL '+','.join(fail_without) if not ok_without else 'PASS'})")
        audit_b_results.append({"tag": tag, "with": m_with, "without": m_without, "filter_load_bearing": filter_load_bearing, "fail_without": fail_without})
    b_ok = b_filter_load_bearing >= 3
    print(f"\nGate B: {b_filter_load_bearing}/4 load-bearing {'PASS' if b_ok else 'FAIL'} (gate >=3/4)")

    # Audit C
    print("\n--- Audit C: exclusao confirmada (2 combos com seed 1337) ---")
    audit_c_results = []
    c_still_fail = 0
    for tag, asset, suffix in EXCLUDED_EDGE:
        rid = f"audit-v4-c-{asset}-{suffix}-seed1337"
        m = load_run(rid)
        if m is None:
            print(f"  {tag}: MISSING")
            audit_c_results.append({"tag": tag, "status": "MISSING"})
            continue
        ok, fail = gate_manifest(m)
        still_fail = not ok
        if still_fail:
            c_still_fail += 1
        mark = "PASS (!!) " if ok else "FAIL (" + ",".join(fail) + ")"
        print(f"  {tag} seed=1337: trd={m['trades']} Sh={m['sharpe']:.2f} MDD={m['mdd_pct']:.2f}% MCp5={m['mc_p5']:.0f} cost_r={m['cost_r']:.4f} -> {mark}")
        audit_c_results.append({"tag": tag, "metrics": m, "pass": ok, "fail": fail, "still_excluded": still_fail})
    c_ok = c_still_fail == len(EXCLUDED_EDGE)
    print(f"\nGate C: {c_still_fail}/{len(EXCLUDED_EDGE)} ainda FAIL com seed 1337 {'PASS' if c_ok else 'FAIL'}")

    overall = "PASS" if (a_ok and b_ok and c_ok) else "FAIL"
    print(f"\n{'=' * 50}\nMANIFEST V4 AUDIT: {overall}\n{'=' * 50}")
    if overall == "PASS":
        print("  => Marcar live_status=active, notificar BotBinance.")
    else:
        print("  => Reverter promocao: live_status=blocked.")
        if not a_ok:
            print(f"     Audit A falhou: {a_fails} FAILs (gate permite <=1)")
        if not b_ok:
            print(f"     Audit B falhou: filtro nao load-bearing em {4-b_filter_load_bearing}/4")
        if not c_ok:
            print(f"     Audit C falhou: exclusao virou PASS com seed alternativo")

    out_p = Path("exports/diag/manifest_v4_audit_summary.json")
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps({
        "audit_adr": "0067",
        "manifest": "rsi_short_width_20260419.json",
        "gate_a_pass": a_pass,
        "gate_a_total": a_total,
        "gate_a_fails": a_fails,
        "gate_a": "PASS" if a_ok else "FAIL",
        "gate_b_load_bearing": b_filter_load_bearing,
        "gate_b": "PASS" if b_ok else "FAIL",
        "gate_c_still_fail": c_still_fail,
        "gate_c": "PASS" if c_ok else "FAIL",
        "overall": overall,
        "audit_a": audit_a_results,
        "audit_b": audit_b_results,
        "audit_c": audit_c_results,
    }, indent=2, default=float))
    print(f"\n-> saved {out_p}")
