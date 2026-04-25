"""Audit cross-check: compara métricas do dispatcher auto-paralelo
(`exports/diag/roadmap_auto_progress.json`) contra os summaries existentes
dos batches manuais (MA01, MA02, ST01, BT01, AE01).

Para cada probe que existe em ambos (mapeando por engine+asset+window+params),
imprime sharpe e trades. Discrepância > 0.01 em sharpe ou ≠ em trades flag.

Saída: stdout + `exports/diag/roadmap_auto_audit.json`.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAG = ROOT / "exports" / "diag"
PROGRESS = DIAG / "roadmap_auto_progress.json"
OUT = DIAG / "roadmap_auto_audit.json"

BATCH_FILES = ["roadmap_ma01_summary.json", "roadmap_ma02_summary.json",
               "roadmap_st01_summary.json", "roadmap_bt01_summary.json",
               "roadmap_ae01_summary.json"]


def parse_batch_label(rid: str) -> dict:
    """t1ma-25-75-btc-2025h2-long-10m -> dict signature."""
    parts = rid.split("-")
    # heuristic
    eng_short = parts[0][2:]  # 'ma' / 'st' / 'bb' (after t1/t3)
    eng_map = {"ma": "ma_crossover", "st": "supertrend", "bb": "bollinger"}
    engine = eng_map.get(eng_short, eng_short)
    return {"engine": engine}


def main() -> None:
    progress = json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {}
    # Build lookup by (engine, asset, window, params_normalized)
    auto_by_sig = {}
    for r in progress.values():
        if not r.get("ok"): continue
        sig = (r["engine"], r["asset"], r["window"], r["params"])
        auto_by_sig[sig] = r

    matches = []
    diffs = []
    for fname in BATCH_FILES:
        path = DIAG / fname
        if not path.exists(): continue
        rows = json.loads(path.read_text())
        for row in rows:
            rid = row["rid"]
            label = row["label"]  # e.g. "ETH 2024-H2"
            asset, window = label.split()
            # parse engine + params from rid
            seg = parse_batch_label(rid)
            engine = seg["engine"]
            # Normalize params from row['params'] string
            p = str(row["params"]).strip()
            # Some summaries store params as "MA 25/75" — strip prefix words
            if " " in p:
                p = p.split(" ")[-1]
            # batch params formats: "10/30" or "10/2.5/bi" — translate
            params_norm = None
            if engine == "ma_crossover":
                short, long = p.split("/")
                params_norm = f"short={int(short)},long={int(long)}"
            elif engine == "supertrend":
                bits = p.split("/")
                if len(bits) >= 2:
                    params_norm = f"atr_period={int(bits[0])},atr_mult={float(bits[1])}"
            elif engine == "bollinger":
                bits = p.split("/")
                if len(bits) == 2:
                    params_norm = f"window={int(bits[0])},num_std={float(bits[1])}"
            if not params_norm:
                continue
            # window from batch (10m windows have "10m-" prefix removed for matching)
            sig = (engine, asset, window, params_norm)
            sig_alt = (engine, asset, f"10m-{window}", params_norm)
            auto = auto_by_sig.get(sig) or auto_by_sig.get(sig_alt)
            if not auto:
                continue
            am = auto.get("metrics") or {}
            sh_a = am.get("sharpe")
            sh_b = row.get("sharpe")
            tr_a = am.get("trades")
            tr_b = row.get("trades")
            ok = (sh_a is not None and sh_b is not None and abs(sh_a - sh_b) < 0.01
                  and tr_a == tr_b)
            entry = {
                "engine": engine, "asset": asset, "window": window, "params": p,
                "auto_sharpe": sh_a, "batch_sharpe": sh_b,
                "auto_trades": tr_a, "batch_trades": tr_b,
                "match": ok,
            }
            (matches if ok else diffs).append(entry)

    print(f"\n{'='*70}\nAuto vs batches audit — overlapping probes\n{'='*70}")
    print(f"Matches: {len(matches)}  |  Diffs: {len(diffs)}\n")
    if diffs:
        print(f"{'engine':<14} {'asset':<5} {'window':<10} {'params':<20} "
              f"{'auto_sh':>8} {'batch_sh':>9} {'auto_tr':>8} {'batch_tr':>9}")
        for d in diffs:
            print(f"{d['engine']:<14} {d['asset']:<5} {d['window']:<10} {d['params']:<20} "
                  f"{(d['auto_sharpe'] or 0):>8.4f} {(d['batch_sharpe'] or 0):>9.4f} "
                  f"{d['auto_trades'] or 0:>8} {d['batch_trades'] or 0:>9}")
    else:
        print("[OK] todos os overlap probes batem (delta sharpe < 0.01).")

    OUT.write_text(json.dumps({"matches": matches, "diffs": diffs}, indent=2, default=str))
    print(f"\n→ {OUT}")


if __name__ == "__main__":
    main()
