# 0031 — JSON-schema formal dos manifests `exports/approved/*.json` (v3+)

**Status:** Accepted
**Date:** 2026-04-18
**Deciders:** Usuário (owner do projeto) + agente.

## Context

Manifests v1 (ADR-0028) e v2 (ADR-0029) de `bollinger_width_regime` foram escritos à mão seguindo o schema informal descrito em `AGENTS.md §8` (Export contract). O handoff de 2026-04-18 via `agents_bridge/` mostrou que:

1. Campos críticos (`execution_hints.entry_rule`, `exit_rule`, `regime_gate`) são strings livres em português — um runtime lê e **pode** interpretar errado (fez isso, 4 vezes).
2. ADR-0030 acabou de definir `runtime_contract` e `runtime_invariants` como novos campos obrigatórios — se não houver schema formal, cada emissão futura reinterpreta esses campos também.
3. O BotBinance pediu explicitamente (mensagem [2026-04-18 18:10 UTC] na bridge): "expressar o contrato do engine em JSON-schema pra evitar esse tipo de ambiguidade".
4. Manifests v1 e v2 coexistirão com v3+ por auditoria (imutáveis). Leitor precisa distinguir por `manifest_version`.

Validação automática é pré-requisito para escalar o protocolo de handoff sem depender de inspeção manual da bridge a cada manifest.

## Decision

Emitir `exports/approved/manifest.schema.json` (JSON Schema Draft 2020-12) como **schema canônico dos manifests v3+**. Todo manifest novo deve validar contra ele antes de export; export que falha validação é rejeitado pelo CLI.

Manifests v1 e v2 ficam **fora do escopo** do schema (preservados imutáveis, leitura best-effort). `manifest_version` no payload seleciona o validator: ausente ou `"v1"`/`"v2"` → legacy (sem validação estrita); `"v3"` ou superior → schema obrigatório.

### Estrutura do schema (v3)

Campos obrigatórios:

- `manifest_version: "v3"` (literal; v3.1, v3.2 futuros via minor bump no schema sem ADR nova se aditivo)
- `strategy_name: string`
- `alpha_forge_commit: string` (40-char hex)
- `approved_at: string` (ISO 8601 UTC)
- `approval_adr: string` (path relativo começando com `decisions/`)
- `engine: object` (family + params, estrutura livre dependente de family)
- `approved_combos: array` de `{symbol, timeframe, validation_window, window_tag, oos_trades, oos_sharpe, oos_mdd_pct, oos_pnl_pct}` — todos obrigatórios, sem valores default
- `validation: object` com `method, cost_model_baseline_pct, cost_model_stress_fee_plus_10_pct, cost_stress_ratio_min, seed_monte_carlo`
- `execution_hints: object` com os 7 campos atuais (inalterados)
- `runtime_contract: "faithful"` (ADR-0030; outros valores não permitidos em v3; novos contratos exigem bump de schema)
- `runtime_invariants: object` com 5 chaves literais fixas (ADR-0030)
- `expansion_policy: object` com `rule, excluded_combos`

Campos opcionais em v3:
- `supersedes: string` (manifest anterior)
- `prior_approval_adr: string`
- `disallow_sizing_modes: array` (strings de `["snowball", "kelly_like", "martingale"]`)

Propriedades adicionais: `false` no topo (strict). Em `engine.params`: `true` (family-specific).

### Enforcement

- `src/alpha_forge/exports/schema.py` — carrega o JSON Schema e expõe `validate_manifest(payload: dict) -> None` (raise em falha).
- CLI `alpha-forge export-manifest` (hoje manual) passa a chamar `validate_manifest` antes de gravar. Em ausência dessa CLI, validação manual via `python -m alpha_forge.exports.validate <path>` — uso obrigatório antes do PR do manifest.
- Property-based test: `tests/exports/test_manifest_schema.py` — manifests v3 gerados por `hypothesis.strategies` devem validar; mutações negativas (campo missing, tipo errado) devem rejeitar.

