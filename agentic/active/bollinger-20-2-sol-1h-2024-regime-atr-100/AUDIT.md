# AUDIT.md — R.1 Bollinger SOL 1h 2024 + atr_regime:100

release_decision: canary_only

## release_decision

**`canary_only`** — 39º piloto. **Domina J.1 e Q.1 em TODAS as dimensões
raw E composto** (primeiro piloto a dominar em TODAS as métricas incluindo
`fold_min_hit`). **Candidato a novo rank 1 do leaderboard N=39**, possivelmente
superando P.2 BTC dependendo do score composto.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------: | ------ |
| Critério 1: hit_rate baseline ≥ 45%     |    70.77% |     OK |
| Critério 2: max_drawdown ≤ 35%          |     3.43% |     OK |
| Critério 3: spread+10 / baseline ≥ 0.95 |    0.9758 |     OK |

## Blockers

`canary-trade` inexistente.

## Findings

1. **Calibração do threshold por asset unlocka o filtro em SOL.** Q.1
   (threshold 50) ficou quase inativo (−1 sinal de 87); R.1 (threshold
   100) ativa em 25% dos sinais (87→65). **Volatilidade típica de SOL
   2024-H2 está em ~70-150 bps range**; threshold 100 bps captura a cauda
   inferior da distribuição onde mean-reversion é frágil.
2. **R.1 tem o maior fe operacional do protocolo** (10803.68) — supera
   todos os P.x BTC (10316 max), todos os K.x SOL (10872 K.1 mas em janela
   diferente), todos os Bollinger 180d. **Combina edge intrínseco de SOL
   com qualidade de sinal do filtro calibrado.**
3. **MC p5 = 10212.03 é o maior do protocolo** (supera P.3=9995, Q.1=10064,
   J.1=10046). Cauda inferior mais robusta de todos os 39 pilotos.
4. **Stress `fee+10 = spread+10 = 10542.34`** — **primeira vez que cenário
   stress termina > 10500**. Edge do filtro calibrado sobrevive stress
   com margem inédita.
5. **Folds todos ≥ 64.29%** — `fold_min_hit` melhora vs J.1 (47.06%) e
   Q.1 (47.06%). Lição Q.2: filtro pode piorar fold_min; aqui, filtro
   **melhora** fold_min — depende da qualidade dos sinais filtrados.
6. **ADR-0019 39ª confirmação** (`fee+10 ≡ spread+10 = 10542.34`).
7. **Escolha do threshold é ADR-0024-eficiente:** filtro remove 25% piores
   sinais; resto domina em todas as 7 dimensões do score composto
   (hit, fe, mdd, stress, MC p5, fold_min, fold_std menor=melhor).

## Lições

1. **Universalidade de filtro de regime é questão de CALIBRAÇÃO, não de
   arquitetura.** Série Q refutou "`atr:50` é universal"; R.1 mostra que
   "`atr` + threshold por asset" é o contrato correto. Este é o framework
   para aplicar regime filters cross-asset em produção.
2. **Threshold ≈ quantile 15-25 da distribuição de ATR do asset** parece
   ser o sweet spot. BTC 2024-H2 quantile 25 ≈ 50 bps (P.2 ativa 15%);
   SOL 2024-H2 quantile 25 ≈ 100 bps (R.1 ativa 25%). Hipótese testável
   em Série futura.
3. **R.2 (threshold 150 bps)** provavelmente será over-filtering em SOL —
   testar para confirmar curva em U ou escada.
4. **Série Q ETH era equivocada em aplicar threshold 50 em ETH sem
   calibração.** Q.2 teve ganho menor porque 50 bps também não é o ideal
   para ETH. Falta Q.3 com threshold calibrado ETH (estimativa: 70-80 bps).

## Recomendações

- **R.1 é o novo candidato primário a handoff BotBinance** se composite
  score N=39 confirmar rank 1. Verificar no ranking antes de mudar STATE.
- **Continuar R.2 (threshold 150)** para mapear curva.
- **Série T candidata: calibrar threshold ETH** (`atr_regime:14:75` e
  `14:100` em J.3 ETH) para recuperar ganho operacional perdido em Q.2.
- **Série T: calibrar threshold BTC** (`atr_regime:14:35` e `14:70`) em
  J.2 BTC — pode otimizar além de P.2.
