# 0070 — Série CI: Donchian short + BollingerWidthFilter min_width_bps=300 (pré-registro)

**Status:** Accepted — pré-registro; execução autorizada
**Date:** 2026-04-19
**Deciders:** Usuário + agente
**Relates to:** ADR-0057 (CG closeout PASS), ADR-0062 (CH closeout PASS), ADR-0068 (Padrão 12), ADR-0069 (v4a/v4b ativos), ADR-0040 (CA Donchian long FAIL — formato distinto, ver Diferenciação)

## Contexto

CG (Bollinger short + width 300) e CH (RSI short + width 300) passaram o gate cross-period (4/9 cada) e geraram manifests v3, v4a, v4b. Padrão 10 (filter composicional eleva edge borderline) confirmado em **2 famílias** mean-reversion (Bollinger e RSI) com filter de volatilidade (BollingerWidthFilter).

Pergunta aberta: **o padrão se estende a uma terceira família estruturalmente diferente (breakout)?** Donchian short é breakout reverso — short ao romper mínima recente. Sem filter, Donchian long FAIL em 2024+ (ADR-0040). Donchian short com width 300 testaria se filter compõe genericamente além da intuição mean-rev.

## Diferenciação vs Série CA (ADR-0039/0040)

CA testou **Donchian long-only** (breakout pra cima) com **ATR gate** (`min_atr_bps`). FAIL 2/10. Esta série CI inverte direção (**short**), troca filter (**BollingerWidthFilter** — mesmo da CG/CH em vez de ATR), e segue formato de 9 pilotos (não 10) cross-period como CG/CH. Não é re-execução de CA.

## Decisão

Espelhar CH para Donchian short. Mesmos 9 pilotos, mesmos parâmetros de engine. Deltas vs CH:
- `--strategy donchian` em vez de `rsi`
- `--donchian-window-entry 20 --donchian-window-exit 10` em vez de RSI params
- `--no-long-only` (mantido — habilita short)
- Filter `bollinger_width:window=30:num_std=1.5:min_width_bps=300` idêntico

### Matriz de pilotos (idêntica CG/CH)

9 pilotos: BTC/ETH/SOL × 2024-H2/2025-H1/2025-H2.

| Tag | Asset | Window | Dataset suffix |
|---|---|---|---|
| CI.1 | BTC | 2024-H2 | 20240705_20241231 |
| CI.2 | ETH | 2024-H2 | 20240705_20241231 |
| CI.3 | SOL | 2024-H2 | 20240705_20241231 |
| CI.4 | BTC | 2025-H1 | 20250105_20250704 |
| CI.5 | ETH | 2025-H1 | 20250105_20250704 |
| CI.6 | SOL | 2025-H1 | 20250105_20250704 |
| CI.7 | BTC | 2025-H2 | 20250705_20251231 |
| CI.8 | ETH | 2025-H2 | 20250705_20251231 |
| CI.9 | SOL | 2025-H2 | 20250705_20251231 |

### Parâmetros de engine (idênticos CH)

- capital 10000, fracao 0.1, alavancagem 2.0
- `--sizing-mode fixed_notional` (default explícito; ADR-0064 reforça)
- taker 5bps, slippage 2bps, spread 0
- n-folds 5, rolling, train_fraction 0.5, min_test_bars 50
- mc_resamples 1000, mc_seed 42
- stress `fee+10:10:0:0`, `spread+10:0:0:10`

### Gates pré-registrados (espelho CH)

- **Gate 1 — principal**: ≥ **3/9** passa critério manifest (trades≥30, Sharpe≥1.0, MDD≤20, MCp5>9500, cost_r≥0.95)
- **Gate 2 — lift cost_r vs CA Donchian long sem filter**: em ≥ **6/9** pilotos, CI cost_r > CA cost_r (proxy: CA não tinha filter; comparar contra runs CA equivalentes em 2024+ se existirem). Se filter não move cost_r pra cima em Donchian, refuta genericidade
- **Gate 3 — preservação de edge**: em ≥ **6/9** pilotos, CI Sharpe > 0 E trades ≥ 30
- **Gate 4 — falsificacionista**: em 2024-H2 bull (3 pilotos), **≤ 1/3 passa Gate 1**
- **Gate 5 (novo, Padrão 12)**: se Gate 1 PASS, audit Gate B obrigatório antes de promoção — re-rodar mesmos combos sem filter; promoção só se ≥3/N combos PASS confirmarem filter load-bearing

### Regras anti-movimento

Gates fixos. Não renegociáveis. Se 2/9 no Gate 1, FAIL.

## Hipóteses explícitas

1. **H-generalidade-breakout** (≥3/9 PASS): padrão 10 é genérico cross-família. Filter de volatilidade compõe com breakout direção-short. Donchian short capitaliza breakdown bear; width filtra falsos breakouts em chop seco.
2. **H-especificidade-mean-rev** (0-2/9 PASS): padrão 10 só funciona em mean-rev (Bollinger, RSI). Breakout precisa de regime trending, não filter de width.
3. **H-direção-importa** (3+/9 mas só em janela específica): Donchian short funciona em 2024-H2 (bear pós-bull) mas falha em 2025 misto. Replica achado CA invertido — direção contra dominante.

## Alternativas consideradas

### Donchian(10,5) ou (40,20) em vez de (20,10)
Rejeitado. Variar 2 eixos quebra falsificabilidade. CG/CH usaram parâmetros canônicos mean-rev — manter Donchian canônico (20,10) que CA usou.

### ATR filter em vez de width
Rejeitado. CA usou ATR e falhou. Quero testar especificamente se **width compõe com Donchian** — ATR seria confundido com replay de CA.

### Cross-timeframe 4h
Rejeitado por ora. Se CI passar 1h, 4h vira teste adicional. Se falhar 1h, 4h provavelmente também (menos trades, mesmo edge).

## Saída da série

- **Gate 1 PASS + Gate 4 PASS + Gate 5 PASS:** elegível para manifest v5 via ADR de promoção separada
- **Gate 1 PASS + Gate 5 FAIL:** filter não load-bearing em Donchian — interessante achado mas não promove (Padrão 12 bloqueia)
- **Gate 1 FAIL com Gate 2 PASS:** filter moveu cost_r mas edge insuficiente. Documenta filter generaliza parcial; pivot para outro formato
- **Gate 1 FAIL com Gate 2 FAIL:** filter não transfere para breakout. Padrão 10 é específico mean-rev. Arquivar Donchian short

## Tooling

- `tools/run_ci_sweep.py`: 9 runs, run_id `ci-donchian-20-10-<asset>-<suffix>-width30-300-short`
- Closeout: análise inline + ADR-0071 (espelho 0062)

## Timebox

~15-20min compute + ADR-0071 closeout mesmo dia se possível.

## Critério de sucesso desta ADR

1. 9 runs rodam sem crash
2. Métricas extraídas e gates avaliados com saída interpretável
3. ADR-0071 emitida com decisão (PASS → audit Gate B → promoção, ou FAIL → arquivar)
