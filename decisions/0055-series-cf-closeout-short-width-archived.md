# 0055 — Série CF closeout: Bollinger short + width, filtro load-bearing mas gate FAIL 2/9

**Status:** Accepted — série arquivada; promoção bloqueada; evidência direcional preservada
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0048 (manifest audit long), ADR-0053 (closeout CE), ADR-0054 (pré-registro CF).

## Context

Série CF (ADR-0054) testou a hipótese simétrica de ADR-0048 Audit B: se `BollingerWidthFilter` é load-bearing pra Bollinger long em bull-com-chop, deveria ser pra Bollinger short em chop. 9 pilotos cross-period (BTC/ETH/SOL × 2024-H2/2025-H1/2025-H2).

## Resultados

Dados crus: `exports/diag/cf_series_summary.json`. Tooling: `tools/run_cf_sweep.py`, `tools/summarize_cf.py`.

### Tabela completa

| Tag | Ativo | Regime | trd | Sh | MDD% | fe | cost_r | MCp5 | vs CE | Gate 1 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| CF.1 | btc | 2024-H2 | 67 | 0.92 | 5.48 | 10224 | 0.9645 | 9553 | +cr | FAIL (Sh) |
| CF.2 | eth | 2024-H2 | 86 | −0.10 | 6.00 | 9943 | 0.9554 | 9011 | +cr | FAIL (Sh, MCp5) |
| CF.3 | sol | 2024-H2 | 110 | 1.24 | 8.34 | 10644 | 0.9466 | 9706 | +cr | FAIL (cost_r) |
| CF.4 | btc | 2025-H1 | 57 | **1.25** | 2.28 | 10318 | 0.9693 | 9883 | +cr | **PASS** |
| CF.5 | eth | 2025-H1 | 98 | **2.89** | 7.20 | 11566 | 0.9545 | 10097 | +cr | **PASS** |
| CF.6 | sol | 2025-H1 | 119 | 2.61 | 4.76 | 11749 | 0.9461 | 10371 | +cr | FAIL (cost_r) |
| CF.7 | btc | 2025-H2 | 50 | 0.95 | 2.77 | 10175 | 0.9773 | 9712 | +cr | FAIL (Sh) |
| CF.8 | eth | 2025-H2 | 79 | 0.38 | 5.68 | 10131 | 0.9547 | 9262 | +cr | FAIL (Sh, MCp5) |
| CF.9 | sol | 2025-H2 | 111 | 1.08 | 8.44 | 10556 | 0.9455 | 9179 | +cr | FAIL (MCp5, cost_r) |

### Gates — avaliação pré-registrada

- **Gate 1** (≥3/9 passam critério manifest): **2/9 → FAIL**
- **Gate 2** (lift cost_r vs CE em ≥6/9): **9/9 → PASS** (filtro é unambiguously load-bearing)
- **Gate 3** (falsificacionista, ≤1/3 em 2024-H2): **0/3 → PASS** (coerência)

**Veredicto overall** (Gate 1 + Gate 3): **FAIL**. Série arquivada. Manifest sem alteração.

## Interpretação

### Filtro é load-bearing, mas ainda insuficiente

Gate 2 PASS **9/9** é resultado contundente: `BollingerWidthFilter` **sempre** melhora cost_r em Bollinger short, sem exceção. Isso confirma a hipótese simétrica de ADR-0048: o filtro discrimina produtivamente regimes de baixa width (squeeze → falso-sinal) tanto pro long quanto pro short.

MAS o edge composicional short não é forte o suficiente pra atingir **todos** os 5 gates simultaneamente em 3/9 pilotos. Breakdown das falhas:

- **Falhas por Sharpe < 1.0** (4 pilotos): CF.1, CF.7 (borderline, Sharpe 0.92 e 0.95), CF.2, CF.8 (Sharpe claramente baixo)
- **Falhas por cost_r < 0.95** (3 pilotos): CF.3, CF.6, CF.9 — todos com Sharpe ≥ 1.08 e fe > 10k, mas cost_r em 0.945-0.947, **bloqueados por 3-5 pp**
- **Falhas por MC p5 ≤ 9500** (3 pilotos): CF.2, CF.8, CF.9

### CF.5 e CF.6 são o drama

- CF.5 (ETH 2025-H1): Sharpe **2.89**, fe 11566, MDD 7.20, cost_r 0.9545, MC p5 10097. **PASS.**
- CF.6 (SOL 2025-H1): Sharpe **2.61**, fe 11749, MDD 4.76, cost_r 0.9461, MC p5 10371. **FAIL por cost_r de 1pp.**

Estatisticamente, CF.6 é o piloto de **maior fe e maior MC p5** da série, e falha por 1 ponto percentual no stress. O edge empírico é real; o gate é cruel no corte. Isso é *exatamente* o padrão do audit ADR-0048: manifest v2 v1.62 Sharpe puro → 2.50 com filtro (pass). Aqui, short puro CE.6 Sharpe 1.92 → CF.6 Sharpe 2.61 com filtro (+0.69). Filtro **funciona**, mas partindo de edge puro menor.

### Pattern cristalizado (Padrão 9, novo)

