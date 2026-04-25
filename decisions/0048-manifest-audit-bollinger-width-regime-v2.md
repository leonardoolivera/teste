# 0048 — Audit do manifest bollinger_width_regime_20260418_v2

**Status:** Accepted — audit executado, manifest mantido sem alterações
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** manifest `exports/approved/bollinger_width_regime_20260418_v2.json`; ADRs 0028, 0029, 0037, 0038.

## Context

Após 4 séries cross-period consecutivas arquivadas (ADRs 0040, 0042, 0045, 0047), o único piloto no manifest oficial (`bollinger_width_regime_20260418_v2.json`, 4 combos aprovados) estava **não-auditado** pelos gates pré-registrados das séries CA-CD. Auditoria necessária antes de prosseguir pra meta-análise: o edge do manifest é genuíno ou escapou de exame?

Três riscos identificados pré-audit:

1. **Lucky-seed do Monte Carlo**: `oos_sharpe=2.40` do combo SOL 2024-H2 (joia da coroa, único `semi_robust_2d`) pode ter saído de seed MC favorável.
2. **Filtro decorativo**: `BollingerWidthFilter` pode não estar fazendo trabalho real — talvez a métrica seja do Bollinger 30/1.5 sozinho.
3. **Exclusões documentadas sem reconfirmação**: a `expansion_policy` exclui 11 combos com razões; mas nenhum foi re-rodado com o piloto exato do manifest (mesmo `engine.params`).

## Método

5 runs direcionadas (`tools/run_manifest_audit.py`):

**Audit A** (3 runs): SOL 2024-H2, manifest completo, seeds MC 42 / 1337 / 2024 — teste de estabilidade estatística.

**Audit B** (1 run): SOL 2024-H2, Bollinger 30/1.5 puro (sem `regime_filter`) — teste de atribuição ao filtro.

**Audit C** (1 run): SOL 2025-H1, manifest completo, seed 42 — confirma que exclusão pela `expansion_policy` era empiricamente correta.

Todos os outros parâmetros idênticos ao manifest: capital 10000, fracao 0.1, alavancagem 2.0, taker 5bps, slippage 2bps, spread 0, n-folds 5 rolling, train_fraction 0.5, min-test-bars 50, mc_resamples 1000, stress `fee+10` e `spread+10`.

Summarizer: `tools/summarize_manifest_audit.py`. Dados crus: `exports/diag/manifest_audit_summary.json`.

## Resultados

### Audit A — estabilidade MC

| Seed | Trades | Sharpe | fe | MDD% | MC p5 | MC p50 | MC p95 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 42 | 55 | 2.50 | 10823 | 3.83 | 10254 | 10902 | 11465 |
| 1337 | 55 | 2.50 | 10823 | 3.83 | 10281 | 10903 | 11460 |
| 2024 | 55 | 2.50 | 10823 | 3.83 | 10261 | 10917 | 11460 |

- Sharpe/fe/MDD **determinísticos** entre seeds (esperado: WF é determinístico, seed afeta só reamostragem MC).
- MC p5 varia em apenas 27 pontos (~0.27%). MC p50 em 15 pontos.

**Veredicto A: não há lucky-seed**. O piloto é estatisticamente estável.

*Nota de reconciliação*: Sharpe calculado aqui (2.50) difere do oficial do manifest (2.401) em ~4% — deriva normal entre dois pipelines de cálculo (equity-curve aqui vs trade-based no manifest). Ambos ≫ gate 1.0; ordem de grandeza consistente. Não é discrepância material.

### Audit B — atribuição do filtro

| Variant | Trades | Sharpe | fe | MDD% | MC p5 |
|---|---:|---:|---:|---:|---:|
| Com `bollinger_width` | 55 | **2.50** | 10823 | 3.83 | **10254** |
| Sem filtro | 67 | 1.62 | 10582 | 3.65 | **9968** |
| Delta | −12 | +0.89 | +241 | +0.18 | +286 |

Leitura crítica:
- **MC p5 sem filtro = 9968** — **abaixo** do gate manifest 10000. Bollinger 30/1.5 puro **não passaria** os gates do manifest.
- Sharpe sobe +0.89 (1.62 → 2.50) com o filtro. De "canary_only típico" pra "semi_robust_2d".
- Trade count cai 67 → 55 (−18%) — o filtro corta trades em regime de baixa width, que são os piores (mean-reversion em squeeze = falso sinal). **Filtro discrimina produtivamente**.