### V1 e V2 legados

`manifest.schema.json` **não** valida `20260418.json` (v1) nem `20260418_v2.json` (v2). Ambos permanecem como emitidos. Se alguém precisar ler e validar um v2, escreve `validate_legacy_v2` separado. O objetivo é que v3+ seja o caminho canônico daqui pra frente, não re-auditar o passado.

## Consequences

- **Positive:** emissão de manifests vira mecânica: CLI valida, falhou → corrige. Agente que escreve manifest não precisa decorar schema — leitor do schema pega typos, campo faltando, tipo errado, invariant fora de lista canônica. Bridge entre AF e runtimes (bot ou humanos) vira sobre conteúdo semântico, não sobre forma. Validação automática permite que séries futuras sejam muitas (BK+) sem cada uma virar um handoff de consistência estrutural.
- **Negative:** v3+ fica estritamente mais fechado que v2 (campos novos obrigatórios). Qualquer piloto novo que precise de flexibilidade (ex: runtime_contract diferente de `faithful`) requer bump de schema (v4) e ADR acompanhando. Pagamos essa rigidez em troca de evitar outra rodada de 5 mensagens na bridge pra descobrir 4 reinterpretações.
- **Neutral:** manifests v1 e v2 continuam válidos até que alguém os remova. Não há migração automática; v1/v2 viverão para sempre como evidência de estado quando foram emitidos. Aplicações (BotBinance) podem consumir os 3 formatos em paralelo via branch no `manifest_version`.

### Fica explicitamente fora desta ADR

1. **Schema para pilotos agentic** (SPEC/IMPLEMENTATION/VALIDATION/BACKTEST/AUDIT/CHECKLIST) — ADR-0020 cobre, separado.
2. **Migração automática v2 → v3** — não vale o esforço; manifests antigos são históricos.
3. **Outros `runtime_contract` além de `faithful`** — ADR futura se necessário.
4. **Validação cross-manifest** (ex: não permitir dois manifests ativos do mesmo `strategy_name` sem `supersedes` correto) — follow-up separado.
5. **Schema de `engine.params`** para cada família (bollinger, donchian, ma_crossover, etc.) — cada family define o seu opt-in; schema raiz aceita `engine.params` como `object` genérico.

## Alternatives considered

- **YAML schema / pydantic model como fonte de verdade** — rejeitado: JSON Schema é neutro à linguagem, o BotBinance pode consumir direto com qualquer lib. Pydantic no AF fica como implementação derivada, não fonte.
- **OpenAPI spec** — rejeitado: overkill; não há API HTTP, só arquivos JSON em repo.
- **Validação informal com checklist em CLAUDE.md** — rejeitado: é exatamente o que temos hoje e não pegou os 4 bugs do handoff de 2026-04-18.
- **Schema inferido do manifest v2 mais recente via `genson`** — rejeitado: congelaria bugs de tipo (ex: `oos_sharpe` optional quando deveria ser required) que o schema manual evita.
- **Incluir validação de v1/v2 no schema** — rejeitado: retrofit desnecessário, manifests históricos são imutáveis de qualquer jeito.

## Follow-ups

Concrete actions this decision creates. Each one belongs in `STATE.md` as pending work.

- Criar `exports/approved/manifest.schema.json` com o schema v3 completo.
- Implementar `src/alpha_forge/exports/schema.py` + testes em `tests/exports/`.
- Estender `AGENTS.md §8` referenciando o schema como fonte canônica.
- Próximo manifest (v3 de qualquer strategy) vai ser o primeiro a passar pelo validator.
- Publicar o schema na bridge (`conversa.md`) pro BotBinance poder validar no lado dele.
- **Explicitamente fora:** re-validação de v1/v2, schema para outras contracts além de `faithful`, schema para pilotos agentic.
