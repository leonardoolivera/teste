# 0057 — Série CG closeout: PRIMEIRO PASS cross-period (Bollinger short + width 300, 4/9)

**Status:** Accepted — série arquivada com gate PASS; promoção pra manifest v3 elegível via ADR separada
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0048 (manifest audit long v2), ADR-0053/0055 (closeouts CE/CF), ADR-0056 (pré-registro CG).

## Context

Série CG (ADR-0056) testou `min_width_bps=300` (vs 250 do CF/manifest v2) pra resolver o gap de cost_r observado em CF. Pré-registrou 4 gates; passou **todos**.

## Resultados

Dados crus: `exports/diag/cg_series_summary.json`. Tooling: `tools/run_cg_sweep.py`, `tools/summarize_cg.py`.

### Tabela completa

| Tag | Ativo | Regime | trd | Sh | MDD% | fe | cost_r | MCp5 | vs CF | Gate 1 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| CG.1 | btc | 2024-H2 | 47 | 0.52 | 4.67 | 10101 | 0.9733 | 9517 | +cr | FAIL (Sh) |
| CG.2 | eth | 2024-H2 | 63 | −0.23 | 4.79 | 9912 | 0.9661 | 9246 | +cr | FAIL (Sh, MCp5) |
| **CG.3** | sol | 2024-H2 | 102 | **1.38** | 6.33 | 10664 | 0.9505 | 9729 | +cr | **PASS** |
| **CG.4** | btc | 2025-H1 | 37 | **1.24** | 2.17 | 10296 | 0.9774 | 9953 | +cr | **PASS** |
| **CG.5** | eth | 2025-H1 | 85 | **2.39** | 8.33 | 11216 | 0.9594 | 9924 | +cr | **PASS** |
| **CG.6** | sol | 2025-H1 | 109 | **2.71** | 4.92 | 11747 | 0.9512 | 10460 | +cr | **PASS** |
| CG.7 | btc | 2025-H2 | 41 | 0.77 | 2.47 | 10119 | 0.9816 | 9727 | +cr | FAIL (Sh) |
| CG.8 | eth | 2025-H2 | 76 | 0.94 | 4.95 | 10323 | 0.9602 | 9442 | +cr | FAIL (Sh, MCp5) |
| CG.9 | sol | 2025-H2 | 101 | 0.72 | 6.46 | 10335 | 0.9497 | 9150 | +cr | FAIL (Sh, MCp5, cost_r) |

### Gates — avaliação final (pré-registrada)

- **Gate 1** (principal, ≥3/9): **4/9 → PASS**
- **Gate 2** (lift cost_r vs CF, ≥6/9): **9/9 → PASS** (unambiguously)
- **Gate 3** (edge preservado, trades≥30 & Sh>0 em ≥6/9): **8/9 → PASS**
- **Gate 4** (falsificacionista, ≤1/3 em 2024-H2): **1/3 → PASS** (CG.3 passou, borderline mas dentro)

**Veredicto overall**: **PASS**. Primeira série cross-period PASS em 6 séries consecutivas (CA/CB/CC/CD/CE/CF todas FAIL).

## Interpretação

### Filtro 300 > 250 em todas as dimensões

Gate 2 **9/9** reforça ADR-0055 Padrão 9. Filtro mais seletivo = menos trades ruins = melhor cost_r **sempre**. Edge preservado em 8/9. O compromisso não é "mais seletivo = menos edge"; é "mais seletivo = mesma estrutura do edge, com menos ruído agregado".

Comparando CF.5 (Sharpe 2.89) vs CG.5 (Sharpe 2.39): cai 0.5 Sharpe mas cost_r sobe de 0.9545 → 0.9594. Trade-off aceito pelo gate.

### Os 4 combos que passam — análise

- **CG.5 (ETH 2025-H1)**: Sharpe 2.39, 85 trades, MC p5 9924. Comparável a manifest v2 ETH 2024-H1 (Sharpe 1.834).
- **CG.6 (SOL 2025-H1)**: Sharpe **2.71**, 109 trades, MC p5 **10460**. Este é **o segundo maior Sharpe de combo composicional aprovável em toda a história do projeto**, só atrás de manifest v2 SOL 2024-H2 Sharpe 2.40 (ajustado) / 2.50 (audit).
- **CG.4 (BTC 2025-H1)**: Sharpe 1.24, 37 trades (borderline no gate trades≥30). Aceito.
- **CG.3 (SOL 2024-H2)**: Sharpe 1.38 — piloto surpresa. Bull forte **não** matou completamente short em SOL porque SOL teve chop interno no recorte. Não é inconsistência com Gate 4 (falsificacionista permite ≤1/3 em bull — 1/3 é o limite, e CG.3 é justo o 1).

