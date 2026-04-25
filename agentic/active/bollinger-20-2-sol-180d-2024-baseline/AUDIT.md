# AUDIT.md — J.1 Bollinger 20/2 SOL 180d 2024

release_decision: canary_only

## release_decision

**`canary_only`** — quarto do protocolo a cruzar hard gate absoluto. Primeiro da Série J.
**Robustez temporal corroborada:** edge mean-reversion sobrevive janela não-correlata (2024-H2).

| Gate                                    | Observado              | Status |
| --------------------------------------- | ---------------------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | **67.82%**             | **OK** |
| Critério 2: max_drawdown ≤ 35%          | 3.43%                  | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | 0.967                  | OK     |

## Blockers

Módulo `canary-trade` inexistente.

## Findings

1. **Robustez temporal confirmada.** I.1 SOL 2025 = 65.85%; J.1 SOL 2024 = 67.82%. Dois
   períodos não-correlatos (6 meses de gap) cruzam 45% com margem. Edge NÃO é artefato
   da janela bull-lateral de 2025-H2.
2. **J.1 domina I.1 em todos os eixos.** fe +4.86 pp (10684 vs 10189), hit +1.97 pp, mdd
   −3.50 pp (3.43% vs 6.93%), MC p5 +7.69 pp (10047 vs 9278). 2024-H2 tem edge mais limpo
   que 2025-H2 para SOL.
3. **Fold 3 atinge 88.24% hit** — maior hit por fold do protocolo inteiro (vs máximo
   anterior 76.47% em I.1 fold 3). Regime desse fold específico é especialmente favorável
   a mean-reversion.
4. **Fold mínimo 47.06% (fold 2)** — marginal mas acima de 45%. Todos os 4 folds cruzam.
5. **ADR-0019 16ª confirmação** (`fee+10 ≡ spread+10 = 10335.23`).

## Lições

1. **Edge sobrevive dimensão temporal.** Série J abre com confirmação forte: a primeira
   dimensão ortogonal testada (temporal, 2024 vs 2025) preserva o edge. Hipótese "é
   artefato de janela" REFUTADA pela J.1.
2. **SOL 2024 > SOL 2025 em qualidade de edge.** A reversão da assimetria (2024-H2 foi
   mais lateral/oscilatório que 2025-H2 bull-drift) explica por que mean-reversion tem
   edge maior — condições de mercado favoráveis.
3. **MC p5 > capital inicial (10046.92)** — pela primeira vez no protocolo, a cauda
   inferior 5% do Monte Carlo baseline está acima de 10000. Sinal estatístico forte de
   que edge absoluto está acima do capital.
4. **Série J vai para 3/3 cross-window?** J.2 BTC 2024 e J.3 ETH 2024 vão confirmar ou
   refutar que edge cross-window é propriedade da família.

## Recomendações

- **Continuar J.2 BTC 2024 e J.3 ETH 2024** para fechar trio cross-window. Se 3/3 passam,
  robustez temporal vira propriedade estrutural confirmada; se só SOL passa, edge temporal
  pode ser asset-específico.
- **SOL 2024 candidato primário a handoff BotBinance após J.2/J.3.** Combina: hit 67.82%
  + mdd 3.43% + MC p5 > 10000 + robusto cross-window. Pré-requisitos antes de export:
  OOS Sharpe explícito + aprovação do usuário.
