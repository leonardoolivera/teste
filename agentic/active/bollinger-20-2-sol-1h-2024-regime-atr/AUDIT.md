# AUDIT.md — Q.1 Bollinger SOL 1h 2024 + atr_regime

release_decision: canary_only

## release_decision

**`canary_only`** — 37º piloto. Cruza os 3 critérios ADR-0025. **Filtro ATR
quase inativo em SOL 2024-H2**: 1 sinal de 87 suprimido, ganho em fe +32.49
e MC p5 +17.24 é via timing marginal. Q.1 ≈ J.1 operacionalmente. **Não
muda handoff**; evidência de que **ganho de P.2 em BTC é asset-específico,
não universal**.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------: | ------ |
| Critério 1: hit_rate baseline ≥ 45%     |    67.82% |     OK |
| Critério 2: max_drawdown ≤ 35%          |     3.43% |     OK |
| Critério 3: spread+10 / baseline ≥ 0.95 |    0.9674 |     OK |

## Blockers

`canary-trade` inexistente.

## Findings

1. **Filtro ATR é quase totalmente inativo em SOL 2024-H2.** 86 de 87 sinais
   preservados (99.0% passam filtro). Volatilidade de SOL mantém ATR > 50
   bps quase continuamente no semestre 2024-H2.
2. **Hit_rate, trade_count e WF folds idênticos a J.1.** Ganho de fe +32.49
   vem de timing marginal de 1 entrada relocada 6 horas adiante.
3. **MC p5 > 10000 (10064.16)** — 2º melhor MC p5 entre assets SOL
   (atrás de K.3 SOL 10/2).
4. **ADR-0019 37ª confirmação**: `fee+10 ≡ spread+10 = 10367.65` (2ª vez
   cenário stress > 10000; primeira em SOL).
5. **Refuta hipótese "atr_regime é universal"**: ganho do filtro ATR
   **depende da distribuição de volatilidade do asset/janela**. Em BTC
   2024-H2, havia períodos de baixa vol onde filtro cortava sinais ruins;
   em SOL, volatilidade é alta o semestre inteiro — filtro nunca aciona.

## Lições

1. **Universalidade de filtros de regime deve ser testada empiricamente
   por asset.** Filtro é estatisticamente neutro no limite (ADR-0022
   property tests passam); utilidade depende de distribuição de volatilidade
   observada no asset/janela específicos. SOL 2024-H2 = volatilidade
   consistentemente alta → filtro ATR inútil.
2. **Parametrização de threshold ATR importa mais em alta-vol assets.**
   `min_atr_bps=50` é apropriado para BTC mas baixo demais para SOL
   (SOL tem ATR típico de 70-150 bps). Para SOL, testar threshold mais
   alto (e.g., 100 bps) seria próxima iteração lógica — mas escopo
   de Q era replicação exata de P.2, não otimização.
3. **SOL tem fe intrinsecamente maior que BTC** (10716 vs 10316) — edge
   do asset em 2024-H2 domina edge do filtro. ATR nem chega a disparar.

## Recomendações

- **Manter J.1 (= Q.1) como handoff secundário.** Q.1 é marginalmente
  superior mas não muda ranking top-3.
- **Não propor threshold tuning em Q (fora de escopo).** Registrar como
  candidato futuro: `atr_regime` com threshold calibrado por asset.
- **Aguardar Q.2 ETH** para decidir se filtro ATR tem qualquer valor
  universal em Bollinger mean-reversion 1h 2024-H2.
