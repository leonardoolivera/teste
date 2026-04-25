# AUDIT.md — N.1 RSI 14/30/70 SOL 1h 2024

release_decision: canary_only

## release_decision

**`canary_only`** — 29º piloto do protocolo. Primeiro `canary_only` de família
não-Bollinger no regime 1h 2024-H2.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------: | ------ |
| Critério 1: hit_rate baseline ≥ 45%     |    58.73% |     OK |
| Critério 2: max_drawdown ≤ 35%          |     6.35% |     OK |
| Critério 3: spread+10 / baseline ≥ 0.95 |     0.975 |     OK |

## Blockers

Módulo `canary-trade` inexistente (idem Séries I/J).

## Findings

1. **Edge mean-reversion é estrutural no regime 1h.** Segunda família MR
   (RSI SMA-smoothed, ADR-0027) cruza os 3 critérios sobre o mesmo dataset
   onde Bollinger cruzou (J.1). Edge **não é Bollinger-específico**.
2. **N.1 < J.1 em qualidade.** fe −7.82 pp (9850 vs 10684), hit −9.09 pp, mdd
   +2.92 pp. RSI 14/30/70 é configuração mais conservadora (menos trades: 63
   vs 87 = −27%) e gera sinais de qualidade inferior em SOL 2024-H2.
3. **MC p5 < capital (9568.51).** Cauda inferior 5% é deficitária — edge
   absoluto não excede capital com 95% de confiança. Diferença crucial vs J.1
   (MC p5 = 10046.92 > 10000).
4. **Fold 3 com hit 42.86% (7 trades).** Fold problemático, amostra pequena.
   Agregado salva; fold-a-fold é marginal.
5. **ADR-0019 29ª confirmação** (`fee+10 ≡ spread+10 = 9598.55`).

## Lições

1. **MR é uma classe, não uma assinatura de família.** Duas famílias
   independentes (Bollinger bandas desvio-padrão vs RSI momentum-oscillator SMA)
   passam os 3 gates no mesmo regime. O edge existe na **propriedade
   mean-reversion sobre crypto 1h**, não em indicadores específicos.
2. **RSI é inferior a Bollinger em SOL 2024.** Pode ser (a) parâmetros padrão
   sub-ótimos (14/30/70 vs otimizado), (b) SMA smoothing menos sensível que
   banda estatística, ou (c) RSI tem edge em regimes diferentes. Sweep de
   parâmetros (Série O?) esclareceria.
3. **Custo relativo idêntico a Bollinger.** Fee/spread ratio ≈ 0.975 em ambos
   — taxa de perda por trade é propriedade do regime+custo, não do sinal.

## Recomendações

- **Continuar N.2 BTC e N.3 ETH** para fechar trio cross-asset RSI.
- **Se N.2/N.3 passam:** edge MR @ 1h vira propriedade estrutural forte
  (6 pilotos: 3 Bollinger + 3 RSI, duas famílias independentes).
- **Sweep de parâmetros RSI** após N.2/N.3: testar (period=7, os=25, ob=75) e
  (period=21, os=35, ob=65) para mapear sensibilidade.
- **Não priorizar N.1 para handoff** — J.1 domina em todas as métricas. RSI só
  vale como diversificação se parâmetros ótimos superarem J.1.
