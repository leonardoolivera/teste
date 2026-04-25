# AUDIT.md — M.3 Bollinger 20/2 ETH 4h 2024

release_decision: fail

## release_decision

**`fail`** — terceiro consecutivo da Série M. Único do trio a violar critério 1
(hit=43.75% < 45%) + fe < capital + mdd pior.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | 43.75%    | **VIOLADO** |
| Critério 2: max_drawdown ≤ 35%          | 8.54%     | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | **0.9933**| OK     |
| Hipótese SPEC: fe > capital             | 9327.15   | **VIOLADO** |

## Blockers

- Hit=43.75% é o menor da Série M e falha o hard gate.
- Fe=9327.15 é o pior da Série M (−6.73% do capital).
- Mdd=8.54% é o maior da Série M.
- Amostra mínima: 16 trades, 4 trades/fold médios.

## Findings

1. **Paradoxo de amostra pequena em M.3:** 4/4 folds WF cruzam 45% (50-66.67%) mas
   baseline consolidado fica em 43.75%. Cada fold teve sorte dentro de sua janela;
   agregado acumula perdedores.
2. **ETH é o pior asset em 4h** — combina pior hit, pior fe, pior mdd do trio M.
   Contrasta com J.3 (ETH 1h) que tinha **maior hit** do trio J (71.76%). Asset com
   maior volatilidade mean-reversion em 1h é o mais prejudicado por 4h.
3. **Série M fecha com padrão uniforme fail.** Trade-off de timeframe agora
   formalmente delimitado por dois trios `fail`:
   - Série L (15m): critério 3 violado (custos)
   - Série M (4h): hipótese SPEC violada (edge insuficiente)
   - **Sweet spot 1h** (Séries I + J): 3/3 × 2 = 6/6 `canary_only`.
4. **ADR-0019 28ª confirmação** (`fee+10 ≡ spread+10 = 9264.56`).

## Lições

1. **Timeframe ótimo Bollinger 20/2 é universal em 1h para este protocolo de custos.**
   Duas janelas (2025-H2 Série I + 2024-H2 Série J) × 3 assets × 2 family params (J + K)
   concordam. Delimitado formalmente por L (15m quebra) e M (4h quebra).
2. **Série M retorna sinal informativo negativo claro.** Diferente de L (crítica
   operacional explícita: custos), M é crítica estatística (edge dilui). Ambas são
   descobertas formais úteis — NÃO são ruído.
3. **Handoff BotBinance confirma-se em 1h.** J.2 BTC 1h 2024 e J.1 SOL 1h 2024
   permanecem candidatos primários.

## Recomendações

- **Nenhuma nova ADR.** ADR-0025 + hipótese SPEC capturaram o caso.
- **Encerrar exploração de timeframe.** L + M delimitaram sweet spot.
- **Próximos candidatos (ordem de prioridade):**
  1. **Série N: RSI 1h cross-asset** — segunda família mean-reversion. Requer
     nova ADR (RSIMeanReversion) + implementação. ~20 linhas de código + testes.
  2. **Série O: regime filter + Bollinger 1h** — filtro ATR para cortar trend regime
     e preservar edge mean-reversion só em laterais. ADR-0022 já cobre contrato.
  3. **Export handoff J.2 BTC 1h 2024** — caminho para BotBinance, requer OOS Sharpe
     + aprovação explícita do usuário (AGENTS.md §8).