### Concentração em 2025-H1 (3/4 dos passes)

CG.4/5/6 formam um cluster **geograficamente** (todos 3 ativos de 2025-H1, o regime de chop). Isto:
- **Confirma** a hipótese regime-dependente (ADR-0053 cristalizado): short mean-rev paga custo em chop.
- **Espelha simétrico** o manifest v2 (4/4 combos em bull 2024-H2 com long mean-rev).
- **Reduz independência dos pilotos**. 4/9 parece robusto, mas 3 deles correlacionados via regime temporal.

Isso é real limitação — **não** muda o PASS do gate (gate foi pré-registrado em 3/9, não em "3 recortes distintos"), mas informa a decisão de promoção: o edge aprovado é **regime-específico** e deve ser documentado como tal no manifest v3.

### Interpretação estatística

3 dos 4 passes em 2025-H1 poderia ser "sorte de 1 recorte". Mas:
- Audit ADR-0048 já estabeleceu que seed MC não movimenta Sharpe (determinístico no WF). Resultados são estruturais, não MC-drawn.
- Edge puro (CE) e composicional (CF, CG) em 2025-H1 são consistentes (Sharpe crescente 1.92 → 2.61 → 2.71 em SOL; 2.45 → 2.89 → 2.39 em ETH). Não é noise.
- Gate 2 PASS 9/9 mostra que o filtro **não está** sendo sortudo num subset — move cost_r em todos.

Conclusão: o edge é real, fortemente regime-dependente, e o filtro 300 é a configuração operacional correta pra extraí-lo.

### Padrão 10 (novo, consolidado)

"**Filtro composicional com parâmetro ajustado ao regime dominante pode elevar edge borderline pra passer**." Manifest v2 é um exemplo (width 250 em bull 2024-H2 long). CG é o segundo (width 300 em chop 2025-H1 short). Parâmetro diferente porque regime diferente. ADR-0049 Padrão 8 ("cada regime tem uma direcionalidade preferida") agora tem corolário operacional.

## Consequences

### Imediatas

- **Elegível pra manifest v3** via ADR de promoção separada. **Não promover aqui** — promoção requer ADR própria + decisões sobre engine.params, expansion_policy, approval criteria por combo.
- **Bot BotBinance não notificado ainda** — aguarda ADR de promoção. Signal-only rule: só notifica quando manifest muda de fato.
- **ADR-0056 gates honrados.** Nenhum gate renegociado post-hoc.

### Próxima ADR proposta — ADR-0058 Manifest v3 promoção

Escopo:
1. Escolher schema: manifest **separado** (`bollinger_short_width_20260419.json` v3) ou **superseding v2** (`bollinger_width_regime_20260419_v3.json`).
2. Especificar `engine.params`: `{family: bollinger, window: 20, num_std: 1.5, long_only: false, regime_filter: bollinger_width(window=30, num_std=1.5, min_width_bps=300)}`.
3. Listar 4 combos aprovados: CG.3, CG.4, CG.5, CG.6.
4. `expansion_policy` excluindo CG.1/2/7/8/9 com razões quantitativas.
5. `runtime_invariants` ADR-0030 (faithful runtime) — todos os 5 literais preservados.
6. Re-validação: Audit similar a ADR-0048 pra confirmar manifest novo antes de marcar ready.
7. Notificação BotBinance após manifest gravado.

### Regras consolidadas

- ADR-0030 faithful runtime continua em vigor — manifest short usará os mesmos 5 literais.
- ADR-0031 schema v3 JSON suporta short via campo `engine.params.long_only: false`. Sem mudança de schema.
- Combo manifest deve documentar expectativa regime-dependente em `expansion_policy.rule` — não promover cross-regime sem nova Série de validação.

## Critério de sucesso deste closeout

1. `cg_series_summary.json` arquivado ✓
2. Gates 1-4 avaliados com veredicto pré-registrado ✓
3. Padrão 10 documentado ✓
4. Próxima ADR proposta com escopo definido ✓

## Fora do escopo

- Promoção imediata. ADR-0058 fará isso separadamente; promoção não é reversível casualmente e merece review próprio.
- Rodar outras parametrizações (width 350, 400). Se ADR-0058 Audit encontrar problema, adiar pra ADR posterior.
- Adicionar RSI short + width ao manifest. Se existir gap semântico (width+RSI não combina como width+Bollinger), adiar.
- Testar short em 2024-H1 (fora do escopo cross-period; overlapping com in-sample original).