Combinando ADR-0048 + ADR-0053 + ADR-0055:

| Direção | Edge puro (sem filtro) Sharpe típico | Edge composicional (+ width) Sharpe típico | Passa Gate? |
|---|---:|---:|---|
| Long em 2024-H2 (bull) | 1.62 | 2.50 | SIM (manifest v2) |
| Short em 2025-H1 (chop) | 1.92-2.45 | 2.61-2.89 | BORDERLINE (2/3 do regime) |
| Short em 2024-H2 (bull) | −0.87 a 0.80 | −0.10 a 1.24 | NÃO (Gate 3 PASS correto) |
| Long em 2025-H1 (chop) | não testado nesta série | não testado | desconhecido |

**Padrão 9**: "**filtro composicional move o vidro ~1.0 Sharpe; se edge puro é < 1.5 Sharpe, não chega a gate-passer mesmo assim**". ADR-0048 Audit B mostrou delta +0.89 Sharpe. ADR-0055 mostra delta +0.44 a +0.69 para short em chop. Vidro move, mas edge puro precisa começar em ≥ 1.5-2.0 Sharpe pra emergir como approved combo.

### Por que CF.5 PASS e CF.6 FAIL com edge similar?

CF.5 tem cost_r 0.9545 (passa); CF.6 tem 0.9461 (falha por 1pp). Mesmo gate, resultados diferentes. Razão: SOL tem trades mais (119 vs 98) e maiores (fe maior), então turnover aumenta sensibilidade a fees. Gate é calibrado pra ser conservador exatamente nesse caso — SOL é mais volátil → mais trades → custo de fees aumenta mais rápido com stress. Coerente.

### H1 vs H2 de ADR-0049 — agora com mais evidência

ADR-0053 reforçou H2 (regime domina). ADR-0055 **refina**: H2 não é "edge não existe"; é "edge existe mas é frágil sozinho". Com filtro composicional especializado, 2025-H1 short fica borderline-passer. Esta é evidência **entre** H1 e H2: ajusta a posição de "regime absolutamente domina" pra "regime + composição específica podem passar, mas rarificado".

## Consequences

### Imediatas

- **Manifest v2 preservado.** CF não gera combos promovíveis.
- **Bot BotBinance não notificado.**
- **ADR-0054 pré-registro honrado.** Gate não renegociado.

### Direções priorizadas (próxima ADR)

1. **Prioridade 1 — ADR-0050 §D3 (volatility-adjusted sizing)**. Agora tem **evidência** de que cost é o fator bloqueante em 3-4 pilotos promissores (CF.3, CF.6, CF.9 em particular, todos com Sharpe ≥ 1.08 mas cost_r em 0.94). Reduzir fração em alto overbought poderia estabilizar. Payoff esperado concreto: mover CF.6 de 0.9461 pra > 0.95 provavelmente promove o piloto inteiro.

2. **Prioridade 2 — Série CG com parâmetros alternativos**. Testar Bollinger short + width com `min_width_bps=300` (filtro mais seletivo, menos trades → menos custo agregado). Risco: pode matar edge ao mesmo tempo. Se Série CG passar onde CF falhou, ganhamos manifest v3 combo short.

3. **Prioridade 3 (backlog) — §D5 ensemble regime-gated**. Mais complexo de implementar; espera evidência que §D3 é insuficiente.

4. **Prioridade 4 (descartada implicitamente)** — Série com `trend_htf:mode=short_only` como filtro adicional em short. CD mostrou que trend_htf em trend-following é risk modulator não edge gen; seria pior em mean-rev.

**Escolhido como próximo passo** — pausa pra decisão do usuário. Tanto §D3 quanto Série CG são legítimos; diferem em escopo e incerteza:

- **Série CG**: baixo custo (~20min compute, 2 ADRs), alta incerteza de passar (modifica 1 parâmetro, edge pode desaparecer)
- **§D3 sizing adjustment**: médio custo (requer novo módulo de sizing, ADR-específica, pelo menos 3 ADRs), incerteza moderada (ataca o gap específico identificado — cost_r)

### Regras consolidadas

- **Cost stress é a fronteira real** (reforçado desde ADR-0053).
- **Filtros composicionais melhoram mas não transformam edge** (Padrão 9 novo).
- **2025-H1 chop é o único regime onde short paga custo** (3 dos 4 pilotos de maior Sharpe da CF estão aqui: CF.5, CF.6; CF.4 tem Sharpe menor mas passa).

## Critério de sucesso deste closeout

1. `cf_series_summary.json` arquivado ✓
2. Gates 1-3 avaliados com veredicto pré-registrado ✓
3. Padrão 9 documentado ✓
4. 2 direções priorizadas pra próxima ADR, com custo estimado ✓

## Fora do escopo

- Promover CF.4 e CF.5 individualmente (2/9 < gate). Alinhado com ADR-0049 §Padrão 5 (anti-cherry-pick).
- Grid-search em `min_width_bps` (200, 300, 400). Só vira relevante depois de decidir direção §D3 vs CG.
- Re-interpretar cost stress gate. ADR-0014 fixou `cost_r ≥ 0.95`; não é negociável sem ADR própria.
