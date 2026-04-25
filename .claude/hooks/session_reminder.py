#!/usr/bin/env python
"""SessionStart hook — reinjeta lembretes de segurança no contexto da sessão.

Contrato do hook:
- stdout é adicionado ao contexto da sessão como system message.
- exit code 0 sempre.

Objetivo: garantir que, mesmo após compactação de contexto, o agente volte
a enxergar as regras de segurança duras do laboratório.

Importado do fork `feature/agentic-pilot-donchian` via ADR-0020.
"""
from __future__ import annotations

import io
import sys

# Windows default stdout é cp1252 e quebra em caracteres UTF-8 como "→".
# Re-wrap para utf-8 com errors="replace" para não quebrar o hook em nenhum ambiente.
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REMINDER = """
[Alpha Forge — laboratório agentic, lembretes persistentes]

1. Live trading está DESABILITADO. Nenhum código envia ordens reais.
   LIVE_TRADING=true é bloqueado por hook (.claude/hooks/block_live_trading.py).

2. Promoção de estágio exige auditoria aprovada. Inicial é backtest_only.
   paper_only só com AUDIT.md(release_decision=paper_only).
   live_trading não é estágio atingível neste repositório.

3. Nunca exponha secrets. .env / chaves / credenciais são bloqueados para edição.
   Ingestão pública (data.binance.vision) é permitida; qualquer venue real é bloqueada.

4. Source of truth = artefatos + git. Decisao -> ADR. Estado -> STATE.md.
   Hipóteses agentic vivem em agentic/active/<slug>/ (SPEC/IMPLEMENTATION/VALIDATION/BACKTEST/AUDIT/CHECKLIST).

5. Leia AGENTS.md antes de escrever código. CLAUDE.md adiciona a camada agentic.
   Camada agentic foi instalada via ADR-0020.
""".strip()


def main() -> int:
    sys.stdout.write(REMINDER + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