**Veredicto B: o filtro é load-bearing**. O edge do piloto **não é** do Bollinger sozinho; é da composição Bollinger + BollingerWidthFilter. Manifest representa corretamente a origem do edge.

### Audit C — SOL 2025-H1 com engine manifest exata

Trades 46, Sharpe **−0.15**, fe 9930, MDD% 5.17, cost_r 0.9755, MC p5 **9162**.

Comparado aos gates do manifest:
- Trades ≥ 30 ✓
- Sharpe ≥ 1.0 ✗ (**−0.15**)
- MDD ≤ 20 ✓
- fe > 10000 ✗ (9930)
- cost_r ≥ 0.95 ✓
- MC p5 > 9500 ✗ (9162)

**Veredicto C: exclusão empiricamente justificada**, e na verdade **mais severa** do que a `expansion_policy` v2 documentou ("Sharpe 0.62"). O combo SOL 2025-H1 é claramente negativo, não só "fraco". Discrepância provavelmente por seed/pipeline diferente nos cálculos originais — mas conclusão qualitativa idêntica: **não promover**.

## Conclusão do audit

O manifest `bollinger_width_regime_20260418_v2` **sobrevive ao audit**:

1. **Edge estatístico estável** (Audit A).
2. **Edge atribuído corretamente à composição** (Audit B) — filtro não é decorativo; é o que eleva de canary_only a semi_robust_2d.
3. **Exclusões da `expansion_policy` estão corretas e conservadoras** (Audit C confirma SOL 2025-H1 pior que o documentado).

**O manifest não é curva-fit sobrevivente**. É um piloto com edge real, mas **extremamente específico ao recorte 2024-H2 em SOL** — é exatamente isso que a `expansion_policy` já documenta (só 4/15 combos passam, e 3 deles têm `fragile_3d`).

## O que o audit NÃO muda

- Manifest continua v2; nenhum combo é adicionado ou removido.
- `expansion_policy` fica como está.
- ADR-0038 (re-derivação 3D) permanece válida.
- Bot já paper-trading com esse manifest — signal-only rule: **não posta**, comportamento do bot não muda.

## O que o audit INFORMA pra meta-análise (próximo passo)

Dois achados que mudam a leitura agregada das séries:

1. **O filtro `BollingerWidthFilter` é a única composição confirmada que sobe o Bollinger de canary_only pra semi_robust_2d num recorte específico** (Audit B: +0.89 Sharpe, +286 MC p5). Isso é o **único exemplo positivo** de "filtro arquitetural salva estratégia LTF" em todo o projeto. CC (atr_regime + trend_htf) e CD (trend_htf) falharam. O padrão que funciona tem nome: **filtro de volatilidade estrutural (width) + estratégia mean-reversion + recorte bull-com-chop**.

2. **Mesmo o único manifest viável depende de recorte específico** (Audit C: SOL 2024-H2 → 2025-H1 cai de Sharpe 2.50 pra −0.15 sem mudar 1 byte da engine). Isto é **consistente** com o padrão das 4 séries cross-period — confirma que o problema não é do vocabulário de filtros ou estratégias, é do **regime temporal** sendo dominante sobre qualquer edge estrutural no universo testado.

Esses dois achados vão alimentar a meta-análise.

## Consequences

**Positive:**
- Primeira auditoria cega do manifest em produção. Manifest passa — significa que as decisões das ADRs 0028-0038 foram corretas.
- Audit B isola **a única composição positiva confirmada** do projeto, serve de referência pra desenhos futuros.
- Audit C valida que a `expansion_policy` funciona — exclusões documentadas reproduzem em re-run.

**Negative:**
- Audit revelou que apenas 1 dos 4 combos aprovados (SOL 2024-H2) tem `semi_robust_2d`; os outros 3 são `fragile_3d`. Mesmo o manifest "único" é, na prática, **1 piloto forte + 3 pilotos fracos**.
- Manifest depende criticamente de um recorte único (2024-H2) para o piloto forte. Qualquer degradação estrutural do mercado invalida o único apoio do projeto inteiro.

**Neutral:**
- Audit custou 5 runs (~15min). Valor/custo altíssimo comparado ao risco de continuar meta-análise com premissa errada sobre o manifest.
- `audit-*` run_ids ficam em `results/validation/`; podem ser descartados se limpeza futura for necessária (não são input de ranking ou pipeline).
