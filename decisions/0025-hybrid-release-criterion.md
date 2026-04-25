# 0025 — Critério de release híbrido (absoluto + relativo pós-Série H)

**Status:** Accepted
**Date:** 2026-04-18
**Accepted:** 2026-04-18
**Deciders:** Usuário (owner do projeto) + agente.

## Context

A Série H encerrou com **12 pilotos agentic** (H.1 a H.10 + H.5b + variantes H.2a/b/c) todos classificados `release_decision: fail` em seus `AUDIT.md`. Em 100% dos casos o motivo foi o **critério 1 absoluto** — `hit_rate ≥ 45%` — que nenhum piloto cruzou. Os 12 pilotos convergiram empiricamente em faixa **25–32%**; o melhor é H.9 (ETH+SMA) com 32.29%, 12.71pp abaixo do piso.

Isso evidencia duas coisas: (a) o piso de 45% não é **inatingível em princípio** — é possível que famílias de estratégia diferentes (mean-reversion, intraday, outros ativos) o cruzem — mas é **operacionalmente inviável como único gate** para sair de `fail`, porque trava toda evolução do laboratório; e (b) ADR-0024 (ranking composto) entregou dispersão real entre os 12 (score de 1.98 até 7.65), permitindo **ordenação relativa com sinal**, não só absoluta.

Sem revisão, o laboratório fica em deadlock: ranking ordena pilotos, mas todos ficam `fail` → north star ("testar centenas 1 por 1 e ranqueando") produz 0 promoções. Precisa-se de um critério que preserve a **barra de segurança de `canary_only`** (onde há exposição de capital real, mesmo que hipotética futura) e que abra um **canal operacional para `paper_only`** baseado em performance relativa validada — sem jamais abrir `live` (ADR-0005 doutrina) e sem reescrever auditorias existentes.

## Decision

Adotar critério de release **híbrido**, com dois canais distintos e critério **append-only** na re-auditoria:

1. **`canary_only`** (inalterado) — **hard gate absoluto**: `hit_rate ≥ 45%` no baseline segue como piso obrigatório. Nenhum piloto que não cruzar este piso pode ser promovido a `canary_only`, independentemente do ranking. Mantém-se a barra que o protocolo original estabeleceu para exposição de capital.
2. **`paper_only`** (novo canal) — **gate relativo via ranking**: pilotos no **top-3 por `composite_score`** (ADR-0024) em um sample com **N ≥ 9 pilotos válidos** recebem `paper_only`. Sample menor que 9 continua sem canal relativo (sinal ranking é ruído em N pequeno). Tiebreaks seguem `slug` alfabético (ADR-0024).
3. **Resto** — `fail`.

**Re-auditoria é append**: cada `AUDIT.md` existente recebe uma **nova seção** `## Re-auditoria 2026-04-18 (ADR-0025)` no fim do arquivo, com a decisão revisada sob o critério híbrido. A seção `## release_decision` original permanece intacta como histórico — não se reescreve passado.

`live` **segue proibido** (ADR-0005, hook de validação). Esta ADR não altera isso.

### Aplicação imediata aos 12 pilotos da Série H

Com `N = 12 ≥ 9`, top-3 por `composite_score` conforme leaderboard atual (DEFAULT_WEIGHTS de ADR-0024):

| Rank | Slug                                             | composite_score | hit_baseline | release revisado |
|------|--------------------------------------------------|-----------------|--------------|------------------|
| 1    | donchian-20-10-eth-180d-regime-sma (H.9)         | 7.65            | 32.29%       | `paper_only`     |
| 2    | donchian-20-10-btc-180d-regime-sma-or-atr (H.7)  | 6.87            | ~29%         | `paper_only`     |
| 3    | ma-crossover-20-50-btc-180d-baseline (H.2b)      | 6.44            | ~27%         | `paper_only`     |
| 4–12 | demais                                           | 1.98–5.31       | 25–30%       | `fail`           |

Nenhum piloto cruza 45% → **zero `canary_only`** (canal preservado, vazio até aparecer edge absoluto).

## Consequences

