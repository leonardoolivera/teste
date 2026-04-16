"""Ingesta klines mensais de Binance Vision (ADR-0009).

Fluxo por símbolo:
  1. Baixa ZIPs mensais em ``data/raw/binance_vision/<SYMBOL>/<INTERVAL>/``.
  2. Descompacta e concatena todos os CSVs cobrindo a janela ``[start, end]``.
  3. Filtra para a janela exata; converte para OHLCV `DataFrame` com
     `DatetimeIndex` timezone-aware (UTC).
  4. Detecta gaps (buracos não cobertos pela grade do timeframe) — não
     preenche nada; apenas reporta.
  5. Escreve Parquet em ``data/processed/<SYMBOL>/<INTERVAL>/<dataset_id>.parquet``.
  6. Atualiza ``data/datasets.yaml`` com entrada pydantic-validada.

Guardrails (ADR-0009):
  - Símbolo é normalizado para forma canônica única (upper, sem barra/traço)
    logo na entrada — nenhum módulo downstream decide forma.
  - `timezone` e `source` são campos obrigatórios, preenchidos pelo script.
  - Gap detectado é reportado; não há preenchimento silencioso. Se houver
    qualquer gap, o operador precisa declará-los explicitamente na CLI
    (`--declared-gap start,end,reason`) para o dataset ser aceito.
  - Multi-símbolo de verdade: nenhum ramo `if symbol == "BTCUSDT"`.
  - Código de rede mora só aqui. `src/` não importa este módulo.

Uso:
    uv run python scripts/ingest_binance_vision.py \\
        --symbols BTCUSDT --timeframe 1h \\
        --start 2025-07-05 --end 2025-12-31

    uv run python scripts/ingest_binance_vision.py \\
        --symbols BTCUSDT,ETHUSDT,SOLUSDT --timeframe 1h \\
        --start 2025-07-05 --end 2025-12-31 \\
        --declared-gap 2025-08-12T00:00:00Z,2025-08-12T02:00:00Z,"Binance maintenance"
"""

from __future__ import annotations

import argparse
import hashlib
import io
import ssl
import sys
import urllib.error
import urllib.request
import zipfile

import certifi
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import cast

import pandas as pd
import yaml

from alpha_forge.data.schemas import DatasetManifest, GapRecord
from alpha_forge.data.synthetic import TIMEFRAME_DELTAS
from alpha_forge.io.paths import (
    data_processed_dir,
    data_raw_dir,
    datasets_manifest_path,
    processed_dataset_path,
)


BINANCE_VISION_BASE = "https://data.binance.vision/data/spot/monthly/klines"
KLINE_COLUMNS = [
    "open_time_ms",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time_ms",
    "quote_volume",
    "trades",
    "taker_buy_base",
    "taker_buy_quote",
    "ignore",
]


@dataclass
class IngestionOutcome:
    symbol: str
    timeframe: str
    start: datetime
    end: datetime
    dataset_id: str
    parquet_path: Path
    bars_saved: int
    gaps_detected: list[tuple[datetime, datetime]]
    sha256: str
    status: str
    note: str = ""


@dataclass
class IngestionContext:
    timeframe: str
    start: datetime
    end: datetime
    raw_root: Path
    processed_root: Path
    manifest_path: Path
    declared_gaps: list[GapRecord] = field(default_factory=list)
    source_tag: str = "binance_vision_spot"


def canonical_symbol(raw: str) -> str:
    """Forma canônica única: upper, sem barra/traço/underscore/espaço.

    Usada no manifest, no path e na URL de Binance Vision. Normalizar na
    borda (entrada do script) garante que nada downstream precisa decidir
    formato.
    """
    cleaned = raw.strip().upper().replace("/", "").replace("-", "").replace("_", "")
    if not cleaned:
        raise ValueError(f"símbolo vazio após normalização: {raw!r}")
    if not cleaned.isalnum():
        raise ValueError(f"símbolo com caractere inválido após normalização: {cleaned!r}")
    return cleaned


def months_between(start: datetime, end: datetime) -> list[tuple[int, int]]:
    """Lista de (ano, mês) cobrindo [start, end], ambos inclusivos."""
    cur = date(start.year, start.month, 1)
    stop = date(end.year, end.month, 1)
    months: list[tuple[int, int]] = []
    while cur <= stop:
        months.append((cur.year, cur.month))
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)
    return months


