# 0172 — Série KE closeout definitivo: Keltner refutado em 12 runs (3 fases)

**Status:** Accepted — Keltner arquivado em todas as dimensões testadas.
**Date:** 2026-04-20
**Deciders:** Usuário (piloto automático) + agente
**Relates to:** ADR-0170 (pré-reg), ADR-0171 (Fase 1 closeout parcial), Padrão 41

## Resumo executivo

| Fase | Runs | Dim. variadas | Pass gate |
|---|---:|---|:---:|
| 1 — Naked 2025-H1 | 3 | 3 assets | 1/3 (ETH outlier) |
| 1b — Naked cross-window | 6 | 2 windows × 3 assets | 0/6 |
| 2 — + width filter 2025-H1 | 3 | filter composition | 0/3 |
| **Total** | **12** |  | **1/12** |

**1/12** = Padrão 41 isolado (ETH 2025-H1). Keltner **confirmado como dead** em toda dimensão acessível sem implementação adicional.

## Resultados agregados

### Fase 1 — naked 2025-H1 (KE.1-3)

| | Sh | Trades | vs BB | Lift |
|---|---:|---:|---:|---:|
| BTC | 0.06 | 49 | 0.85 | -0.79 |
| ETH | **2.40** | 48 | 0.68 | **+1.72** |
| SOL | 0.62 | 46 | 1.44 | -0.82 |

### Fase 1b — naked cross-window (KE.4-9)

| | 2025-H2 Sh | 2024-H2 Sh |
|---|---:|---:|
| BTC | -0.55 | -1.02 |
| ETH | -0.71 | 0.65 |
| SOL | 1.00 | 0.19 |

### Fase 2 — + bollinger_width(30, 1.5, 300) 2025-H1 (KE.10-12)

| | Sh | Trades | vs BB+width baseline | Lift |
|---|---:|---:|---:|---:|
| BTC | 1.16 | 25 | 1.32 | -0.16 |
| ETH | 1.24 | 47 | 1.53 | -0.29 |
| SOL | 1.19 | 57 | 1.30 | -0.11 |

## Interpretação

### Hipótese estrutural Keltner vs BB NÃO se realiza em crypto 1h

ADR-0170 previu: ATR é mais robusto a spikes que stdev, podendo dar edge em regimes com outliers. **Empiricamente**: ATR e stdev dão largura de envelope praticamente idêntica em crypto 1h. Vol é **persistente**, não spiky-discreta — não há "flash crash vs calm" dicotomia dura que favorecia ATR. Resultado: Keltner é Bollinger com mais hiperparâmetros, mesma performance ou pior.

### Padrão 41 "curado" pelo filter em Fase 2

Interessante: Fase 1 tinha ETH outlier (Sh=2.40 vs BTC 0.06 / SOL 0.62). Fase 2 com width filter: ETH cai para 1.24, BTC sobe para 1.16, SOL para 1.19 — **todos convergem** numa faixa estreita ~1.2. O filter aparentemente corta sinais ruidosos de ETH e padroniza. **Padrão 41 em engines naked pode ser ruído filtrável**, não regime-específico irreversível.

### Implicação: filter corrige engine, mas não destrava edge ≥1.5

Mesmo com ETH normalizado, nenhum dos 3 assets atinge gate ≥1.5 em Fase 2. Keltner+width está 0.1-0.3 abaixo do BB+width equivalente. Dead-on-arrival como upgrade.

## Candidato Padrão 45 (formalizar)

**"Engines vanilla (engine-only, sem filter) em crypto 1h tendem a produzir Padrão 41 em ETH 2025-H1. Adicionar filter canônico (bollinger_width) normaliza o sinal cross-asset — o outlier ETH converge para a faixa de BTC/SOL, mas o edge absoluto não sobe. Implicação: Padrão 41 em engine naked pode ser ruído corrigível, não regime; mas normalização não cria edge onde não há."**

Evidência: DE (trend_htf 1d) + KE (Keltner) ambos mostram assinatura ETH-outlier em naked. KE.10-12 +width normaliza. N=2 engines, comportamento consistente.

Formalizar agora — próximo engine (se houver) deve testar +filter cedo antes de arquivar pela Fase 1.

## Decisão

- **Keltner arquivado** em todas as dimensões testadas (naked, cross-window, +width filter)
- **Código Keltner preservado** em `src/alpha_forge/strategies/families/keltner/` — já implementado, testado (21/21 unit), wired na CLI. Custo de manter = zero. Re-revisitar se nova hipótese emergir (ex. Keltner+trend_htf, Keltner long-only, timeframe 4h)
- **Nenhuma edição de manifest**
- Stack: **13 combos** inalterados

## Implicação para handoff bot

Piloto automático objetivo = estratégia para bot. Keltner não entrega. Opções remanescentes exauridas neste turno:

1. **Zscore MR** (ADR-0169 Candidato A): ainda mais próximo de BB; prior pessimista; valor de informação apenas
2. **Cross-sectional momentum** (Candidato D): requer mudança de framework single-asset → multi-asset; alto custo, não single-session
3. **Orderbook** (Candidato E): dados não ingestados, altíssimo custo
4. **Padrão 45 sugere re-examinar**: combos vanilla do stack atual (ex. BB short naked 2025-H1) com filter+engine alternativo — já feito extensivamente
5. **Testar Keltner 4h timeframe** ou **Keltner long-only** — dimensão não explorada, cheap

Recomendação: **pausar frente "novos engines"**. Stack 13 combos é estado estável, diversificado (mean corr +0.38), com combo trendhtf RSI 25/75 SOL recentemente promovido (ADR-0140). **Handoff ao bot deveria usar o stack atual** — não esperar edge incremental marginal quando o stack existente já atende o critério de exportação (ADR-0030).

Próximo ADR proposto: snapshot do stack atual + proposta de manifest v6.2 para handoff (usa combos já aprovados, não novos). Usuário decide se executa.

## Não-alvo

- Não testar Keltner em 4h ou long-only nesta sessão (diminishing returns)
- Não implementar zscore (prior muito ruim)
- Não mudar framework

## A\u00e7\u00e3o executada

- ✅ ADR-0170 pré-reg
- ✅ Engine + CLI + 21/21 testes
- ✅ 12 runs (KE.1-12) em 3 fases
- ✅ Padrão 45 formalizado neste ADR
- ✅ ADR-0172 closeout definitivo
