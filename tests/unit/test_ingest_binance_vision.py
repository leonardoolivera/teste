"""Testes sem rede de `scripts/ingest_binance_vision.py` (ADR-0009).

Stubs substituem `download_if_missing` e `read_zip_as_frame` por frames
sintéticos no formato cru de Binance Vision. Valida:
  - símbolo normalizado em forma canônica única (BTC/USDT → BTCUSDT);
  - dois símbolos distintos coexistem sem colisão (nenhum BTC privilegiado);
  - gap não declarado bloqueia ingestão; Parquet não fica órfão;
  - gap declarado passa e entra no manifesto.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pandas as pd
import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "ingest_binance_vision.py"


def _load_script_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "ingest_binance_vision", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def script() -> Any:
    return _load_script_module()


def _fake_kline_frame(
    start: datetime, periods: int, base_price: float, step_hours: int = 1
) -> pd.DataFrame:
    """Produz frame no layout cru de Binance Vision kline (12 colunas, open_time_ms)."""
    rows = []
    step = timedelta(hours=step_hours)
    for i in range(periods):
        ts = start + i * step
        ot_ms = int(ts.timestamp() * 1000)
        price = base_price + i
        rows.append(
            {
                "open_time_ms": ot_ms,
                "open": price,
                "high": price * 1.001,
                "low": price * 0.999,
                "close": price,
                "volume": 1.0,
                "close_time_ms": ot_ms + int(step.total_seconds() * 1000) - 1,
                "quote_volume": 1.0,
                "trades": 1,
                "taker_buy_base": 0.5,
                "taker_buy_quote": 0.5,
                "ignore": 0,
            }
        )
    return pd.DataFrame(rows)


def _patch_network(
    script: Any, monkeypatch: pytest.MonkeyPatch, frames_by_symbol: dict[str, pd.DataFrame]
) -> None:
    def fake_download(url: str, dest: Path, chunk: int = 1 << 16) -> bool:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"stub")
        return True

    def fake_read(zip_path: Path) -> pd.DataFrame:
        # O path inclui .../SYMBOL/timeframe/SYMBOL-tf-YYYY-MM.zip
        parts = zip_path.parts
        symbol = parts[-3]
        return frames_by_symbol[symbol]

    monkeypatch.setattr(script, "download_if_missing", fake_download)
    monkeypatch.setattr(script, "read_zip_as_frame", fake_read)


def _patch_paths(
    script: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    raw = tmp_path / "data" / "raw"
    processed = tmp_path / "data" / "processed"
    manifest = tmp_path / "data" / "datasets.yaml"
    processed.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(script, "data_raw_dir", lambda: raw)
    monkeypatch.setattr(script, "data_processed_dir", lambda: processed)
    monkeypatch.setattr(script, "datasets_manifest_path", lambda: manifest)
    # `processed_dataset_path` é importada no script e usa o módulo original;
    # precisamos também patchar o módulo original para que a função devolva
    # paths no tmp.
    import alpha_forge.io.paths as paths_mod

    monkeypatch.setattr(paths_mod, "data_processed_dir", lambda: processed)


def test_canonical_symbol_normaliza_formas_diversas(script: Any) -> None:
    assert script.canonical_symbol("BTCUSDT") == "BTCUSDT"
    assert script.canonical_symbol("btc/usdt") == "BTCUSDT"
    assert script.canonical_symbol(" btc-usdt ") == "BTCUSDT"
    assert script.canonical_symbol("eth_usdt") == "ETHUSDT"
    with pytest.raises(ValueError):
        script.canonical_symbol("")
    with pytest.raises(ValueError):
        script.canonical_symbol("BTC USDT$")


def test_ingest_dois_simbolos_distintos_nao_colidem(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end = datetime(2025, 1, 31, 23, 0, tzinfo=timezone.utc)
    periods = int((end - start).total_seconds() // 3600) + 1

    frames = {
        "BTCUSDT": _fake_kline_frame(start, periods, base_price=50_000.0),
        "ETHUSDT": _fake_kline_frame(start, periods, base_price=3_000.0),
    }
    _patch_network(script, monkeypatch, frames)
    _patch_paths(script, monkeypatch, tmp_path)

    ctx = script.IngestionContext(
        timeframe="1h",
        start=start,
        end=end,
        raw_root=tmp_path / "data" / "raw",
        processed_root=tmp_path / "data" / "processed",
        manifest_path=tmp_path / "data" / "datasets.yaml",
    )

    out_btc = script.ingest_symbol("BTCUSDT", ctx)
    out_eth = script.ingest_symbol("ETHUSDT", ctx)

    assert out_btc.status == "OK", out_btc.note
    assert out_eth.status == "OK", out_eth.note
    assert out_btc.bars_saved == periods
    assert out_eth.bars_saved == periods
    assert out_btc.parquet_path != out_eth.parquet_path
    assert out_btc.sha256 != out_eth.sha256  # conteúdo distinto → sha distinto
    assert out_btc.dataset_id != out_eth.dataset_id

    manifest_raw = yaml.safe_load(ctx.manifest_path.read_text(encoding="utf-8"))
    ids = {e["dataset_id"] for e in manifest_raw["datasets"]}
    assert out_btc.dataset_id in ids
    assert out_eth.dataset_id in ids

    for entry in manifest_raw["datasets"]:
        assert entry["timezone"] == "UTC"
        assert entry["source"] == "binance_vision_spot"


def test_gap_nao_declarado_bloqueia_ingestao(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end = datetime(2025, 1, 10, 23, 0, tzinfo=timezone.utc)
    periods = int((end - start).total_seconds() // 3600) + 1

    df_full = _fake_kline_frame(start, periods, base_price=100.0)
    # Remove 3 barras no meio → cria gap. Não declaramos.
    gap_rows = [48, 49, 50]
    df_gap = df_full.drop(index=gap_rows).reset_index(drop=True)

    frames = {"SOLUSDT": df_gap}
    _patch_network(script, monkeypatch, frames)
    _patch_paths(script, monkeypatch, tmp_path)

    ctx = script.IngestionContext(
        timeframe="1h",
        start=start,
        end=end,
        raw_root=tmp_path / "data" / "raw",
        processed_root=tmp_path / "data" / "processed",
        manifest_path=tmp_path / "data" / "datasets.yaml",
    )

    out = script.ingest_symbol("SOLUSDT", ctx)
    assert out.status == "REJECTED_UNDECLARED_GAPS"
    assert len(out.gaps_detected) >= 1
    assert not out.parquet_path.exists(), "Parquet órfão não pode ficar em disco"
    assert not ctx.manifest_path.exists(), "Manifesto não pode receber entrada rejeitada"


def test_gap_declarado_permite_ingestao(
    script: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end = datetime(2025, 1, 10, 23, 0, tzinfo=timezone.utc)
    periods = int((end - start).total_seconds() // 3600) + 1

    df_full = _fake_kline_frame(start, periods, base_price=100.0)
    gap_rows = [48, 49, 50]
    df_gap = df_full.drop(index=gap_rows).reset_index(drop=True)
    frames = {"SOLUSDT": df_gap}
    _patch_network(script, monkeypatch, frames)
    _patch_paths(script, monkeypatch, tmp_path)

    gap_start = start + timedelta(hours=48)
    gap_end = start + timedelta(hours=50)
    declared = script.GapRecord(start=gap_start, end=gap_end, reason="test")

    ctx = script.IngestionContext(
        timeframe="1h",
        start=start,
        end=end,
        raw_root=tmp_path / "data" / "raw",
        processed_root=tmp_path / "data" / "processed",
        manifest_path=tmp_path / "data" / "datasets.yaml",
        declared_gaps=[declared],
    )

    out = script.ingest_symbol("SOLUSDT", ctx)
    assert out.status == "OK", out.note
    assert out.parquet_path.exists()
    assert out.bars_saved == periods - 3

    manifest_raw = yaml.safe_load(ctx.manifest_path.read_text(encoding="utf-8"))
    entry = next(
        e for e in manifest_raw["datasets"] if e["dataset_id"] == out.dataset_id
    )
    assert len(entry["declared_gaps"]) == 1
    _ = cast(dict, entry)