def monthly_zip_url(symbol: str, timeframe: str, year: int, month: int) -> str:
    tag = f"{symbol}-{timeframe}-{year:04d}-{month:02d}"
    return f"{BINANCE_VISION_BASE}/{symbol}/{timeframe}/{tag}.zip"


def download_if_missing(url: str, dest: Path, chunk: int = 1 << 16) -> bool:
    """Baixa o ZIP se não existir localmente. Retorna True se baixou.

    404 em Binance Vision significa "mês ainda não publicado"; nesse caso
    logamos e continuamos — o chamador decide se isso é um gap legítimo ou
    uma falha (via janela pedida × meses disponíveis).
    """
    if dest.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    ctx_ssl = ssl.create_default_context(cafile=certifi.where())
    try:
        with urllib.request.urlopen(url, context=ctx_ssl) as resp, tmp.open("wb") as fh:
            while True:
                buf = resp.read(chunk)
                if not buf:
                    break
                fh.write(buf)
    except urllib.error.HTTPError as err:
        tmp.unlink(missing_ok=True)
        if err.code == 404:
            return False
        raise
    tmp.replace(dest)
    return True


def read_zip_as_frame(zip_path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist() if n.endswith(".csv")]
        if len(names) != 1:
            raise RuntimeError(f"ZIP inesperado em {zip_path}: {names}")
        with zf.open(names[0]) as fh:
            raw = fh.read()
    return _parse_kline_csv(raw)


def _parse_kline_csv(raw: bytes) -> pd.DataFrame:
    """Binance Vision kline CSV: 12 cols, sem header (ou com — a primeira
    linha às vezes é cabeçalho em dumps recentes)."""
    buf = io.BytesIO(raw)
    first = raw.split(b"\n", 1)[0]
    has_header = b"open_time" in first
    df = pd.read_csv(
        buf,
        header=0 if has_header else None,
        names=KLINE_COLUMNS,
        skiprows=1 if has_header else 0,
    )
    return df


def normalize_frame(
    df_raw: pd.DataFrame, start: datetime, end: datetime
) -> pd.DataFrame:
    """Converte frame cru de Binance Vision em OHLCV canônico do Alpha Forge."""
    # Binance Vision às vezes publica open_time em microssegundos (16 dígitos)
    # em vez de milissegundos (13). Detectamos pela magnitude.
    sample = int(cast(int, df_raw["open_time_ms"].iloc[0]))
    unit = "us" if sample > 10**14 else "ms"
    ts = pd.to_datetime(df_raw["open_time_ms"], unit=unit, utc=True)
    df = pd.DataFrame(
        {
            "open": df_raw["open"].astype(float).to_numpy(),
            "high": df_raw["high"].astype(float).to_numpy(),
            "low": df_raw["low"].astype(float).to_numpy(),
            "close": df_raw["close"].astype(float).to_numpy(),
            "volume": df_raw["volume"].astype(float).to_numpy(),
        },
        index=pd.DatetimeIndex(ts.to_numpy(), name="timestamp", tz="UTC"),
    )
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="first")]
    mask = (df.index >= start) & (df.index <= end)
    return df.loc[mask]


def detect_gaps(
    index: pd.DatetimeIndex, timeframe: str
) -> list[tuple[datetime, datetime]]:
    step = TIMEFRAME_DELTAS[timeframe]
    if len(index) < 2:
        return []
    expected = pd.Timedelta(step)
    deltas = index[1:] - index[:-1]
    gaps: list[tuple[datetime, datetime]] = []
    for i, d in enumerate(deltas):
        if d == expected:
            continue
        g_start = cast(pd.Timestamp, index[i] + expected).to_pydatetime()
        g_end = cast(pd.Timestamp, index[i + 1] - expected).to_pydatetime()
        gaps.append((g_start, g_end))
    return gaps


def filter_declared(
    gaps: list[tuple[datetime, datetime]], declared: list[GapRecord]
) -> list[tuple[datetime, datetime]]:
    """Retorna apenas os gaps NÃO cobertos por algum `declared`."""
    undeclared: list[tuple[datetime, datetime]] = []
    for g_start, g_end in gaps:
        if any(d.start <= g_start and d.end >= g_end for d in declared):
            continue
        undeclared.append((g_start, g_end))
    return undeclared


