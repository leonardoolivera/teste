# 0046 — Série CD: Donchian + TrendHTF cross-period — gate pré-registrado

**Status:** Accepted — gate pré-registrado antes da execução
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0043 (arquitetura trend_htf), ADR-0045 (closeout CC com hipótese forward).

## Context

Série CC (Bollinger mean-reversion + trend_htf) arquivada em ADR-0045: gate principal FAIL 0/9, gate de lift PASS 7/9. Leitura: `trend_htf` reduz risco mas não gera edge em mean-reversion, porque filtro de **trend** e estratégia de **contra-tendência** estão em tensão direcional.

Hipótese forward da ADR-0045:

> `trend_htf` combinado com estratégia **trend-following** (não mean-reversion) pode gerar edge aditivo, porque a direção do filtro se alinha com a da estratégia.

Série CD testa essa hipótese com **Donchian 20/10** (breakout puro trend-following, ADR-0011). Donchian falhou cross-period sozinho (Série CA, ADR-0040) pela razão oposta ao Bollinger: **perde em chop**. `trend_htf:long_only` filtraria barras chop (preço abaixo SMA 4h, tipicamente ranging ou bear) e deixaria apenas trades em contexto trend-up — exatamente onde Donchian breakout prospera.

**Calibração pré-experimento** (não-post-hoc, feita antes do gate): smoke Donchian 20/10 + trend_htf:4h:50:long em SOL 2025-H2 = **33 trades** (vs 16 no Bollinger com mesmo filtro). Donchian preserva trade count melhor que Bollinger sob o mesmo filtro — alinha com expectativa de que breakouts concentram em regime trend.

## Matriz (9 pilotos)

3 ativos × 3 recortes (2023-H2, 2025-H1, 2025-H2). Mesma matriz das Séries CB/CC para comparabilidade cruzada. 2024 pulado (já coberto pelos baselines históricos).

| Tag | Dataset |
|---|---|
| CD.1 | ETHUSDT 2023-H2 |
| CD.2 | BTCUSDT 2023-H2 |
| CD.3 | SOLUSDT 2023-H2 |
| CD.4 | ETHUSDT 2025-H1 |
| CD.5 | BTCUSDT 2025-H1 |
| CD.6 | SOLUSDT 2025-H1 |
| CD.7 | ETHUSDT 2025-H2 |
| CD.8 | BTCUSDT 2025-H2 |
| CD.9 | SOLUSDT 2025-H2 |

Engine fixo:
- `DonchianBreakoutStrategy(entry_window=20, exit_window=10, long_only=True)` — ADR-0011 defaults
- Regime filter: `trend_htf:htf=4h:sma_window=50:mode=long_only` (mesma parametrização da CC — ADR-0044 §escolha)
- Sem `atr_regime` composto aqui: **quero medir efeito isolado do trend_htf**, não efeito composto. Em CC o AND com atr_regime confundiu atribuição.
- Capital 10000, fracao 0.1, alavancagem 2.0
- Taker 5bps, slippage 2bps/notional, spread 0bps
- Walk-forward: n_folds=5, rolling, train_fraction=0.5, min_test_bars=50
- MC: 1000 resamples, seed=42
- Cost stress: `fee+10:10:0:0`, `spread+10:0:0:10`

## Gate pré-registrado (decisão)

**Gate 1-6 (sobrevivência do piloto)** — PASS se **todas** em **≥ 6 de 9** pilotos filtered:

1. `trades ≥ 30` — Donchian com trend_htf preservou 33 no smoke SOL 2025-H2; 30 é piso razoável
2. `Sharpe ≥ 1.0`
3. `MDD ≤ 20%`
4. `final_equity > 10000` — **gate mais apertado que CC** (era 9800). Justificativa: o teste da hipótese é "filtro gera edge aditivo", não "filtro preserva break-even". Se for break-even, é CC outra vez.
5. `cost_stress_ratio_min ≥ 0.95`
6. `MC p5 final_equity > 9500` — apertado vs CC (era 9200). Breakout com HTF alinhado deveria ter cauda melhor.

**Gate 7 (lift arquitetural)** — PASS se **em ≥ 6 de 9** pilotos: filtered tem `final_equity` maior **E** `mdd` menor que o baseline Donchian sem filtro.
- Exige **ambos** (vs CC que era "ou"): Donchian sem edge positivo isolado não deveria melhorar só em risk sem mover fe — lift genuíno precisa aparecer nos dois lados.

**Gate 8 (sanidade cross-estratégia)** — PASS se em pelo menos **2 de 3 recortes 2025**, Sharpe filtered é positivo. 2025 foi onde CC teve flips negativos dominantes; se trend_htf+Donchian também produz Sharpe negativo aí, a hipótese "alinhamento direcional resgata cross-period" é falsa.

**PASS GERAL DA SÉRIE** = (Gate 1-6 passa) **AND** (Gate 7 passa) **AND** (Gate 8 passa).

Os três gates são não-movíveis, conjuntos, e endereçam riscos distintos:
- Gate 1-6: é o piloto viável per se?
- Gate 7: o filtro adiciona valor arquitetural sobre baseline Donchian puro?
- Gate 8: a generalização cross-period está lá, especificamente nos recortes que mataram CC?

## Critério de rejeição limpa

- **Gate 1-6 FAIL**: arquiva Donchian + trend_htf; abre ADR-0047 closeout; não retunar.
- **Gate 1-6 PASS + Gate 7 FAIL**: arquiva como "filtro não adicionou valor, Donchian passaria sozinho nesse recorte" — mas consolida Donchian 20/10 como candidato manifest sem filtro.
- **Gate 1-6 PASS + Gate 7 PASS + Gate 8 FAIL**: "passa no agregado mas falha no recorte crítico" — ADR de closeout nuançada, série **não vai pra manifest** mas abre debate sobre regime-specific manifest.
- **Todos 3 PASS**: primeiro sucesso cross-period do projeto. Manifest + ADR de promoção + notificação bot via bridge.

## Timebox

1 dia. 18 runs (9 filtered + 9 baselines). Sem rescue intermediário — regra universal CA/CB/CC.

## Convenções de run_id

- Filtered: `cd-don-20-10-{asset}-{yyyymmdd_yyyymmdd}-htf4h50`
- Baseline: `cd-don-20-10-{asset}-{yyyymmdd_yyyymmdd}-baseline`

## Alternativas consideradas

- **Donchian 40/20 (mais conservador)**: rejeitado. 40/20 dobra warm-up e reduz trade count, arriscando trades <30 mesmo em breakout regime. 20/10 é o default ADR-0011 e mais parcimonioso.
- **Incluir atr_regime no AND**: rejeitado — motivo acima (atribuição de efeito). Se Série CD passar com trend_htf isolado, abrir CE pra confirmar se `and(trend_htf, atr_regime)` ainda melhora.
- **Testar `htf=1d`**: rejeitado pelo mesmo motivo CC ADR-0044 (recortes 180d → ~180 candles 1d, warmup come 1/3 do dataset).
- **`mode=both_sides`**: rejeitado — degenera em "sem filtro" com engine long-only.
- **Fracao dinâmica (2x quando filtro ativo)**: rejeitado nesta série. Fora do escopo AF atual; ADR separada se CD passar.

## Gate não-movível

Declarado antes de qualquer execução. Alteração futura exige ADR nova justificando inadequação — nunca edit deste arquivo.
