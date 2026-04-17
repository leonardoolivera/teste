#!/usr/bin/env python
"""SessionStart hook — reinjeta lembretes de segurança no contexto da sessão.

Contrato do hook:
- stdout é adicionado ao contexto da sessão como system message.
- exit code 0 sempre.

Objetivo: garantir que, mesmo após compactação de contexto, o agente volte
a enxergar as regras de segurança duras do laboratório.
"""
from __future__ import annotations

import sys

REMINDER = """
[Alpha Forge — laboratório agentic, lembretes persistentes]

1. Live trading está DESABILITADO. Nenhum código envia ordens reais.
   LIVE_TRADING=true é bloqueado por hook (.claude/hooks/block_live_trading.py).

2. Promoção de estágio exige auditoria aprovada. Inicial é backtest_only.
   paper_only só com AUDIT.md(release_decision=paper_only).
   live_trading não é estágio atingível neste repositório.

3. Nunca exponha secrets. .env / chaves / credenciais são bloqueados para edição.
   Ingestão pública (data.binance.vision) é permitida; qualquer venue real é bloqueada.

4. Source of truth = artefatos + git. Decisão → ADR. Estado → STATE.md.
   Hipótese → SPEC/IMPLEMENTATION/VALIDATION/BACKTEST/AUDIT/CHECKLIST.

5. Leia AGENTS.md antes de escrever código. CLAUDE.md adiciona a camada agentic.
""".strip()


def main() -> int:
    sys.stdout.write(REMINDER + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