def dataset_id_for(symbol: str, timeframe: str, start: datetime, end: datetime) -> str:
    return (
        f"{symbol.lower()}_{timeframe}_"
        f"{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}_binance_spot"
    )


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def ingest_symbol(symbol_raw: str, ctx: IngestionContext) -> IngestionOutcome:
    symbol = canonical_symbol(symbol_raw)
    dsid = dataset_id_for(symbol, ctx.timeframe, ctx.start, ctx.end)
    parquet_path = processed_dataset_path(symbol, ctx.timeframe, dsid)

    raw_dir = ctx.raw_root / "binance_vision" / symbol / ctx.timeframe
    raw_dir.mkdir(parents=True, exist_ok=True)

    frames: list[pd.DataFrame] = []
    missing_months: list[tuple[int, int]] = []
    for year, month in months_between(ctx.start, ctx.end):
        tag = f"{symbol}-{ctx.timeframe}-{year:04d}-{month:02d}"
        zip_path = raw_dir / f"{tag}.zip"
        url = monthly_zip_url(symbol, ctx.timeframe, year, month)
        downloaded = download_if_missing(url, zip_path)
        if not zip_path.exists():
            missing_months.append((year, month))
            continue
        df_m = read_zip_as_frame(zip_path)
        frames.append(df_m)
        if downloaded:
            print(f"  [get] {url}")
        else:
            print(f"  [cache] {zip_path.name}")

    if not frames:
        return IngestionOutcome(
            symbol=symbol,
            timeframe=ctx.timeframe,
            start=ctx.start,
            end=ctx.end,
            dataset_id=dsid,
            parquet_path=parquet_path,
            bars_saved=0,
            gaps_detected=[],
            sha256="",
            status="FAILED",
            note=f"nenhum mês obtido (missing={missing_months})",
        )

    df_all = pd.concat(frames, axis=0)
    df = normalize_frame(df_all, ctx.start, ctx.end)

    if df.empty:
        return IngestionOutcome(
            symbol=symbol,
            timeframe=ctx.timeframe,
            start=ctx.start,
            end=ctx.end,
            dataset_id=dsid,
            parquet_path=parquet_path,
            bars_saved=0,
            gaps_detected=[],
            sha256="",
            status="FAILED",
            note="nenhuma barra na janela pedida após filtro",
        )

    gaps_all = detect_gaps(cast(pd.DatetimeIndex, df.index), ctx.timeframe)
    undeclared = filter_declared(gaps_all, ctx.declared_gaps)

    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, engine="pyarrow", compression="snappy")
    sha = sha256_of_file(parquet_path)

    first_ts = cast(pd.Timestamp, df.index[0]).to_pydatetime()
    last_ts = cast(pd.Timestamp, df.index[-1]).to_pydatetime()
    relative = parquet_path.relative_to(data_processed_dir())

    entry = DatasetManifest(
        dataset_id=dsid,
        symbol=symbol,
        timeframe=ctx.timeframe,
        path=str(relative).replace("\\", "/"),
        sha256=sha,
        row_count=len(df),
        start_ts=first_ts,
        end_ts=last_ts,
        timezone="UTC",
        declared_gaps=ctx.declared_gaps,
        source=ctx.source_tag,
    )

    if undeclared:
        # Removemos o Parquet para não deixar artefato órfão que o loader
        # rejeitaria em silêncio. Operador precisa declarar e re-rodar.
        parquet_path.unlink(missing_ok=True)
        return IngestionOutcome(
            symbol=symbol,
            timeframe=ctx.timeframe,
            start=ctx.start,
            end=ctx.end,
            dataset_id=dsid,
            parquet_path=parquet_path,
            bars_saved=len(df),
            gaps_detected=gaps_all,
            sha256=sha,
            status="REJECTED_UNDECLARED_GAPS",
            note=(
                f"{len(undeclared)} gap(s) não declarado(s); "
                "declare via --declared-gap e rode de novo"
            ),
        )

    _upsert_manifest(entry, ctx.manifest_path)

    return IngestionOutcome(
        symbol=symbol,
        timeframe=ctx.timeframe,
        start=ctx.start,
        end=ctx.end,
        dataset_id=dsid,
        parquet_path=parquet_path,
        bars_saved=len(df),
        gaps_detected=gaps_all,
        sha256=sha,
        status="OK",
        note=(
            f"{len(ctx.declared_gaps)} gap(s) declarado(s)"
            if ctx.declared_gaps
            else "sem gaps"
        ),
    )


