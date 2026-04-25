"""Helper para gerar 6 artefatos agentic de um piloto (SPEC/IMPL/VAL/BACKTEST/AUDIT/CHECKLIST).

Uso: importar ``write_pilot(config: dict)``. Não é parte do contrato público — ferramenta
interna para acelerar batches H.6-H.10 após plateau confirmado em H.1-H.5.

Cada piloto recebe um dict com: slug, title, hypothesis, dataset_id, regime_filter_canonical,
entry_window, exit_window, metrics (baseline + folds + mc + scenarios), release_decision,
critérios_status, lessons, command.
"""

from __future__ import annotations

from pathlib import Path


def write_pilot(cfg: dict) -> None:
    slug = cfg["slug"]
    root = Path(__file__).resolve().parents[1] / "agentic" / "active" / slug
    root.mkdir(parents=True, exist_ok=True)

    (root / "SPEC.md").write_text(cfg["spec"], encoding="utf-8")
    (root / "IMPLEMENTATION.md").write_text(cfg["implementation"], encoding="utf-8")
    (root / "VALIDATION.md").write_text(cfg["validation"], encoding="utf-8")
    (root / "BACKTEST.md").write_text(cfg["backtest"], encoding="utf-8")
    (root / "AUDIT.md").write_text(cfg["audit"], encoding="utf-8")
    (root / "CHECKLIST.md").write_text(cfg["checklist"], encoding="utf-8")
