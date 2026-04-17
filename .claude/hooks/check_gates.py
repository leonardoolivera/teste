#!/usr/bin/env python
"""Stop hook — verifica presença e coerência dos artefatos agentic.

Contrato do hook:
- stdin recebe JSON do evento Stop.
- exit code 2 (com stderr) força o agente a continuar trabalhando.
- exit code 0 libera a parada.

Regra: se existe pelo menos um artefato agentic (SPEC/IMPLEMENTATION/VALIDATION/...)
com marcador `status: active` ou similar, então TODOS devem existir.
Caso contrário, os artefatos são tratados como templates vazios e a sessão pode parar.

Gates checados:
- SPEC.md existe e não contém apenas placeholder {{...}} sem substituição.
- IMPLEMENTATION.md existe e referencia pelo menos um arquivo real de src/.
- VALIDATION.md existe e tem seção de testes executados.
- BACKTEST.md existe e tem seção de métricas preenchida.
- AUDIT.md existe e tem release_decision.
- CHECKLIST.md existe.
- STATE.md raiz existe (protocolo do AGENTS.md).

Falha é informativa, não agressiva: o hook pede para continuar mas deixa claro
qual gate está faltando. Usuário pode sobrescrever a paralisação explicitamente
através da próxima prompt.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ARTIFACTS = {
    "SPEC.md": [
        re.compile(r"##\s*Hip[óo]tese", re.IGNORECASE),
        re.compile(r"##\s*Mercado", re.IGNORECASE),
        re.compile(r"##\s*Entradas?", re.IGNORECASE),
        re.compile(r"##\s*Sa[íi]das?", re.IGNORECASE),
    ],
    "IMPLEMENTATION.md": [
        re.compile(r"##\s*Arquivos alterados", re.IGNORECASE),
        re.compile(r"##\s*Mapeamento SPEC", re.IGNORECASE),
    ],
    "VALIDATION.md": [
        re.compile(r"##\s*Testes executados", re.IGNORECASE),
        re.compile(r"##\s*Conformidade", re.IGNORECASE),
    ],
    "BACKTEST.md": [
        re.compile(r"##\s*Dataset", re.IGNORECASE),
        re.compile(r"##\s*M[ée]tricas", re.IGNORECASE),
    ],
    "AUDIT.md": [
        re.compile(r"##\s*Blockers", re.IGNORECASE),
        re.compile(r"release[_ ]decision\s*:", re.IGNORECASE),
    ],
    "CHECKLIST.md": [
        re.compile(r"pesquisa", re.IGNORECASE),
        re.compile(r"implementa", re.IGNORECASE),
        re.compile(r"valida", re.IGNORECASE),
        re.compile(r"auditoria", re.IGNORECASE),
    ],
    "STATE.md": [
        re.compile(r"current phase", re.IGNORECASE),
    ],
}


def _read_event() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _gate_status(path: Path, required_sections: list[re.Pattern]) -> tuple[bool, list[str]]:
    if not path.exists():
        return False, [f"arquivo ausente: {path.name}"]
    text = path.read_text(encoding="utf-8", errors="ignore")
    missing = []
    if "{{PLACEHOLDER}}" in text or "{{TODO}}" in text:
        missing.append("contém placeholders não preenchidos ({{PLACEHOLDER}}/{{TODO}})")
    for pat in required_sections:
        if not pat.search(text):
            missing.append(f"seção faltando: /{pat.pattern}/")
    return (len(missing) == 0), missing


def _is_stop_hook_active(event: dict) -> bool:
    stop_hook_active = event.get("stop_hook_active")
    return bool(stop_hook_active)


def main() -> int:
    event = _read_event()
    if _is_stop_hook_active(event):
        return 0

    problems: list[str] = []
    for name, sections in ARTIFACTS.items():
        ok, missing = _gate_status(ROOT / name, sections)
        if not ok:
            problems.append(f"- {name}: " + "; ".join(missing))

    if not problems:
        return 0

    message = (
        "[check_gates] Artefatos agentic incompletos — não pare ainda.\n"
        "Continue preenchendo os gates faltantes antes de encerrar:\n"
        + "\n".join(problems)
        + "\n\nSe o piloto estiver inativo no momento, atualize STATE.md documentando."
    )
    sys.stderr.write(message + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
