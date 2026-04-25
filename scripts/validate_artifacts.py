"""Valida a presença e coerência mínima dos artefatos agentic de pilotos ativos.

Mesma lógica do Stop hook `.claude/hooks/check_gates.py`, rodada no CI (e localmente).
Modo opt-in — importado via ADR-0020:

- Se NÃO há nenhum piloto em `agentic/active/<slug>/` → exit 0 com "nenhum piloto ativo — OK".
- Caso contrário, verifica para cada piloto: SPEC/IMPLEMENTATION/VALIDATION/BACKTEST/AUDIT/CHECKLIST + STATE.md raiz.
- Exit != 0 se algum artefato essencial ausente ou tiver placeholder.

Uso: `python scripts/validate_artifacts.py`.
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

for _name in ("stdout", "stderr"):
    _stream = getattr(sys, _name, None)
    if _stream is not None and hasattr(_stream, "buffer"):
        setattr(sys, _name, io.TextIOWrapper(_stream.buffer, encoding="utf-8", errors="replace"))

ROOT = Path(__file__).resolve().parents[1]
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


def _check(path: Path, patterns: list[re.Pattern]) -> list[str]:
    if not path.exists():
        return [f"{path.relative_to(ROOT)}: arquivo ausente"]
    text = path.read_text(encoding="utf-8", errors="ignore")
    problems: list[str] = []
    if "{{PLACEHOLDER}}" in text or "{{TODO}}" in text:
        problems.append(f"{path.relative_to(ROOT)}: placeholders não preenchidos")
    for pat in patterns:
        if not pat.search(text):
            problems.append(f"{path.relative_to(ROOT)}: seção faltando /{pat.pattern}/")
    return problems


def main() -> int:
    if not AGENTIC_ACTIVE_DIR.exists():
        print("[validate_artifacts] nenhum piloto ativo (agentic/active/ não existe) — OK.")
        return 0
    pilots = [p for p in AGENTIC_ACTIVE_DIR.iterdir() if p.is_dir()]
    if not pilots:
        print("[validate_artifacts] nenhum piloto ativo (agentic/active/ vazio) — OK.")
        return 0

    problems: list[str] = []
    for name, patterns in ROOT_ARTIFACTS.items():
        problems.extend(_check(ROOT / name, patterns))
    for pilot in pilots:
        for name, patterns in ARTIFACTS.items():
            problems.extend(_check(pilot / name, patterns))

    if problems:
        sys.stderr.write("[validate_artifacts] falhas:\n")
        for p in problems:
            sys.stderr.write(f"  - {p}\n")
        return 1
    print(f"[validate_artifacts] OK — {len(pilots)} piloto(s) ativo(s), todos os artefatos presentes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
