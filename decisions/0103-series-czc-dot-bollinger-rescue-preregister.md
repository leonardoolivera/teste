# 0103 — Série CZC pré-registro: DOT Bollinger rescue (seed stability + MC robusto)

**Status:** Accepted — pré-registro
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0102 (CZB closeout), Padrão 23, seed stability padrão v4b

## Hipótese

CZB.1 revelou DOT Bollinger naked Sh=1.33 — quase PASS com seed=42 (falha só em MC p5 9295 e cost_r 0.942). Dois caminhos para confirmar edge:

1. **Seed stability (2 seeds adicionais)**: se Sh ≥ 1.0 em ≥ 2/3 seeds, edge replicável independente de aleatoriedade de fold/MC.
2. **MC robusto (2000 resamples)**: se com mais amostras MC p5 sobe ≥ 9500, sinal de que p5 9295 original é ruído de bootstrap com 1000 samples.

Padrão: v4b teve seed stability PASS 3/3 em {42, 1337, 2024} como critério canônico. Aplicar mesmo protocolo.

### Escopo reduzido vs pré-plano
ADR-0102 lista 3 probes (seeds + MC + inverse filter). Inverse filter (width < threshold) **não existe na tooling atual** (`BollingerWidthFilter` só suporta `min_width_bps`). Remove probe 3 sem perda — seeds e MC são testes de robustez mais fundamentais.

## Design (3 runs)

### Probe 1 — Seed stability
| Tag | Seed | Config |
|---|---|---|
| CZC.1 | 1337 | Bollinger(20/1.5) short naked, MC 1000 |
| CZC.2 | 2024 | idem |

### Probe 2 — MC robusto
| Tag | Seed | Config |
|---|---|---|
| CZC.3 | 42 | Bollinger(20/1.5) short naked, **MC 2000** |

Total: 3 runs (~8min).

Runtime faithful ADR-0030 em todos.

## Gates pré-registrados

### Gate 1 — Replicação seed
PASS se Sh ≥ 1.0 em ≥ 2/3 seeds (incluindo CZB.1 seed=42 Sh=1.33). Protocolo v4b.

### Gate 2 — MC robusto
PASS se CZC.3 (2000 resamples) tem p5 ≥ 9500. Se p5 sobe significativamente (> 9400), indica variância do bootstrap; se permanece ~9300, edge tem lower-tail legítimo fino.

### Gate 3 — Promoção v9 candidato
Se Gate 1 PASS (seed stability) **e** Gate 2 PASS (MC robusto): promove DOT Bollinger naked 2025-H2 para novo manifest v9.

Se Gate 1 PASS mas Gate 2 FAIL (MC p5 ainda < 9500): **PASS contextual** — documenta que edge existe mas tail risk é notável. Decisão manual de promoção; default = não promove, mantém em backlog para validação adicional.

Se Gate 1 FAIL (seed instabilidade): seed 42 foi fluke. Não promove, encerra DOT.

### Gate 4 — cost_r
CZB.1 cost_r=0.9421 (< 0.95). Se nos seeds novos cost_r permanece < 0.95, custo de execução stress-test reprova mesmo com edge confirmado. Documenta.

## Riscos antecipados

1. **Variância de seed**: DOT naked pode ter Sh variável dado trade count alto (127) e baixa liquidez altcoin. Se Sh cai para < 1.0 em outros seeds, Padrão 22 atualizado.
2. **MC 2000 não muda nada**: p5 estabiliza próximo ao original. Edge tail real fino.
3. **Custo alto altcoin**: cost_r 0.94 pode ser estrutural (liquidez DOT menor que BTC). Se sim, o edge existe mas é fragil a custo.

## Interpretação

| Gate 1 | Gate 2 | Gate 4 | Ação |
|---|---|---|---|
| PASS | PASS | ≥ 0.95 | Promove v9 (novo manifest DOT Bollinger 2025-H2) |
| PASS | PASS | < 0.95 | PASS contextual, documenta fragilidade a custo, decide manual |
| PASS | FAIL | — | PASS contextual seed-only, tail fino, não promove default |
| FAIL | — | — | seed 42 fluke, encerra DOT |
| 1/3 | — | — | sinal instável, documenta e deixa em backlog |

## Critério de sucesso desta ADR

1. 3 runs executados
2. ADR-0104 closeout documenta verdict
3. Decisão de promoção baseada em gates
4. STATE.md atualizado
