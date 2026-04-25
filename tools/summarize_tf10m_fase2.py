"""Resumir Série TF10m Fase 2 — 30 probes, 4 engines paralelas (ADR-0197).

Blocos:
  B (RSI+width short, 9)
  C (BB+width long, 9)
  D (RSI+width long, 9)
  E (RSI+trend_htf short SOL, 3)

Annualização: sqrt(144 × 365) ≈ 229.25.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "series_tf10m_fase2_summary.json"


def _probes_bcd(prefix: str, short_long: str) -> list[tuple[str, str, str]]:
    order_w = ["2024h2", "2025h1", "2025h2"]
    order_a = ["btc", "eth", "sol"]
    labels_w = {"2024h2": "2024-H2", "2025h1": "2025-H1", "2025h2": "2025-H2"}
    labels_a = {"btc": "BTC", "eth": "ETH", "sol": "SOL"}
    strat = "rsi" if prefix.startswith("tf10b") or prefix.startswith("tf10d") else "bol"
    rsi_range = "30-70"
    bb_range = "30-15"
    out: list[tuple[str, str, str]] = []
    i = 1
    for w in order_w:
        for a in order_a:
            if strat == "rsi":
                rid = f"{prefix}-rsi-{rsi_range}-width-{a}-{w}-{short_long}-10m"
            else:
                rid = f"{prefix}-bol-{bb_range}-width-{a}-{w}-{short_long}-10m"
            tag = f"{prefix.upper().replace('TF10', 'TF10')}.{i}"
            out.append((tag, rid, f"{labels_a[a]} {labels_w[w]}"))
            i += 1
    return out


BLOCO_B = [(f"TF10B.{i+1}", rid, lbl) for i, (_, rid, lbl) in enumerate(_probes_bcd("tf10b", "short"))]
BLOCO_C = [(f"TF10C.{i+1}", rid, lbl) for i, (_, rid, lbl) in enumerate(_probes_bcd("tf10c", "long"))]
BLOCO_D = [(f"TF10D.{i+1}", rid, lbl) for i, (_, rid, lbl) in enumerate(_probes_bcd("tf10d", "long"))]

BLOCO_E = [
    ("TF10E.1", "tf10e-rsi-25-75-trendhtf-sol-2024h2-short-10m", "SOL 2024-H2"),
    ("TF10E.2", "tf10e-rsi-25-75-trendhtf-sol-2025h1-short-10m", "SOL 2025-H1"),
    ("TF10E.3", "tf10e-rsi-25-75-trendhtf-sol-2025h2-short-10m", "SOL 2025-H2"),
]

BLOCKS: dict[str, list[tuple[str, str, str]]] = {
    "B (RSI+width short)": BLOCO_B,
    "C (BB+width long)": BLOCO_C,
    "D (RSI+width long)": BLOCO_D,
    "E (RSI+trendhtf short SOL)": BLOCO_E,
}


def annual_sharpe_10m(rets: list[float]) -> float:
    n = len(rets)
    if n < 2:
        return 0.0
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / n
    sd = math.sqrt(var)
    if sd == 0:
        return 0.0
    return (mean / sd) * math.sqrt(144 * 365)


def metrics(rid: str) -> dict:
    p = RESULTS / rid
    wf = json.loads((p / "walk_forward.json").read_text())
    folds = wf["payload"]
    all_trades: list[dict] = []
    full_eq = [10000.0]
    for f in folds:
        all_trades.extend(f["result"].get("trades", []))
        ec_pairs = f["result"].get("equity_curve", [])
        ec_vals = [pair[1] for pair in ec_pairs]
        if ec_vals:
            base_eq = full_eq[-1]
            first = ec_vals[0] if ec_vals[0] != 0 else 10000.0
            for v in ec_vals:
                full_eq.append(base_eq * v / first)
    n_trades = len(all_trades)
    final_eq = full_eq[-1]
    pnl_pct = (final_eq / 10000.0 - 1) * 100
    rets = [
        (full_eq[i] / full_eq[i - 1] - 1)
        for i in range(1, len(full_eq))
        if full_eq[i - 1] > 0
    ]
    sh = annual_sharpe_10m(rets)
    return dict(trades=n_trades, pnl_pct=pnl_pct, sharpe=sh, final_eq=final_eq)


def main() -> None:
    out_all: list[dict] = []
    block_pass: dict[str, list[str]] = {}
    for block_name, probes in BLOCKS.items():
        print(f"\n{'=' * 70}\nBloco {block_name}\n{'=' * 70}")
        print(f"{'Tag':<9} {'Label':<14} {'Tr':>5} {'Sh':>7} {'PnL%':>8}  {'FE':>8}")
        rows: list[dict] = []
        for tag, rid, label in probes:
            try:
                m = metrics(rid)
            except FileNotFoundError:
                print(f"{tag:<9} {label:<14}  MISSING ({rid})")
                continue
            rows.append({"block": block_name, "tag": tag, "label": label, "run_id": rid, **m})
            print(
                f"{tag:<9} {label:<14} {m['trades']:>5} "
                f"{m['sharpe']:>7.3f} {m['pnl_pct']:>8.2f}  {m['final_eq']:>8.0f}"
            )
        passing = [r for r in rows if r["sharpe"] >= 1.5 and r["trades"] >= 30]
        block_pass[block_name] = [f"{r['tag']} {r['label']} Sh={r['sharpe']:.2f}" for r in passing]
        print(f"Gate bloco (Sh>=1.5 AND trades>=30): {len(passing)}/{len(rows)}")
        out_all.extend(rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_all, indent=2))

    total_pass = [r for r in out_all if r["sharpe"] >= 1.5 and r["trades"] >= 30]
    print(f"\n{'=' * 70}\nAGREGADO FASE 2\n{'=' * 70}")
    print(f"Total probes completos: {len(out_all)}/30")
    print(f"Gate agregado (Sh>=1.5 AND trades>=30): {len(total_pass)}/30")
    for block_name, passes in block_pass.items():
        print(f"\n  Bloco {block_name}: {len(passes)} pass")
        for p in passes:
            print(f"    {p}")


if __name__ == "__main__":
    main()
