#!/usr/bin/env python
"""Stop hook — verifica presença e coerência dos artefatos agentic de um piloto ATIVO.

Contrato do hook:
- stdin recebe JSON do evento Stop.
- exit code 2 (com stderr) força o agente a continuar trabalhando.
- exit code 0 libera a parada.

Modo opt-in (adaptado de ADR-0020 em relação à versão original do fork):

- Hipóteses agentic vivem em `agentic/active/<slug>/` — cada diretório é UM piloto.
- Se NÃO há diretório `agentic/active/` com pelo menos um sub-diretório → retorna 0 silenciosamente.
- Para cada piloto ativo em `agentic/active/<slug>/`: verifica presença e coerência dos
  6 artefatos (SPEC/IMPLEMENTATION/VALIDATION/BACKTEST/AUDIT/CHECKLIST) + STATE.md raiz.
- Se qualquer piloto tem gap → exit 2 + stderr informativo.

A separação entre "template" (em `agentic/templates/`) e "piloto ativo" (em `agentic/active/<slug>/`)
garante que a camada agentic não dispara falsos positivos durante desenvolvimento de infra
(caso típico: trabalhar em ADRs/system sem um piloto em andamento).

Gates checados por piloto ativo:
- SPEC.md existe e tem seções Hipótese / Mercado / Entradas / Saídas.
- IMPLEMENTATION.md existe e tem Arquivos alterados / Mapeamento SPEC.
- VALIDATION.md existe e tem Testes executados / Conformidade.
- BACKTEST.md existe e tem Dataset / Métricas.
- AUDIT.md existe e tem Blockers / release_decision.
- CHECKLIST.md existe e menciona pesquisa / implementação / validação / auditoria.
- STATE.md (raiz) existe com "current phase".

Importado do fork `feature/agentic-pilot-donchian` via ADR-0020, com modo opt-in adicionado.
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

# Windows default stdout/stderr é cp1252 e quebra em UTF-8; re-wrap com fallback.
for _name in ("stdout", "stderr"):
    _stream = getattr(sys, _name, None)
    if _stream is not None and hasattr(_stream, "buffer"):
        setattr(sys, _name, io.TextIOWrapper(_stream.buffer, encoding="utf-8", errors="replace"))

ROOT = Path(__file__).resolve().parents[2]
AGENTIC_ACTIVE_DIR = ROOT / "agentic" / "active"

ARTIFACTS: dict[str, list[re.Pattern]] = {
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
}

ROOT_ARTIFACTS: dict[str, list[re.Pattern]] = {
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
    missing: list[str] = []
    if "{{PLACEHOLDER}}" in text or "{{TODO}}" in text:
        missing.append("contém placeholders não preenchidos ({{PLACEHOLDER}}/{{TODO}})")
    for pat in required_sections:
        if not pat.search(text):
            missing.append(f"seção faltando: /{pat.pattern}/")
    return (len(missing) == 0), missing


def _is_stop_hook_active(event: dict) -> bool:
    return bool(event.get("stop_hook_active"))


def _active_pilots() -> list[Path]:
    if not AGENTIC_ACTIVE_DIR.exists():
        return []
    return [p for p in AGENTIC_ACTIVE_DIR.iterdir() if p.is_dir()]


def main() -> int:
    event = _read_event()
    if _is_stop_hook_active(event):
        return 0

    pilots = _active_pilots()
    if not pilots:
        return 0

    problems: list[str] = []
    for name, sections in ROOT_ARTIFACTS.items():
        ok, missing = _gate_status(ROOT / name, sections)
        if not ok:
            problems.append(f"- {name} (raiz): " + "; ".join(missing))

    for pilot_dir in pilots:
        for name, sections in ARTIFACTS.items():
            ok, missing = _gate_status(pilot_dir / name, sections)
            if not ok:
                problems.append(f"- agentic/active/{pilot_dir.name}/{name}: " + "; ".join(missing))

    if not problems:
        return 0

    message = (
        "[check_gates] Artefatos agentic incompletos — não pare ainda.\n"
        "Continue preenchendo os gates faltantes antes de encerrar:\n"
        + "\n".join(problems)
        + "\n\nSe o piloto estiver inativo no momento, mova a pasta para agentic/inactive/ "
        "ou remova-a e atualize STATE.md documentando."
    )
    sys.stderr.write(message + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
