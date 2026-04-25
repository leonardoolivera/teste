"""Extrai metrics de runs BK/BN/BO rerun e avalia gates strict.

Gates (iguais BK/BN/BO originais):
    trades >= 30, Sharpe >= 1.0, MDD <= 20%, PnL > 0,
    cost_stress_ratio_min >= 0.95, MC p5 final_equity > 10000, MC MDD p95 <= 10%.
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
    pnl_pct = (full_eq[-1] / 10000 - 1) * 100
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
    mc_mdd_p95 = mc["max_drawdown_percentiles"]["95"] * 100  # frac -> pct
    cs_payload = json.loads(cs_p.read_text())["payload"]
    base_fe = cs_payload["baseline"]["result"]["final_equity"]
    stress_fes = [s["result"]["final_equity"] for s in cs_payload["scenarios"]]
    if base_fe <= 0:
        cost_r = 0.0
    else:
        cost_r = min((sfe / base_fe) for sfe in stress_fes) if stress_fes else 1.0
    return dict(trades=n_trades, sharpe=sharpe, mdd_pct=mdd, pnl_pct=pnl_pct,
                cost_r=cost_r, mc_p5=mc_p5, mc_mdd_p95=mc_mdd_p95)


def evaluate_gates(m: dict) -> tuple[bool, list[str]]:
    fail = []
    if m["trades"] < 30:
        fail.append("trades")
    if m["sharpe"] < 1.0:
        fail.append("Sharpe")
    if m["mdd_pct"] > 20:
        fail.append("MDD")
    if m["pnl_pct"] <= 0:
        fail.append("PnL")
    if m["cost_r"] < 0.95:
        fail.append("cost_r")
    if m["mc_p5"] <= 10000:
        fail.append("MCp5")
    if m["mc_mdd_p95"] > 10:
        fail.append("MCmddp95")
    return len(fail) == 0, fail


def process(name: str, runs: list[tuple[str, str, str, float | int]]) -> None:
    base = Path("results/validation")
    print(f"\n=== {name} rerun summary ===")
    print(f'{"Tag":5}{"Combo":15}{"pert":>8}{"trd":>5}{"Sh":>7}{"MDD%":>7}{"PnL%":>8}{"cost_r":>8}{"MCp5eq":>9}{"MCmddp95":>10}  verdict')
    print("-" * 110)
    results = []
    for tag, run_id, combo, pert in runs:
        out = base / run_id
        wf_p, mc_p, cs_p = out / "walk_forward.json", out / "monte_carlo.json", out / "cost_stress.json"
        if not (wf_p.exists() and mc_p.exists() and cs_p.exists()):
            print(f"{tag} MISSING")
            continue
        m = metrics(wf_p, mc_p, cs_p)
        passed, fail = evaluate_gates(m)
        verdict = "PASS" if passed else "FAIL(" + ",".join(fail) + ")"
        print(f'{tag:5}{combo:15}{str(pert):>8}{m["trades"]:>5}{m["sharpe"]:>7.2f}{m["mdd_pct"]:>7.2f}{m["pnl_pct"]:>+8.2f}{m["cost_r"]:>8.4f}{m["mc_p5"]:>9.0f}{m["mc_mdd_p95"]:>10.2f}  {verdict}')
        results.append(dict(tag=tag, combo=combo, perturbation=pert,
                            **{k: round(v, 4) if isinstance(v, float) else v for k, v in m.items()},
                            verdict="PASS" if passed else "FAIL", fail_reasons=fail))
    out_p = Path(f"exports/diag/{name.lower()}_rerun_summary.json")
    out_p.write_text(json.dumps(results, indent=2))
    print(f"-> saved {out_p}")


if __name__ == "__main__":
    BK = [
        ("BK.1", "bk-rerun-w30-ns1.25-bw250-eth-20240105_20240704", "ETH 2024-H1", 1.25),
        ("BK.2", "bk-rerun-w30-ns1.25-bw250-eth-20250105_20250704", "ETH 2025-H1", 1.25),
        ("BK.3", "bk-rerun-w30-ns1.25-bw250-btc-20240705_20241231", "BTC 2024-H2", 1.25),
        ("BK.4", "bk-rerun-w30-ns1.25-bw250-sol-20240705_20241231", "SOL 2024-H2", 1.25),
        ("BK.5", "bk-rerun-w30-ns1.75-bw250-eth-20240105_20240704", "ETH 2024-H1", 1.75),
        ("BK.6", "bk-rerun-w30-ns1.75-bw250-eth-20250105_20250704", "ETH 2025-H1", 1.75),
        ("BK.7", "bk-rerun-w30-ns1.75-bw250-btc-20240705_20241231", "BTC 2024-H2", 1.75),
        ("BK.8", "bk-rerun-w30-ns1.75-bw250-sol-20240705_20241231", "SOL 2024-H2", 1.75),
    ]
    BN = [
        ("BN.1", "bn-rerun-w25-ns150-bw250-eth-20240105_20240704", "ETH 2024-H1", 25),
        ("BN.2", "bn-rerun-w25-ns150-bw250-eth-20250105_20250704", "ETH 2025-H1", 25),
        ("BN.3", "bn-rerun-w25-ns150-bw250-btc-20240705_20241231", "BTC 2024-H2", 25),
        ("BN.4", "bn-rerun-w25-ns150-bw250-sol-20240705_20241231", "SOL 2024-H2", 25),
        ("BN.5", "bn-rerun-w35-ns150-bw250-eth-20240105_20240704", "ETH 2024-H1", 35),
        ("BN.6", "bn-rerun-w35-ns150-bw250-eth-20250105_20250704", "ETH 2025-H1", 35),
        ("BN.7", "bn-rerun-w35-ns150-bw250-btc-20240705_20241231", "BTC 2024-H2", 35),
        ("BN.8", "bn-rerun-w35-ns150-bw250-sol-20240705_20241231", "SOL 2024-H2", 35),
    ]
    BO = [
        ("BO.1", "bo-rerun-w30-ns150-bw200-eth-20240105_20240704", "ETH 2024-H1", 200),
        ("BO.2", "bo-rerun-w30-ns150-bw200-eth-20250105_20250704", "ETH 2025-H1", 200),
        ("BO.3", "bo-rerun-w30-ns150-bw200-btc-20240705_20241231", "BTC 2024-H2", 200),
        ("BO.4", "bo-rerun-w30-ns150-bw200-sol-20240705_20241231", "SOL 2024-H2", 200),
        ("BO.5", "bo-rerun-w30-ns150-bw300-eth-20240105_20240704", "ETH 2024-H1", 300),
        ("BO.6", "bo-rerun-w30-ns150-bw300-eth-20250105_20250704", "ETH 2025-H1", 300),
        ("BO.7", "bo-rerun-w30-ns150-bw300-btc-20240705_20241231", "BTC 2024-H2", 300),
        ("BO.8", "bo-rerun-w30-ns150-bw300-sol-20240705_20241231", "SOL 2024-H2", 300),
    ]
    process("BK", BK)
    process("BN", BN)
    process("BO", BO)
