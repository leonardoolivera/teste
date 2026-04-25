"""V2 RB018 — Execution invariant audit (RAIO Nível 1 Scout).

Audita os 658 r1k-* runs do V1 contra os 4 invariantes ADR-0030:
1. Entry fill: market @ open[t+1] após ENTER signal at t (signal_timestamp + 1 bar = timestamp).
2. Exit fill: market @ open[t+1] após EXIT signal at t (idem).
3. Sizing: literal `notional_per_trade_quote_ccy` (10000 * fracao=0.1 * alavancagem=2.0 = 2000.0 default).
4. Stop loss: disabled (nenhum exit pode ter side='stop' ou similar).

Saída: stdout + `exports/diag/v2_rb018_audit.json`.

Conformidade RAIO:
- Pre-reg: ADR-0213 §"Top 4 V2"
- Nível 1 Scout
- Decision após: EXPAND/CUT/QUARANTINE per RAIO §12
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validation"
OUT = ROOT / "exports" / "diag" / "v2_rb018_audit.json"

# Default per BASE_ARGS em run_roadmap_auto.py: capital=10000, fracao=0.1, alavancagem=2.0
EXPECTED_NOTIONAL = 10000.0 * 0.1 * 2.0  # 2000.0
NOTIONAL_TOL = 5.0  # tolerar pequena diferença por arredondamento de size

# Bar duration per dataset suffix (segundos)
def bar_seconds(dataset_id: str) -> int | None:
    if "_10m_" in dataset_id: return 600
    if "_1h_" in dataset_id: return 3600
    if "_4h_" in dataset_id: return 14400
    if "_15m_" in dataset_id: return 900
    return None


def audit_run(run_dir: Path) -> dict:
    rid = run_dir.name
    wf_path = run_dir / "walk_forward.json"
    if not wf_path.exists():
        return {"rid": rid, "ok": False, "error": "missing walk_forward.json"}

    wf = json.loads(wf_path.read_text())
    folds = wf.get("payload", [])
    violations = defaultdict(int)
    n_fills = 0
    sample_violations: list[dict] = []
    notional_outliers: list[float] = []

    for f in folds:
        result = f.get("result", {})
        ds_id = result.get("dataset_id", "")
        bar_s = bar_seconds(ds_id)
        if bar_s is None:
            violations["unknown_bar_duration"] += 1
            continue
        fills = result.get("fills", []) or []
        for i, fill in enumerate(fills):
            n_fills += 1
            sig_ts = fill.get("signal_timestamp")
            ts = fill.get("timestamp")
            side = fill.get("side")
            notional = fill.get("notional")

            # Invariant 1+2: timestamp = signal_timestamp + bar_seconds
            if sig_ts and ts:
                from datetime import datetime
                try:
                    s = datetime.fromisoformat(sig_ts.replace("Z", "+00:00"))
                    t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    delta = (t - s).total_seconds()
                    if abs(delta - bar_s) > 1:  # 1s tolerance
                        violations["bar_offset_mismatch"] += 1
                        if len(sample_violations) < 5:
                            sample_violations.append({
                                "rid": rid, "fold": f.get("fold_index"),
                                "kind": "bar_offset", "expected_s": bar_s,
                                "actual_s": delta, "signal_ts": sig_ts, "fill_ts": ts,
                            })
                except Exception:
                    violations["timestamp_parse_error"] += 1
            else:
                violations["missing_timestamp"] += 1

            # Invariant 3: sizing — notional ≈ EXPECTED_NOTIONAL para fills de abertura (side != flat)
            if side and side not in ("flat",) and notional is not None:
                # entry fills: notional should be exactly expected
                if abs(notional - EXPECTED_NOTIONAL) > NOTIONAL_TOL:
                    violations["notional_drift"] += 1
                    if len(notional_outliers) < 10:
                        notional_outliers.append(notional)

            # Invariant 4: stop loss disabled — side never 'stop'/'sl'
            if side in ("stop", "sl", "stop_loss"):
                violations["stop_loss_present"] += 1
                if len(sample_violations) < 5:
                    sample_violations.append({
                        "rid": rid, "fold": f.get("fold_index"),
                        "kind": "stop_loss_side", "side": side,
                    })

    ok = (violations.get("bar_offset_mismatch", 0) == 0
          and violations.get("stop_loss_present", 0) == 0
          and violations.get("missing_timestamp", 0) == 0)
    return {
        "rid": rid, "ok": ok, "n_fills": n_fills,
        "violations": dict(violations),
        "sample_violations": sample_violations,
        "notional_outliers_sample": notional_outliers[:5],
    }


def main() -> int:
    run_dirs = sorted(d for d in RESULTS.glob("r1k-*") if d.is_dir())
    print(f"[RB018] auditing {len(run_dirs)} r1k-* runs")
    results = []
    n_clean = 0
    n_dirty = 0
    agg_violations: dict[str, int] = defaultdict(int)
    dirty_runs: list[str] = []

    for d in run_dirs:
        r = audit_run(d)
        results.append(r)
        if r["ok"]:
            n_clean += 1
        else:
            n_dirty += 1
            dirty_runs.append(r["rid"])
        for k, v in r.get("violations", {}).items():
            agg_violations[k] += v

    summary = {
        "n_runs_audited": len(run_dirs),
        "n_clean": n_clean,
        "n_dirty": n_dirty,
        "aggregate_violations": dict(agg_violations),
        "dirty_runs_sample": dirty_runs[:20],
        "expected_notional": EXPECTED_NOTIONAL,
    }
    sample_violations_all = []
    for r in results:
        sample_violations_all.extend(r.get("sample_violations", []))
        if len(sample_violations_all) >= 30:
            break

    out_payload = {
        "summary": summary,
        "sample_violations": sample_violations_all[:30],
        "per_run": [r for r in results if not r["ok"]][:50],  # only dirty for compactness
    }
    OUT.write_text(json.dumps(out_payload, indent=2, default=str))

    print(f"\n{'='*70}\nRB018 Execution Invariant Audit\n{'='*70}")
    print(f"Runs audited: {len(run_dirs)}")
    print(f"Clean: {n_clean}  ({n_clean/len(run_dirs)*100:.1f}%)")
    print(f"Dirty: {n_dirty}  ({n_dirty/len(run_dirs)*100:.1f}%)")
    print(f"\nAggregate violations across all runs:")
    for k, v in sorted(agg_violations.items(), key=lambda kv: -kv[1]):
        print(f"  {v:>8}  {k}")
    if sample_violations_all:
        print(f"\nSample violations (first 5):")
        for sv in sample_violations_all[:5]:
            print(f"  {sv}")
    print(f"\n-> {OUT}")
    return 0 if n_dirty == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
