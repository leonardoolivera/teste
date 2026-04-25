# AUDIT.md — I.3 Bollinger 20/2 ETH 180d

release_decision: canary_only

## release_decision

**`canary_only`** — terceiro do protocolo a cruzar hard gate absoluto. Trio SOL+BTC+ETH completo.

| Gate                                    | Observado              | Status |
| --------------------------------------- | ---------------------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | **63.41%**             | **OK** |
| Critério 2: max_drawdown ≤ 35%          | 5.17%                  | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | 0.967                  | OK     |
| Rank top-3 (ADR-0024, N=15)             | **3/15** (score 7.12)  | OK     |

## Blockers

Módulo `canary-trade` inexistente.

## Findings

1. **Edge mean-reversion generaliza em 3 assets independentes.** SOL (I.1, 65.85%), BTC
   (I.2, 65.85%), ETH (I.3, 63.41%). Todos baseline acima de 45%. Hipótese
   "mean-reversion Bollinger 20/2 em crypto 1h 180d tem edge" é corroborada com n=3.
2. **82 trades exatos em todos os três assets.** Coincidência notável que sugere que o
   trigger edge-triggered duplo (ADR-0026) dispara com frequência estrutural similar em
   tape 1h 180d com 4320 barras, independente de asset.
3. **ETH tem hit marginalmente menor (63.41% vs 65.85% BTC/SOL).** Diferença ~2.4 pp;
   mdd intermediário (5.17% vs 2.80% BTC e 6.93% SOL).
4. **Ranking top-3 é monopólio Bollinger.** Os três pilotos I.1/I.2/I.3 ocupam rank 1/2/3
   com ≥2.17 pontos de margem sobre o 4º (H.9 ETH+SMA, score 5.04). Separação clara
   entre Bollinger e resto.
5. **ADR-0019 15ª confirmação** (`fee+10 ≡ spread+10 = 9729.39`).

## Lições

1. **Série I encerra com sucesso estrutural.** 3/3 pilotos abertos sob ADR-0025
   retornaram `canary_only`. Comparar Série H: 0/12. Mudança de família produziu o sinal
   que o protocolo procurava.
2. **Família importa mais que asset dentro da família Bollinger.** Variação cross-asset
   em hit é 2.44 pp (63.41 a 65.85); Variação dentro da Série H cross-asset para Donchian
   foi 5.62 pp. Mean-reversion tem menos dispersão cross-asset que breakout — sinal mais
   robusto.
3. **Próxima dimensão crítica é temporal.** Todos os 3 pilotos são sobre o mesmo recorte
   de 180 dias (2025-07 → 2025-12). Janela bull/lateral específica pode estar favorecendo
   mean-reversion. Próximo piloto natural: recorte diferente (outro período, não mesmo
   comprimento).

## Recomendações

- **Série I encerrada com 3/3 canary_only.** Abrir Série J com perguntas ortogonais:
  (a) janela temporal diferente (período anterior 2024-07 a 2024-12 se dataset
  disponível), (b) sensibilidade de hiperparâmetros (num_std 1.5/2.5; window 10/50),
  (c) segunda família mean-reversion (RSI) para ortogonalidade intra-classe.
- **Handoff BotBinance** agora tem 3 candidatos concretos. Prioridade por critério:
  - Menor mdd: I.2 BTC (2.80%).
  - Maior fe: I.1 SOL (10189.15, +1.89%).
  - Intermediário equilibrado: I.3 ETH.
  Pré-req antes de export: OOS Sharpe + aprovação do usuário.
