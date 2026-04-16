# `risk/` — módulo 4

## Responsabilidade

Controlar exposição, orçamento de risco e mecanismos de defesa. **Governança**, separada do motor de simulação (ADR-0001: `risk` nunca é mesclado em `backtest`).

## O que ainda não existe

Tudo. Nenhuma política de risco implementada.

Capabilities previstas em `vision/02-scope.md`:

- risco por trade / dia / ativo / estratégia / agregado
- equity guard
- escada de equity
- trailing de equity
- kill switch
- lockout
- risco de liquidação aproximada (com alavancagem até 10x)

## Depende de

`data` (para preços em modelagem de liquidação).

## Primeiro arquivo real esperado

`schemas.py` — modelos pydantic de `RiskBudget` (por trade, dia, ativo, estratégia, portfólio) e `EquityGuardConfig`. Segundo passo: `budget.py` (checagem de budget antes de permitir entrada) e `liquidation.py` (estimativa aproximada de preço de liquidação).

Referência: ADR-0004 (a escrever) formaliza a política completa de risco.
