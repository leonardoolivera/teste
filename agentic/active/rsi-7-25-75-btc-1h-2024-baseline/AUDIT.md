# AUDIT.md — O.1 RSI 7/25/75 BTC 1h 2024

release_decision: fail

## release_decision

**`fail`** — 32º piloto. **Segundo `fail` operacional do protocolo via
Critério 3 de ADR-0025**, primeiro por sensibilidade paramétrica (L.1/L.2/L.3
foi por timeframe).

| Gate                                    | Observado | Status |
| --------------------------------------- | --------: | ------ |
| Critério 1: hit_rate baseline ≥ 45%     |    59.86% |     OK |
| Critério 2: max_drawdown ≤ 35%          |     4.46% |     OK |
| Critério 3: spread+10 / baseline ≥ 0.95 |  **0.9418** | **FAIL** |

## Blockers

Critério 3 violado — piloto não é elegível para `canary_only` mesmo com edge
médio positivo.

## Findings

1. **ADR-0025 Critério 3 captura exatamente o tipo de overfitting mais
   insidioso: parametrização que maximiza edge médio mas gera custos não
   sustentáveis.** Sem o critério, O.1 pareceria superior a N.2 (MC p5
   maior, edge médio maior). Com o critério, O.1 é detectado como
   economicamente frágil.
2. **Frequência-custo relação é linear.** N.2 tem 64 trades e ratio 0.9747;
   O.1 tem 147 trades (+130%) e ratio 0.9418 (−0.033, escala linear esperada:
   ratio = 1 − k·trades, com k ≈ 3.9e-4/trade neste regime). Confirma
   linearidade entre trade-count e sensibilidade a spread observada na Série L.
3. **Edge médio por trade O.1 < N.2.** fe_O.1/trades = 0.87 USDT/trade;
   fe_N.2/trades = 1.84 USDT/trade (−53%). Mais trades de qualidade pior —
   configuração 7/25/75 entra em sinais demasiado frequentes/marginais.
4. **ADR-0019 32ª confirmação** (`fee+10 ≡ spread+10 = 9538.35`).
5. **Fold 3 hit=81.48%** — altíssimo, mas não compensa outros folds (57.58%,
   57.69%, 64.52%). Variabilidade inter-fold maior que N.2.

## Lições

1. **Primeira evidência de overfit-via-parâmetro detectado por custo stress.**
   O.1 é um caso-escola: edge médio positivo, WF 4/4 folds ≥45%, MC p5 maior
   que 14/30/70 — mas Critério 3 falha. Se o protocolo tivesse só Critérios
   1+2, O.1 passaria. ADR-0025 está **fazendo seu trabalho**.
2. **Frequência ≠ edge.** Aumentar frequência de sinais (via `period=7` e
   `oversold=25`) parece oferecer mais oportunidades, mas custo por
   oportunidade fica constante — o saldo é pior se o edge por trade cai mais
   rápido que a frequência sobe.
3. **Sweet spot paramétrico ≈ N.2 (14/30/70).** Sweep não encontrou
   configuração superior. RSI padrão é razoável; sensibilidade é relativamente
   achatada em regime favorável.
4. **Séries L (timeframe) + O.1 (parâmetro) convergem:** ambos quebram por
   Critério 3 via frequência de sinais. "Mais trades" não é solução para
   edge marginal.

## Recomendações

- **Não promover O.1.** `fail` é definitivo por ADR-0025.
- **O.2 RSI 21/35/65 continua como controle inverso** (menos trades, thresholds
  mais largos) — provável `canary_only` marginal.
- **Série P (próxima):** aplicar regime filter (ADR-0022 `sma_slope` ou
  `atr_regime`) a J.2 BTC Bollinger para tentar elevar MC p5 > capital do
  candidato primário de handoff. Infraestrutura pronta; valor esperado maior
  que sweep de parâmetros.
