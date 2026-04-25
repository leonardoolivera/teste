# IMPLEMENTATION.md — {{NOME DA ESTRATÉGIA}}

> **Template.** Copie para `agentic/active/<slug>/IMPLEMENTATION.md` e preencha. Remova este bloco de nota ao finalizar.
> Produzido pelo `strategy-implementer` a partir do `SPEC.md` aprovado.

---

## Arquivos alterados

{{Lista de arquivos tocados, com resumo de uma linha por arquivo.}}

| Path | Papel |
|---|---|
| `src/alpha_forge/strategies/families/{{familia}}/strategy.py` | {{resumo}} |
| `src/alpha_forge/cli/app.py` | {{resumo, ex: nova flag `--{{param}}`}} |
| `tests/unit/test_{{familia}}.py` | {{classes de teste}} |
| `tests/property/test_{{familia}}_causal.py` | {{property-based causalidade}} |

## Mapeamento SPEC → código

{{Tabela ligando cada seção do SPEC ao trecho de código que a implementa. Se alguma seção está sem código, marca `GAP` em vez de inventar.}}

| SPEC §seção | Código (path:linhas) | Nota |
|---|---|---|
| Hipótese | — | decisão, não código |
| Entradas | `{{path}}:{{linhas}}` | {{observação}} |
| Saídas | `{{path}}:{{linhas}}` | {{observação}} |
| Stops | `{{path}}:{{linhas}}` ou `GAP` | {{razão se gap}} |
| Sizing | via `fixed_fractional_position_sizing` (ADR-0004) | — |
| Fees/Slippage/Spread | via `CostModel` (ADR-0006 + ADR-0019) | — |

## Decisões técnicas

{{Escolhas de implementação que o SPEC não ditou. Exemplos: hot path via `numpy` vs `pandas`, cache de rolling, ordem de validação de parâmetros, etc.}}

## Gaps

{{O que ficou fora do escopo desta entrega, com motivo. Não esconda gap para fingir completude. Cada gap deve ter ADR-candidata OU razão de "fora do SPEC".}}

- {{gap 1}} — razão: {{...}}
- {{gap 2}} — razão: {{...}}

## Suíte de testes

- **Comando:** `python -m pytest -q` (ou `uv run pytest -q`).
- **Resultado:** `{{N}} passed, {{M}} skipped`.
- **Adições desta entrega:** {{+X unit, +Y property, +Z integration}}.
