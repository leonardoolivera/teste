#!/usr/bin/env python
"""PreToolUse hook — bloqueia qualquer tentativa de habilitar live trading ou tocar em secrets.

Contrato do hook (Claude Code):
- stdin recebe JSON com {tool_name, tool_input, ...}
- exit code != 0 bloqueia a tool call; stderr vira feedback ao agente
- exit code 0 libera

Regras (em ordem de avaliação):
1. Bloqueia LIVE_TRADING=true em qualquer comando ou arquivo sendo escrito.
2. Bloqueia edição/escrita de arquivos de secrets (.env, .env.*, secrets*, *.pem, *.key, credentials*).
3. Bloqueia imports/chamadas de venues reais (ccxt, binance.client, exchange.create_order, etc.)
   quando sendo escritos em src/.
4. Bloqueia URLs de endpoints reais de trading em configs ou código.

Exceção explícita: data.binance.vision é URL pública de histórico e é PERMITIDA.

Este hook é a última linha de defesa. Se bloquear algo legítimo, abra ADR
documentando o caso — não relaxe a regra.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LIVE_FLAG_PATTERNS = (
    re.compile(r"\bLIVE_TRADING\s*=\s*(?:true|1|TRUE|True|yes|YES|on|ON)\b"),
    re.compile(r"\blive_trading\s*:\s*(?:true|yes|on)\b"),
    re.compile(r"\brelease_mode\s*[:=]\s*['\"]?live['\"]?"),
)

SECRET_PATH_PATTERNS = (
    re.compile(r"(^|[\\/])\.env(\.|$)"),
    re.compile(r"secrets\b"),
    re.compile(r"credentials\b"),
    re.compile(r"\.pem$"),
    re.compile(r"\.key$"),
    re.compile(r"(^|[\\/])id_rsa\b"),
)

BLOCKED_VENUE_PATTERNS = (
    re.compile(r"\bimport\s+ccxt\b"),
    re.compile(r"\bfrom\s+ccxt\b"),
    re.compile(r"\bimport\s+binance\.client\b"),
    re.compile(r"\bfrom\s+binance\.client\b"),
    re.compile(r"\.create_order\s*\("),
    re.compile(r"\.place_order\s*\("),
    re.compile(r"\.execute_order\s*\("),
    re.compile(r"\.futures_create_order\s*\("),
    re.compile(r"\.submit_order\s*\("),
)

BLOCKED_TRADING_ENDPOINTS = (
    re.compile(r"\bapi\.binance\.com\b"),
    re.compile(r"\bfapi\.binance\.com\b"),
    re.compile(r"\bapi\.bybit\.com\b"),
    re.compile(r"\bapi\.okx\.com\b"),
    re.compile(r"\bapi\.kraken\.com\b"),
    re.compile(r"\bapi\.coinbase\.com\b"),
    re.compile(r"\bapi\.huobi\.pro\b"),
    re.compile(r"\bapi\.kucoin\.com\b"),
)

ALLOWED_ENDPOINTS = (re.compile(r"\bdata\.binance\.vision\b"),)

NETWORK_ALLOWED_FILES = (
    re.compile(r"(^|[\\/])scripts[\\/]ingest_binance_vision\.py$"),
)


def _read_event() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _block(reason: str) -> None:
    sys.stderr.write(
        f"[block_live_trading] BLOQUEADO: {reason}\n"
        "Se este bloqueio for falso positivo, abra uma ADR documentando o caso.\n"
        "Política em CLAUDE.md §2 e ASSUMPTIONS.md A4.\n"
    )
    sys.exit(2)


def _scan_text(text: str, *, file_path: str | None = None) -> None:
    for pat in LIVE_FLAG_PATTERNS:
        if pat.search(text):
            _block(f"tentativa de habilitar live trading (match: {pat.pattern})")

    if file_path is None or not any(p.search(file_path) for p in NETWORK_ALLOWED_FILES):
        if file_path is None or file_path.startswith(("src", "src/", "src\\")) or "src/alpha_forge" in file_path.replace("\\", "/"):
            for pat in BLOCKED_VENUE_PATTERNS:
                if pat.search(text):
                    _block(f"uso de venue real em código de produção (match: {pat.pattern})")

    for pat in BLOCKED_TRADING_ENDPOINTS:
        if pat.search(text):
            if any(ap.search(text) for ap in ALLOWED_ENDPOINTS):
                continue
            _block(f"endpoint de produção de trading detectado (match: {pat.pattern})")


def _check_bash(tool_input: dict) -> None:
    command = tool_input.get("command", "") or ""
    _scan_text(command)
    for pat in BLOCKED_VENUE_PATTERNS:
        if pat.search(command):
            _block(f"comando tentando invocar venue real (match: {pat.pattern})")


def _check_file_op(tool_input: dict) -> None:
    file_path = (
        tool_input.get("file_path")
        or tool_input.get("path")
        or tool_input.get("notebook_path")
        or ""
    )
    normalized = file_path.replace("\\", "/")
    for pat in SECRET_PATH_PATTERNS:
        if pat.search(normalized):
            _block(f"edição de arquivo de secrets bloqueada: {file_path}")

    content_fields = ("content", "new_string", "new_source")
    for field in content_fields:
        value = tool_input.get(field)
        if isinstance(value, str) and value:
            _scan_text(value, file_path=normalized)


def main() -> int:
    event = _read_event()
    tool_name = event.get("tool_name") or event.get("tool") or ""
    tool_input = event.get("tool_input") or event.get("input") or {}
    if not isinstance(tool_input, dict):
        return 0
    try:
        if tool_name == "Bash":
            _check_bash(tool_input)
        elif tool_name in {"Edit", "Write", "NotebookEdit"}:
            _check_file_op(tool_input)
    except SystemExit:
        raise
    except Exception as exc:
        sys.stderr.write(f"[block_live_trading] hook error (fail-open): {exc}\n")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
