# 0224 — Stack 13: Paper-trade observation S10/S11 antes de retirada

**Status:** Accepted (operational protocol)
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0222 (Cycle 8 stack 13 audit Padrão 60), ADR-0030 (export gates), AGENTS.md §8 (handoff contract BotBinance)

## Contexto

ADR-0222 identificou S10 (rsi_short_pure_2025h2 BTCUSDT) e S11 (rsi_short_pure_2025h2 SOLUSDT) como **catastróficos sob janela contínua 30m**:

| ID | Manifest | Sym | Sh | Tr | MDD% | PnL% (30m) |
|---|---|---|---:|---:|---:|---:|
| S10 | rsi_short_pure_2025h2 | BTC | -0.58 | 424 | **22.0** | **-11.7** |
| S11 | rsi_short_pure_2025h2 | SOL | -0.38 | 392 | **35.9** | **-16.8** |

Discovery em 2025-H2 isolada (oos_sharpe 1.64 BTC, 2.30 SOL conforme manifest aprovado) foi **selection bias temporal** confirmado — em janela contínua 2023-H2..2025-H2, edge inverte negativamente.

Risco operacional: ambos manifests **estão em produção/staging paper-trade** (`exports/approved/rsi_short_pure_2025h2_20260419.json`). Se condições de mercado pós-2025-H2 ressuscitarem regime tipo 2023-H2 (recovery early), stack pode incorrer drawdown agudo.

## Decisão (operational protocol)

**NÃO retirar S10 e S11 imediatamente do stack canonical.** Precipitação cria risco simétrico (perder edge real se Padrão 60 audit foi enviesado). Em vez disso, executar **paper-trade observation extended** com critério explícito de retirada:

### Protocolo de observação

**Duração:** 14 dias úteis (2 semanas) a partir de 2026-04-26.

**Sinais de retirada (qualquer um → flag para retirada):**
1. **Drawdown intra-period > 8%** em qualquer combo (S10 ou S11) durante observation window. Threshold conservador (V1 manifest declarava MDD esperado 4.97% S10 e ~5% S11 — 8% = 1.6× margem).
2. **Sequência adversa**: 5+ trades consecutivos com PnL negativo em S10 ou S11.
3. **Net PnL period < -3%** ao final dos 14 dias (qualquer combo).
4. **Correlação anômala**: corr(S10 daily PnL, S11 daily PnL) > 0.85 (sinal de regime adverso compartilhado, não diversificação).

**Sinais de manutenção:**
- Net PnL period > 0 + MDD < 5% em ambos.
- Trade count ≥ 10 em cada (ainda há sinais sendo gerados, não-zumbi).

### Cronograma

| Data | Ação |
|---|---|
| 2026-04-26 | Início observation. Snapshot inicial equity per combo. |
| 2026-05-03 | Mid-check (7 dias). Se sinais 1-3 ativos → considerar retirada antecipada. |
| 2026-05-10 | End-check (14 dias). Decisão final retirada vs manutenção. |

### Outputs do protocol

- **`exports/diag/s10_s11_paper_observation_<YYYYMMDD>.json`**: snapshot daily de PnL, trades, equity por combo.
- **ADR-0225+**: decisão de retirada (se acionada) com manifests v3 atualizados (stack v9 sem S10/S11).
- **Bridge notification**: BotBinance recebe heads-up sobre observation extended (não muda stack, mas avisa risk monitoring).

## Mitigation paralela (sem mexer no stack)

Para reduzir exposure aos combos suspeitos durante observation:

1. **Nenhuma ação de retirada** — manter alocação 1/13 em paper-trade.
2. **Monitoring automation**: if Bot live trade infra detecta 3+ stops em sequência em S10 ou S11, pausa esses combos manualmente até review.
3. **Não ampliar** stack 13 com novos combos similares (rsi_short_pure 2025h2 family).

## Consequences

- **Positive:** decisão informada baseada em observation real, não apenas backtest retroativo. Reduz risco de retirada precipitada (gambit: ADR-0222 audit em janela longa pode não capturar mecanismo causal real do edge).
- **Negative:** 2 semanas de exposição continuada a combos potencialmente fee-fragile. Limitação aceitável dado MDD esperado original 4.97-5%.
- **Neutral:** S10/S11 mantêm-se em manifests aprovados durante observation — handoff a BotBinance segue contrato vigente.

## Não-alvo

- Não retirar imediatamente baseado em audit retroativo isolado.
- Não relaxar threshold (8% drawdown) se observation mostrar 6-7% — disciplina mantida.
- Não estender observation além de 14 dias sem ADR explícito.
- Não substituir S10/S11 por novos combos durante observation (pode correlacionar artefatos).

## Follow-ups

- **2026-05-10**: ADR-0225 com decisão retirada vs manutenção.
- Se retirada: stack v9 manifest formal, bridge notification BotBinance, ADR de transition window.
- Se manutenção: revisar Padrão 60 audit (algo pode estar enviesado na re-execução vs aprovação original).
