# AUDIT.md — J.2 Bollinger 20/2 BTC 180d 2024

release_decision: canary_only

## release_decision

**`canary_only`** — quinto do protocolo a cruzar hard gate absoluto. Segundo da Série J.
Edge temporal BTC confirmado.

| Gate                                    | Observado              | Status |
| --------------------------------------- | ---------------------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | **68.24%**             | **OK** |
| Critério 2: max_drawdown ≤ 35%          | 3.62%                  | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | 0.967                  | OK     |

## Blockers

Módulo `canary-trade` inexistente.

## Findings

1. **BTC cross-window 2/2.** I.2 (2025-H2) hit=65.85%; J.2 (2024-H2) hit=68.24%. Ambos
   cruzam 45% com margem ampla. Edge BTC é robusto a janela temporal.
2. **Fold-homogeneidade máxima do protocolo:** std_hit 3.48 pp (vs 9.65 I.2, 10.90 I.3,
   11.04 I.1). Todos os 4 folds entre 64.71 e 72.73%. **Menor dispersão fold-a-fold
   observada.**
3. **Fold mínimo 64.71%** (vs 44.44% em I.2 fold 2 — marginal). Sai da zona de alerta
   para região confortável.
4. **ADR-0019 17ª confirmação** (`fee+10 ≡ spread+10 = 9911.98`).

## Lições

1. **Série J 2/2 até agora — robustez temporal generaliza cross-asset.** J.3 ETH
   pendente para fechar trio.
2. **2024-H2 BTC tem edge mais limpo que 2025-H2 BTC** — hit +2.39 pp, fold-min
   +20.27 pp. Inversão do padrão "janela recente é melhor" — mean-reversion
   beneficia-se de regime mais lateral/oscilatório.
3. **BTC J.2 candidato forte a handoff BotBinance.** Combina: menor mdd, maior
   fold-homogeneidade, 2º maior hit do protocolo. **Melhor perfil risco/retorno
   até agora.**

## Recomendações

- **Fechar J.3 ETH 2024** antes de qualquer handoff.
- **Re-ranquear N=18** com os 6 pilotos Bollinger + 12 Série H.
- **Considerar promoção de candidato primário:** J.2 BTC (se J.3 ETH confirmar padrão) com
  OOS Sharpe explícito.