def _upsert_manifest(entry: DatasetManifest, manifest_path: Path) -> None:
    existing: list[dict[str, object]] = []
    if manifest_path.exists():
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        existing = cast(list[dict[str, object]], raw.get("datasets", []))
    updated = [
        e for e in existing if e.get("dataset_id") != entry.dataset_id
    ] + [entry.model_dump(mode="json")]
    updated.sort(key=lambda e: cast(str, e["dataset_id"]))
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        "# Manifesto de datasets (ADR-0005). Versionável no git.\n"
        "# Os arquivos Parquet são regeneráveis via scripts/bootstrap_* e scripts/ingest_*.\n\n"
        + yaml.safe_dump({"datasets": updated}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _parse_iso(value: str) -> datetime:
    # Aceita "2025-07-05" (00:00 UTC) ou ISO completo com timezone.
    if "T" not in value:
        dt = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return dt
    # Python 3.12+ aceita "Z" em fromisoformat; normalizamos para robustez.
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _parse_declared_gap(value: str) -> GapRecord:
    parts = value.split(",", 2)
    if len(parts) < 2:
        raise argparse.ArgumentTypeError(
            f"--declared-gap espera 'start,end[,reason]', recebeu: {value!r}"
        )
    start = _parse_iso(parts[0].strip())
    end = _parse_iso(parts[1].strip())
    reason = parts[2].strip() if len(parts) == 3 else ""
    return GapRecord(start=start, end=end, reason=reason)


def _summary_line(o: IngestionOutcome) -> str:
    window = f"{o.start.isoformat()} -> {o.end.isoformat()}"
    return (
        f"  symbol={o.symbol}  timeframe={o.timeframe}\n"
        f"  window={window}\n"
        f"  bars_saved={o.bars_saved}  gaps_detected={len(o.gaps_detected)}\n"
        f"  dataset_id={o.dataset_id}\n"
        f"  sha256={o.sha256 or '-'}\n"
        f"  status={o.status}  {o.note}"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Ingesta Binance Vision (ADR-0009).")
    p.add_argument(
        "--symbols",
        required=True,
        help="Lista separada por vírgula (ex: BTCUSDT,ETHUSDT,SOLUSDT).",
    )
    p.add_argument("--timeframe", required=True, help="Ex: 1h, 4h, 1d.")
    p.add_argument("--start", required=True, help="YYYY-MM-DD ou ISO8601.")
    p.add_argument("--end", required=True, help="YYYY-MM-DD ou ISO8601.")
    p.add_argument(
        "--declared-gap",
        action="append",
        default=[],
        type=_parse_declared_gap,
        metavar="START,END[,REASON]",
        help="Gap declarado, pode ser repetido. Intervalo inclusivo em UTC.",
    )
    args = p.parse_args(argv)

    if args.timeframe not in TIMEFRAME_DELTAS:
        print(f"[erro] timeframe não suportado: {args.timeframe}", file=sys.stderr)
        return 2

    start = _parse_iso(args.start)
    end = _parse_iso(args.end)
    if end < start:
        print("[erro] --end antes de --start", file=sys.stderr)
        return 2

    # End exclusivo de meia-noite? Não. Usuário pede end explícito; mantemos
    # inclusivo. Para incluir o dia inteiro, ajustamos para 23:59:59 se for
    # apenas data.
    if "T" not in args.end:
        end = end + timedelta(hours=23, minutes=59, seconds=59)

    symbols = [s for s in args.symbols.split(",") if s.strip()]
    if not symbols:
        print("[erro] --symbols vazio", file=sys.stderr)
        return 2

    ctx = IngestionContext(
        timeframe=args.timeframe,
        start=start,
        end=end,
        raw_root=data_raw_dir(),
        processed_root=data_processed_dir(),
        manifest_path=datasets_manifest_path(),
        declared_gaps=list(args.declared_gap),
    )

    outcomes: list[IngestionOutcome] = []
    for sym in symbols:
        print(f"\n[ingest] {sym}")
        try:
            outcome = ingest_symbol(sym, ctx)
        except Exception as exc:  # noqa: BLE001 — queremos reportar sem abortar os outros
            outcome = IngestionOutcome(
                symbol=canonical_symbol(sym) if sym.strip() else sym,
                timeframe=ctx.timeframe,
                start=ctx.start,
                end=ctx.end,
                dataset_id="-",
                parquet_path=Path("-"),
                bars_saved=0,
                gaps_detected=[],
                sha256="",
                status="ERROR",
                note=f"{type(exc).__name__}: {exc}",
            )
        outcomes.append(outcome)

    print("\n=== RESUMO ===")
    for o in outcomes:
        print(_summary_line(o))

    any_failed = any(o.status != "OK" for o in outcomes)
    return 1 if any_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
