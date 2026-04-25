# AUDIT.md — N.2 RSI 14/30/70 BTC 1h 2024

release_decision: canary_only

## release_decision

**`canary_only`** — 30º piloto do protocolo. Segundo RSI cruzando hard gate.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------: | ------ |
| Critério 1: hit_rate baseline ≥ 45%     |    67.19% |     OK |
| Critério 2: max_drawdown ≤ 35%          |     3.46% |     OK |
| Critério 3: spread+10 / baseline ≥ 0.95 |     0.975 |     OK |

## Blockers

`canary-trade` inexistente.

## Findings

1. **BTC é asset onde RSI mais se aproxima de Bollinger.** N.2 hit=67.19% vs
   J.2 Bollinger hit=68.24% (−1.05 pp, vs −9.09 pp em SOL). fe positiva
   (10117.99 > 10000). MDD 3.46% = J.2.
2. **4/4 folds cruzam 45%**, inclusive fold 3 com **90% hit** (maior hit por
   fold de RSI até agora; todos os 3 pilotos N). Cauda Monte Carlo p5 = 9878,
   marginal mas melhor que N.1 SOL.
3. **ADR-0019 30ª confirmação** (`fee+10 ≡ spread+10 = 9862.02`).
4. **Trades: 64 N.2 vs 85 J.2** — RSI gera −25% sinais vs Bollinger na mesma
   janela BTC. Menos trades, hit comparável, edge por trade ligeiramente maior
   em BTC.
5. **fe positiva (+117.99).** Único piloto N com fe positiva — BTC 2024 é o
   regime mais favorável a RSI 14/30/70.

## Lições

1. **Edge MR @ 1h é cross-família + cross-asset em BTC.** Bollinger e RSI
   convergem em BTC: duas famílias independentes com métricas dentro de 1–2 pp.
   Propriedade estrutural do regime, não do indicador.
2. **Asset-specific spread (SOL vs BTC) afeta RSI mais que Bollinger.**
   N.1 SOL inferior a J.1 Bollinger SOL em 9 pp; N.2 BTC só 1 pp abaixo de J.2.
   Hipótese: volatilidade elevada de SOL degrada detecção de cruzamento RSI
   (SMA-smoothed) mais do que banda estatística Bollinger.

## Recomendações

- **Continuar N.3 ETH** para fechar trio.
- Se N.3 passa: RSI vira segunda família canary-ready, com BTC como asset
  primário (N.2 mais forte do trio em todas as dimensões).
- **Sweep Série O?** Testar RSI 7/25/75 e 21/35/65 sobre BTC 2024 para tentar
  extrair edge > Bollinger.
