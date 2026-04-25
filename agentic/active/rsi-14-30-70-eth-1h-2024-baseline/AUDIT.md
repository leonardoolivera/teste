# AUDIT.md — N.3 RSI 14/30/70 ETH 1h 2024

release_decision: canary_only

## release_decision

**`canary_only`** — 31º piloto do protocolo. Fecha Série N 3/3 canary_only.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------: | ------ |
| Critério 1: hit_rate baseline ≥ 45%     |    69.33% |     OK |
| Critério 2: max_drawdown ≤ 35%          |     5.71% |     OK |
| Critério 3: spread+10 / baseline ≥ 0.95 |     0.970 |     OK |

## Blockers

`canary-trade` inexistente.

## Findings

1. **Hit rate 69.33% é o maior do trio N** (vs N.1 58.73%, N.2 67.19%). ETH
   é o asset onde RSI **supera Bollinger em hit** (J.3 ~66%). Mas fe ETH < J.3.
2. **Edge-por-trade RSI < Bollinger em ETH:** hit superior não compensa que
   cada trade ETH RSI perde ligeiramente mais do que ETH Bollinger. Custo fixo
   por trade (10 bps ida+volta) domina a diferença.
3. **Série N fecha 3/3 canary_only.** Duas famílias MR independentes, 3 assets
   cada, 6 pilotos no total, 6/6 cruzam hard gate. Edge MR @ 1h **está
   estruturalmente estabelecido** no regime 2024-H2.
4. **ADR-0019 31ª confirmação** (`fee+10 ≡ spread+10 = 9600.61`).
5. **Fold 4 hit=82.35%** — entre maiores hits por fold RSI do protocolo.
6. **Margem spread mais apertada do trio N (0.9697).** ETH + RSI é combinação
   mais custo-sensível, ainda assim acima do threshold.

## Lições

1. **Hit ≠ fe sob custos.** ETH mostra que uma família pode ter hit superior a
   outra no mesmo asset (+3 pp) e mesmo assim perder em fe, pois o custo por
   trade é fixo e o edge por trade RSI é menor. Lição para Série O (sweep):
   otimizar por hit é armadilha — otimizar por fe líquido.
2. **Série N completa valida ADR-0027.** SMA smoothing vs Wilder EMA não é
   limitação: três pilotos independentes passam. RSI 14/30/70 não é degenerado.
3. **Próximo teste discriminativo é parametrização, não família.** Após 6/6
   MR @ 1h cross-família validados, próximo corte natural é sweep de parâmetros
   (Série O) sobre melhor asset (BTC, por N.2 + J.2).

## Recomendações

- **Fechar Série N aqui.** 3/3 cross-asset é evidência suficiente de estrutura.
- **Re-ranquear (rank N=31)** para ver posição RSI vs Bollinger em composite
  score (ADR-0024).
- **Abrir Série O: sweep RSI em BTC 2024** com 3–4 configurações de
  (`period, oversold, overbought`) para mapear sensibilidade de edge.
- **Handoff BotBinance segue priorizando J.2 Bollinger BTC** — domina N.2 em
  fe/hit/trades. RSI só compete se Série O achar parametrização superior.
