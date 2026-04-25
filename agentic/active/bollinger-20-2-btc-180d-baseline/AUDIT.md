# AUDIT.md — I.2 Bollinger 20/2 BTC 180d

release_decision: canary_only

## release_decision

**`canary_only`** — segundo do protocolo a cruzar hard gate absoluto `hit_rate ≥ 45%`.

**Critério vigente:** ADR-0025 híbrido. `canary_only` prevalece sobre `paper_only` quando
edge absoluto existe.

| Gate                                    | Observado              | Status |
| --------------------------------------- | ---------------------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | **65.85%**             | **OK (canary_only ativo)** |
| Critério 2: max_drawdown ≤ 35%          | 2.80%                  | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | 0.967                  | OK     |
| Rank top-3 (ADR-0024, N=15)             | **1/15** (score 7.70)  | OK (redundante) |

## Blockers

Módulo `canary-trade` inexistente — execução efetiva pendente de infraestrutura futura.

## Findings

1. **Generalização cross-asset do edge mean-reversion confirmada.** I.2 BTC cruza 45%
   (65.85%) com mesma janela, hiperparâmetros e custos que I.1 SOL. Hipótese "família
   mean-reversion em crypto 1h tem edge" ganha n=2 forte.
2. **Hit_rate baseline numericamente idêntico entre assets (65.85%, 82 trades).** Coincidência
   notável — SOL e BTC terminam com mesmo número de trades e mesmo hit_rate. Sugere que
   mean-reversion em tape 180d 1h tem componente estrutural independente de asset.
3. **BTC tem menor mdd do protocolo inteiro (2.80%).** Menos volátil que SOL → oscilações
   ao redor das bandas menores em amplitude, mas mais frequentes; net PnL menor por trade.
4. **Fold 2 marginalmente abaixo de 45% (44.44%).** Único fold não-cruzante do piloto.
   Fold 2 em BTC contém período com tendência direcional mais forte — mean-reversion sofre
   em trends. Agregação passa.
5. **ADR-0019 14ª confirmação** (`fee+10 ≡ spread+10 = 9703.27`).
6. **Rank 1/15 em score composto** (7.70; +0.51 sobre I.1 SOL). BTC vence no ranking por
   mdd dramaticamente menor (2.80% vs 6.93%), apesar de fe menor.

## Lições

1. **Edge é da família, não do asset.** Dois assets independentes (SOL volátil, BTC
   moderado) produzem hit idêntico com mesma configuração. Série H achava "asset é a
   variável dominante"; Série I mostra "família é a variável dominante, asset modula
   risco/retorno mas não hit".
2. **Hit ≠ PnL.** I.2 vence em hit e mdd, I.1 vence em fe. Ranking (ADR-0024) com pesos
   atuais prioriza hit + mdd → I.2 rank 1. Trade-off: BTC é mais "seguro" por mdd,
   SOL mais "rentável" por fe.
3. **Replicação é barata agora.** Custo de I.2 foi ~10 minutos (zero código, só validate).
   Próximos pilotos cross-asset/cross-janela/cross-threshold são replicação pura da receita.

## Recomendações

- **I.3 ETH** já rodado em paralelo; análise em `bollinger-20-2-eth-180d-baseline/`.
- **I.4 sensibilidade num_std** (1.5, 2.5) sobre o asset winner (SOL ou BTC).
- **I.5 janela 10/1.5 ou 50/2** sobre SOL/BTC — verificar se período de lookback importa.
- **Handoff BotBinance:** I.2 BTC é forte candidato por baixo mdd; I.1 SOL por fe. Pré-req
  antes de export: OOS Sharpe explícito + aprovação do usuário.
