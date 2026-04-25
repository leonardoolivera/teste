"""Sumariza o progresso do dispatcher auto-paralelo (`run_roadmap_auto.py`).

Lê `exports/diag/roadmap_auto_progress.json` e produz:
- Counts globais (ok/fail, gates passed)
- Breakdown por engine: total / passed / pass_rate
- Breakdown por (engine, asset, window): pass count
- Lista os top 20 probes por sharpe (entre os ok com trades >= 30)
- Lista probes com gate sh+alfa (alfa = pnl_pct - bh_pct/leverage)

Saída: `exports/diag/roadmap_auto_phase1_summary.json` + tabela stdout.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "exports" / "diag" / "roadmap_auto_progress.json"
OUT = ROOT / "exports" / "diag" / "roadmap_auto_phase1_summary.json"

# B&H aproximado por (asset, window) — mesmo do summarize_roadmap_ma01.py
BH_APPROX = {
    ("BTC", "2024-H2"): 70.0, ("BTC", "2025-H1"): -8.0, ("BTC", "2025-H2"): 12.0,
    ("ETH", "2024-H2"): 0.0,  ("ETH", "2025-H1"): -47.0, ("ETH", "2025-H2"): 70.0,
    ("SOL", "2024-H2"): 46.0, ("SOL", "2025-H1"): -40.0, ("SOL", "2025-H2"): 35.0,
    ("DOT", "2025-H1"): -35.0, ("DOT", "2025-H2"): 20.0,
    ("LINK", "2025-H1"): -30.0, ("LINK", "2025-H2"): 25.0,
    ("AVAX", "2025-H1"): -45.0, ("AVAX", "2025-H2"): 15.0,
}
LEVERAGE = 2.0
SH_GATE = 1.5
TR_GATE = 30


def main() -> None:
    prog = json.loads(PROGRESS.read_text())
    rows = list(prog.values())
    n_total = len(rows)
    n_ok = sum(1 for r in rows if r["ok"])
    n_fail = n_total - n_ok

    by_engine_total = defaultdict(int)
    by_engine_pass_sh = defaultdict(int)
    by_engine_pass_alfa = defaultdict(int)
    by_combo = defaultdict(list)
    enriched = []

    for r in rows:
        eng = r["engine"]
        by_engine_total[eng] += 1
        m = r.get("metrics") or {}
        sh = m.get("sharpe")
        tr = m.get("trades")
        pnl = m.get("pnl_pct")
        bh = BH_APPROX.get((r["asset"], r["window"]))
        alfa = (pnl - (bh / LEVERAGE)) if (pnl is not None and bh is not None) else None
        gate_sh = bool(sh is not None and tr is not None and sh >= SH_GATE and tr >= TR_GATE)
        gate_alfa = bool(alfa is not None and alfa > 0)
        if gate_sh: by_engine_pass_sh[eng] += 1
        if gate_alfa: by_engine_pass_alfa[eng] += 1
        by_combo[(eng, r["asset"], r["window"])].append({
            "id": r["id"], "params": r["params"], "sharpe": sh, "trades": tr,
            "pnl_pct": pnl, "alfa": alfa, "gate_sh": gate_sh, "gate_alfa": gate_alfa,
        })
        enriched.append({**r, "alfa": alfa, "gate_sh": gate_sh, "gate_alfa": gate_alfa, "bh_pct": bh})

    print(f"\n{'='*70}\nRoadmap Auto Phase 1 — Summary\n{'='*70}")
    print(f"Total: {n_total} | ok: {n_ok} | fail: {n_fail}")
    print(f"\n{'Engine':<22} {'N':>5} {'gate_sh':>8} {'gate_alfa':>10} {'sh%':>6} {'alfa%':>7}")
    for eng in sorted(by_engine_total):
        n = by_engine_total[eng]
        ps = by_engine_pass_sh[eng]
        pa = by_engine_pass_alfa[eng]
        rs = ps / n * 100 if n else 0
        ra = pa / n * 100 if n else 0
        print(f"{eng:<22} {n:>5} {ps:>8} {pa:>10} {rs:>5.0f}% {ra:>6.0f}%")

    # Top 20 by sharpe (gates passed)
    pass_rows = [r for r in enriched if r.get("gate_sh") and r.get("gate_alfa")]
    pass_rows.sort(key=lambda r: -((r.get("metrics") or {}).get("sharpe") or 0))
    print(f"\nTop probes (gate_sh AND gate_alfa, n={len(pass_rows)}):")
    print(f"{'#':>3} {'engine':<18} {'asset':<5} {'window':<8} {'params':<35} {'sh':>6} {'pnl%':>7} {'alfa':>7} {'tr':>5}")
    for i, r in enumerate(pass_rows[:30], 1):
        m = r.get("metrics") or {}
        print(f"{i:>3} {r['engine']:<18} {r['asset']:<5} {r['window']:<8} "
              f"{r['params'][:35]:<35} {m.get('sharpe', 0):>6.2f} "
              f"{m.get('pnl_pct', 0):>7.1f} {(r.get('alfa') or 0):>7.1f} "
              f"{m.get('trades', 0):>5}")

    summary = {
        "n_total": n_total, "n_ok": n_ok, "n_fail": n_fail,
        "engines": {
            eng: {
                "n": by_engine_total[eng],
                "pass_sh": by_engine_pass_sh[eng],
                "pass_alfa": by_engine_pass_alfa[eng],
            } for eng in by_engine_total
        },
        "passed_probes": pass_rows,
    }
    OUT.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
