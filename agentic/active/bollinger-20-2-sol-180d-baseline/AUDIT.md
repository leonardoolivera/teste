# AUDIT.md — I.1 Bollinger 20/2 SOL 180d

release_decision: canary_only

## release_decision

**`canary_only`** — primeiro do protocolo a cruzar hard gate absoluto (`hit_rate ≥ 45%`).

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto;
`paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9. `canary_only` é o canal
*mais forte* quando ambos se aplicam.

### Observado vs ADR-0025

| Gate                               | Observado              | Status |
| ---------------------------------- | ---------------------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%| **65.85%**             | **OK (canary_only ativo)** |
| Critério 2: max_drawdown ≤ 35%     | 6.93%                  | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | 0.968             | OK     |
| Rank top-3 (ADR-0024, N=13)        | **1/13** (score 7.66)  | OK (redundante com canary_only) |

**Decisão:** `canary_only`. `paper_only` também seria acionado pela posição no ranking, mas
`canary_only` é decisão dominante (há edge absoluto, não só relativo).

## Blockers

**`canary_only` bloqueado por ausência de módulo `canary-trade`.** ADR-0005 proíbe `live`;
`canary_only` requer pipeline de execução em ambiente isolado com capital real pequeno,
infraestrutura que **ainda não existe** neste repositório. Handoff para BotBinance (AGENTS.md §8)
é `paper_only` na prática até módulo `canary-trade` existir.

Decisão formal: **`canary_only` registrado**; execução efetiva fica pendente de infraestrutura
futura (segue mesma situação operacional documentada para `paper_only` no template AUDIT.md).

## Findings

1. **Primeiro piloto do protocolo a cruzar `hit_rate ≥ 45%`.** Hit 65.85% — 2.06× o maior da
   Série H (H.10 SOL: 31.07%, Donchian). Falsifica a conclusão da Série H "edge não existe
   nesta família causal sem filtro": edge **existe em outra família**.
2. **Ortogonalidade de família confirmada em tape compartilhado.** Mesmo dataset SOL 180d, duas
   estratégias: Donchian 20/10 (breakout) = 31.07% hit / 14.55% mdd; Bollinger 20/2
   (mean-reversion) = 65.85% hit / 6.93% mdd. SOL tem componente mean-reversion dominante no
   período 2025-07 a 2025-12.
3. **Fold-homogeneidade inédita:** os 4 folds cruzam 45% (50% a 76.47%; std 11.04 pp). H.10 SOL
   tinha 1 fold a 47.62% e 1 fold a 9.52%. Sinal mean-reversion em SOL não é fold-dependent.
4. **ADR-0019 13ª confirmação** (`fee+10 ≡ spread+10 = 9859.11`). Primeira confirmação sobre
   família mean-reversion — antes só tinha Donchian + MA-crossover.
5. **ADR-0010 confirmado sobre família mean-reversion.** Property test
   `test_cost_monotonicity_bollinger` (30 examples, 3 eixos) verde; baseline observado também
   respeita monotonicidade (baseline > slip+5 > {fee+10, spread+10}).
6. **Menor mdd na família mean-reversion sobre SOL:** Bollinger 6.93% vs Donchian 14.55%. Menos
   trades (82 vs 103), maior seletividade pelo duplo-cruzamento edge-triggered (ADR-0026).

## Lições

1. **Série I corrobora a hipótese "mudança estrutural de família é o caminho".** Primeira
   evidência de que o piso de 45% (ADR-D, ADR-0025) **não é inatingível no laboratório** — só
   é inatingível na família breakout-causal-sem-filtro.
2. **"Qual família?" é pergunta mais importante que "qual filtro?"** — diferença cross-family
   (+34.78 pp hit Donchian SOL → Bollinger SOL) é **7.7× maior** que a maior diferença cross-filter
   da Série H (+4.37 pp em H.3 BTC).
3. **SOL não é ativo ruim — era ativo com família errada.** H.10 concluíra "SOL tem maior
   dispersão fold-a-fold, asset volátil"; I.1 reinterpreta: SOL é volátil *na direção* — janela
   de 180d tem componente oscilatório forte captured by Bollinger.

## Recomendações (abertura Série I)

- **I.2 Bollinger 20/2 BTC 180d** — testar se mean-reversion generaliza cross-asset ou se é
  propriedade específica de SOL no período.
- **I.3 Bollinger 20/2 ETH 180d** — terceiro ativo.
- **I.4 Bollinger com num_std variados (1.5, 2.5)** — sensibilidade do threshold da banda.
- **I.5 RSI long-only** (se fizer sentido) — segunda família mean-reversion, ortogonal a Bollinger.
- **Atualizar ADR-0025 aplicação** — agora que Série I tem piloto `canary_only`, ranking passa
  a ter `canary_only` concreto em top (redundante com `paper_only` para pilotos que cruzam ambos).
- **Revisitar handoff BotBinance (AGENTS.md §8):** Bollinger I.1 é o primeiro candidato concreto
  a `exports/approved/<strategy_name>_<YYYYMMDD>.json`. Pré-requisitos do handoff:
  - OOS Sharpe ≥ 1.0 → precisa computar (não está nos 4 JSONs).
  - OOS MDD ≤ 20%: baseline 6.93% ✓ (mas OOS específico exige separação train/test).
  - OOS PnL > 0: +1.89% baseline ✓.
  - Trade count ≥ 30: 82 ✓.
  - ADR-0026 escrito ✓.

  **Lista de pendências antes de exportar:** (a) computar OOS Sharpe explicitamente; (b)
  aprovação explícita do usuário para handoff (AGENTS.md §8 "Do NOT export: strategies the user
  has not explicitly approved for handoff").
