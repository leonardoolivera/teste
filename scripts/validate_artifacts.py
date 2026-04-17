"""Valida a presença e coerência mínima dos artefatos agentic.

Mesma lógica do hook Stop, rodada no CI (e localmente). Falha com exit != 0
se algum artefato essencial estiver ausente ou tiver só placeholder.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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
    "STATE.md": [
        re.compile(r"current phase", re.IGNORECASE),
    ],
    "ASSUMPTIONS.md": [
        re.compile(r"^#", re.IGNORECASE | re.MULTILINE),
    ],
}


def main() -> int:
    problems: list[str] = []
    for name, patterns in ARTIFACTS.items():
        path = ROOT / name
        if not path.exists():
            problems.append(f"{name}: arquivo ausente")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "{{PLACEHOLDER}}" in text or "{{TODO}}" in text:
            problems.append(f"{name}: placeholders não preenchidos")
        for pat in patterns:
            if not pat.search(text):
                problems.append(f"{name}: seção faltando /{pat.pattern}/")
    if problems:
        sys.stderr.write("[validate_artifacts] falhas:\n")
        for p in problems:
            sys.stderr.write(f"  - {p}\n")
        return 1
    print("[validate_artifacts] OK — todos os artefatos presentes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
