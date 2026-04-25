"""Driver: roda engines aprovados em crypto sobre PAXGUSDT 1h, 5 janelas.

Replica parâmetros canônicos das aprovações (RSI 14/30/70, BB 20/2.0),
cost model baseline igual ao das aprovações (fee 5bps + slip 2bps), e
coleta métricas agregadas dos folds OOS do walk-forward.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from alpha_forge.cli import main as cli_main

WINDOWS = [
    ("2023h2", "paxgusdt_1h_20230705_20231231_binance_spot"),
    ("2024h1", "paxgusdt_1h_20240105_20240704_binance_spot"),
    ("2024h2", "paxgusdt_1h_20240705_20241231_binance_spot"),
    ("2025h1", "paxgusdt_1h_20250105_20250704_binance_spot"),
    ("2025h2", "paxgusdt_1h_20250705_20251231_binance_spot"),
]

# (label, strategy_name, extra_args)
STRATEGIES = [
    ("rsi_long_pure", "rsi",
     ["--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70",
      "--long-only"]),
    ("rsi_short_pure", "rsi",
     ["--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70",
      "--no-long-only"]),
    ("bb_long_mr", "bollinger",
     ["--bollinger-window", "20", "--bollinger-num-std", "2.0",
      "--long-only"]),
    ("bb_short_mr", "bollinger",
     ["--bollinger-window", "20", "--bollinger-num-std", "2.0",
      "--no-long-only"]),
]

RESULTS_DIR = Path("results/validation")


def run_one(run_id: str, dataset_id: str, strategy: str, extra: list[str]) -> int:
    argv = [
        "validate",
        "--run-id", run_id,
        "--dataset-id", dataset_id,
        "--strategy", strategy,
        "--capital", "10000",
        "--fracao", "0.2",
        "--alavancagem", "1.0",
        "--taker-fee-bps", "5",
        "--slippage-bps-per-notional", "2",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--stress", "fee+10:10:0",
        "--stress", "slip+10:0:10",
    ] + extra
    return cli_main_with_argv(argv)


def cli_main_with_argv(argv: list[str]) -> int:
    from alpha_forge.cli.app import run as cli_run
    return cli_run(argv)


def summarize(run_dir: Path) -> dict:
    wf = json.loads((run_dir / "walk_forward.json").read_text(encoding="utf-8"))
    folds = wf.get("folds", wf)
    if isinstance(folds, dict):
        folds = folds.get("folds", [])
    trades = []
    for f in folds:
        m = f.get("result", {}).get("metrics") or {}
        trades.append(m)
    total_trades = sum(m.get("trade_count", 0) for m in trades)
    total_pnl = sum(m.get("total_pnl", 0.0) for m in trades)
    hr = [m.get("hit_rate", 0.0) for m in trades if m.get("trade_count", 0) > 0]
    mc_path = run_dir / "monte_carlo.json"
    mc_median = None
    mc_p5 = None
    if mc_path.exists():
        mc = json.loads(mc_path.read_text(encoding="utf-8"))
        pcts = mc.get("final_equity_percentiles") or mc.get("percentiles") or {}
        mc_median = pcts.get("50") if isinstance(pcts, dict) else None
        mc_p5 = pcts.get("5") if isinstance(pcts, dict) else None
    cs_path = run_dir / "cost_stress.json"
    cs_min_ratio = None
    if cs_path.exists():
        cs = json.loads(cs_path.read_text(encoding="utf-8"))
        scenarios = cs.get("scenarios", [])
        ratios = [s.get("pnl_ratio_vs_baseline") for s in scenarios
                  if s.get("pnl_ratio_vs_baseline") is not None]
        if ratios:
            cs_min_ratio = min(ratios)
    return {
        "total_trades": total_trades,
        "total_pnl": round(total_pnl, 2),
        "avg_hit_rate": round(sum(hr) / len(hr), 3) if hr else None,
        "mc_median_final": mc_median,
        "mc_p5_final": mc_p5,
        "cost_stress_min_ratio": cs_min_ratio,
    }


def main() -> int:
    summary_rows: list[dict] = []
    for win_tag, dsid in WINDOWS:
        for strat_label, strat_name, extra in STRATEGIES:
            run_id = f"paxg_{strat_label}_{win_tag}"
            run_dir = RESULTS_DIR / run_id
            print(f"\n=== {run_id} ===")
            rc = run_one(run_id, dsid, strat_name, extra)
            if rc != 0:
                print(f"  FAIL rc={rc}")
                summary_rows.append({
                    "run_id": run_id, "window": win_tag, "strategy": strat_label,
                    "status": "FAIL", "rc": rc,
                })
                continue
            stats = summarize(run_dir)
            row = {
                "run_id": run_id, "window": win_tag, "strategy": strat_label,
                "status": "OK", **stats,
            }
            print(f"  OK  trades={stats['total_trades']}  pnl={stats['total_pnl']}  "
                  f"hr={stats['avg_hit_rate']}  mc_median={stats['mc_median_final']}  "
                  f"cs_min={stats['cost_stress_min_ratio']}")
            summary_rows.append(row)

    out = Path("results/paxg_sweep_summary.json")
    out.write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")
    print(f"\nSummary -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
