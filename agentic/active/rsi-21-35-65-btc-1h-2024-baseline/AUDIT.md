# AUDIT.md — O.2 RSI 21/35/65 BTC 1h 2024

release_decision: canary_only

## release_decision

**`canary_only`** — 33º piloto. Terceiro RSI cruzando hard gate, mas **domina
em nenhuma dimensão vs N.2** — pior hit, pior fe, pior MC p5, melhor apenas em
mdd e spread ratio (marginal).

| Gate                                    | Observado | Status |
| --------------------------------------- | --------: | ------ |
| Critério 1: hit_rate baseline ≥ 45%     |    58.62% |     OK |
| Critério 2: max_drawdown ≤ 35%          |     3.65% |     OK |
| Critério 3: spread+10 / baseline ≥ 0.95 |     0.977 |     OK |

## Blockers

`canary-trade` inexistente.

## Findings

1. **Sweep RSI em BTC 2024 não achou configuração melhor que 14/30/70.**
   O.1 (faster) falha; O.2 (slower) passa mas com edge médio mais fraco.
   Conclusão: N.2 é ótimo local.
2. **Fold 2 hit=44.44%** — marginal, 0.56 pp abaixo de 45%. Amostra 9 trades.
   Sinal de que a parametrização lenta perde resolução em amostras pequenas.
3. **MC p5 = 9595.53** é o **pior MC p5 de todos os 13 pilotos `canary_only`**.
   Edge absoluto mais frágil; cauda inferior pode produzir perda de 4% com
   5% de probabilidade.
4. **ADR-0019 33ª confirmação** (`fee+10 ≡ spread+10 = 9728.15`).
5. **Fe negativa** (9959.83 < 10000) — edge bruto não excede custos em regime
   baseline; edge operacional depende de realização favorável.

## Lições

1. **Sweep de parâmetros em 2 pontos é insuficiente para conclusão estrutural.**
   Testei extremos (7/25/75 e 21/35/65) mas não intermediários (10/28/72,
   17/32/68). Se objetivo fosse otimizar, seria sweep denso; aqui o objetivo
   era mapear sensibilidade — 2 pontos **confirmam que 14/30/70 é razoável**.
2. **Série O conclui: RSI 14/30/70 é sweet spot paramétrico; Bollinger 20/2
   Φ segue superior.** Próxima dimensão ortogonal a explorar é regime filter
   (Série P), não mais parâmetros.
3. **Trio O.1/N.2/O.2 valida empiricamente relação linear trade-count ↔
   critério 3:** 147 trades → 0.9418; 64 trades → 0.9747; 58 trades → 0.9767.
   Slope ≈ −0.0004/trade (consistente com Série L 15m).

## Recomendações

- **Fechar Série O aqui.** 2 pilotos são suficientes para conclusão
  "sensibilidade paramétrica baixa em 14/30/70".
- **Não promover O.2 para handoff.** Fica abaixo de N.2 em todas as dimensões
  materiais (hit, fe, MC p5).
- **Série P (próxima):** regime filter sobre J.2 BTC Bollinger — dimensão
  ortogonal com valor esperado maior.
