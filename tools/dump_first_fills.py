import json, sys
from pathlib import Path

BASE = Path(r"c:\Users\leo-a\OneDrive\Área de Trabalho\Testador de Estrategias\teste\results\validation")

PILOTS = [
    ("ETH 2024-H1", "bollinger-30-15-eth-1h-2024h1-regime-bw-250"),
    ("SOL 2024-H2", "bollinger-30-15-sol-1h-2024h2-regime-bw-250"),
]

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

for label, pilot in PILOTS:
    d = BASE / pilot
    cs = load(d / "cost_stress.json")["payload"]
    run = load(d / "run.json")
    wf = load(d / "walk_forward.json")["payload"]

    # dataset id from run.json
    dataset_id = run.get("dataset_id") or run.get("payload", {}).get("dataset_id", "?")

    fills = cs["baseline"]["result"]["fills"]
    # entries = side long (opening)
    entries = [f for f in fills if f.get("side") == "long"]

    print(f"\n=== {label} — {pilot} ===")
    print(f"dataset_id (run.json): {dataset_id}")
    print(f"total fills (cost_stress baseline): {len(fills)} | entries (long): {len(entries)} | exits (flat): {len(fills)-len(entries)}")
    print(f"\nPrimeiros 10 entry fills:")
    print(f"{'#':>3} {'signal_timestamp':25} {'fill_timestamp':25} {'price':>12} {'size':>14}")
    for i, f in enumerate(entries[:10], 1):
        print(f"{i:>3} {f.get('signal_timestamp',''):25} {f.get('timestamp',''):25} {f.get('price',0):>12.4f} {f.get('size',0):>14.8f}")

    # also from walk_forward fold 0
    if isinstance(wf, list) and wf:
        f0 = wf[0]
        f0_fills = f0.get("result", {}).get("fills", [])
        f0_entries = [f for f in f0_fills if f.get("side") == "long"]
        f0_ds = f0.get("result", {}).get("dataset_id", "?")
        tw = f0.get("train_window")
        te = f0.get("test_window")
        print(f"\n  [walk_forward fold 0] dataset_id={f0_ds}")
        print(f"  train={tw} test={te}")
        print(f"  fold 0 entries: {len(f0_entries)} (primeiros 5)")
        for i, f in enumerate(f0_entries[:5], 1):
            print(f"    {i} {f.get('signal_timestamp',''):25} {f.get('timestamp',''):25} {f.get('price',0):>12.4f}")