- **Positive:** laboratório sai do deadlock — há um canal operacional (`paper_only`) que não depende de piloto nenhum atingir 45%; ranking (ADR-0024) passa a ter efeito operacional, não só diagnóstico; `canary_only` preserva doutrina de segurança absoluta. Re-auditoria append mantém histórico intacto e auditável (possível reconstruir a decisão original a qualquer momento).
- **Negative:** introduz componente relativo (top-K) no gate de promoção → top-3 de um sample ruim ainda é promovido, mesmo sem edge real. Mitigação parcial: `paper_only` não expõe capital (ADR-0005) — promoção é primariamente para priorizar atenção/desenvolvimento, não risco financeiro. Threshold `N ≥ 9` é empírico (derivado do fato de a Série H ter 12): não há fundamentação estatística formal. Risco de "gaming" dos pesos de ranking: quem escolher `ScoreWeights` controla quem promove; mitigado pela rastreabilidade (pesos são persistidos em cada leaderboard e auditáveis).
- **Neutral:** `paper_only` continua bloqueado por **ausência de módulo `paper-trade`** (mesma situação de 2026-04 documentada no template AUDIT.md) — a decisão de release é formal; execução efetiva de paper depende de infraestrutura futura. Ranking em si não muda (ADR-0024 intacto); apenas a interpretação dos scores muda. `flags_digest` (ADR-0024) continua sendo a identidade invariante do piloto — re-auditoria não altera digest.

## Alternatives considered

- **Pure relative (top-K sem safety floor)** — rejeitado porque remover hard gate de 45% para `canary_only` abriria exposição de capital por ranking relativo em sample potencialmente ruim. Barra absoluta para capital é inegociável.
- **Revisar 45% para ~32% (teto empírico Série H)** — rejeitado porque 32% é **teto observado em faixa sem edge** (12 pilotos fail), não patamar de edge real; rebaixar o critério normalizaria "não tem edge" como sucesso. 45% foi escolhido como patamar de edge, não de média de mercado.
- **Reset/reescrita dos 12 AUDIT.md existentes** — rejeitado: perda de histórico é irreversível; auditoria precisa ser reconstruível. Append preserva trilha.
- **Top-K fixo em K=1** — rejeitado por ser frágil: 1 único outlier promovido não exercita a infraestrutura comparativa. K=3 com N≥9 dá margem de corroboração (razão 1:3).
- **Z-score threshold em vez de top-K** — rejeitado: score composto é linear ponderado com min-max (ADR-0024), não distribuição estatística; z-score sobre min-max é operação sem significado. Top-K é nativo ao contrato ADR-0024.
- **Score absoluto mínimo (e.g., composite_score ≥ 5.0)** — rejeitado: score depende dos pesos e do sample (min-max é relativo ao sample). Threshold absoluto sobre quantidade relativa é inconsistente.

## Follow-ups

Cada um belongs em `STATE.md` como pending work até ser fechado.

- Atualizar `agentic/templates/AUDIT.md` — seção `## Release decision` deve descrever critério híbrido (ADR-0025) e referenciar ADR-0024 para `paper_only`.
- Executar re-auditoria append nos 12 `agentic/active/*/AUDIT.md` — nova seção `## Re-auditoria 2026-04-18 (ADR-0025)` com decisão revisada + justificativa (ranking position + score). Esperado: 3 `paper_only`, 9 `fail`, 0 `canary_only`.
- Atualizar `vision/01-product.md` — seção "Definition of success" (linhas 60–87): a métrica `≥ 1 estratégia sobrevivendo em ≥ 2 regimes` ganha sub-critério; agora existe canal `paper_only` relativo, mas "sobreviver" requer interpretação sob ADR-0025.
- Atualizar `system/flows.md` — acrescentar referência a ADR-0025 no fluxo de auditoria de pilotos.
- Atualizar `STATE.md` — `What was last delivered` + `Next step` refletindo re-auditoria concluída.
- Próxima série (I) abrir pilotos já sob ADR-0025 desde o início; `AUDIT.md` novos não precisam de seção append.
