# 0095 — Ingest expansion: DOT/AVAX/LINK 1h + BTC/ETH/SOL 4h (desbloqueia CM/CN backlog)

**Status:** Accepted
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0005 (datasets manifest), ADR-0009 (ingest_binance_vision), Item 4 do plano de 2026-04-20

## Contexto

Stack approved cobre só BTC/ETH/SOL em 1h (cross-period 2024-H2 / 2025-H1 / 2025-H2). Séries de teste recentes (CU/CV/CW/CX) extraíram todo o edge extraível desse envelope:
- Padrão 20 (long-naked refutável) já tem 9 observações → regra operacional.
- Padrão 21 (breakout-naked refutável) fechou 9 runs adicionais.
- Meta-correlação (11 combos) mostrou nenhum r≥0.7 → stack bem diversificado **dentro** dos 3 ativos.

**Próximo eixo de teste natural:** expandir **ativos** (DOT/AVAX/LINK — altcoins L1/oracle) e **timeframes** (4h, menor ruído, mais sinal de trend).

Antes dessa expansão: verificar se ingest tooling ADR-0009 estava funcional (nem todos os scripts herdados estão). Confirmar.

## O que foi feito

### Checagem da tooling
- `scripts/ingest_binance_vision.py` (ADR-0009) é o ingest canônico: baixa ZIPs mensais de `data.binance.vision`, descompacta, valida gaps, grava Parquet em `data/processed/`, faz upsert no `data/datasets.yaml` com sha256+row_count+timezone.
- Smoke test: `python scripts/ingest_binance_vision.py --symbols DOTUSDT --timeframe 1h --start 2025-01-05 --end 2025-07-04` → OK, 4344 bars, sem gaps. Tooling **funcional sem modificação**.

### Datasets novos ingeridos
1h cross-period:
| Symbol | 2024-H2 | 2025-H1 | 2025-H2 |
|---|---|---|---|
| DOTUSDT | ✅ 4320 bars | ✅ 4344 bars | ✅ 4320 bars |
| AVAXUSDT | ✅ 4320 bars | ✅ 4344 bars | ✅ 4320 bars |
| LINKUSDT | ✅ 4320 bars | ✅ 4344 bars | ✅ 4320 bars |

4h janelas faltantes BTC/ETH/SOL:
| Symbol | 2025-H1 | 2025-H2 |
|---|---|---|
| BTCUSDT | ✅ 1086 bars | ✅ 1080 bars |
| ETHUSDT | ✅ 1086 bars | ✅ 1080 bars |
| SOLUSDT | ✅ 1086 bars | ✅ 1080 bars |

Zero gaps detectados em todos os 15 datasets novos. Todos sha256 registrados.

### Estado final do inventário
- Total datasets: **37** (antes: 22)
- BTC/ETH/SOL: 9 cada (1h × 3 janelas + 4h × 3 janelas + 15m × 1 janela onde aplicável)
- DOT/AVAX/LINK: 3 cada (1h × 3 janelas)
- Timeframes: 15m (3), 1h (25), 4h (9)

## Desbloqueios

### CM (cross-market expansion)
RSI short naked (perna v4b) foi testada só em BTC+SOL 2025-H2. Agora tem dataset para DOT+AVAX+LINK 2025-H2. Se PASS em ≥1, adiciona diversificação cross-asset sem nova engine.

### CN (timeframe expansion)
Todas as engines testadas em 1h. 4h cobre janelas BTC/ETH/SOL 2024-H2 + 2025-H1 + 2025-H2 agora completas. Hipótese: Bollinger/RSI em 4h tende a menos whipsaws e maior Sharpe por trade, mas menos trades → gate ≥30 pode ser apertado em 6 meses (1080 bars vs 4320 em 1h).

### CY (Donchian+filter rescue)
Padrão 21 (CX closeout) deixou CY em backlog. Não re-aberto agora — prioridade é explorar espaço novo antes de tentar rescue em engine refutada.

## Escolha: ordem de exploração

Após esse desbloqueio, 3 direções abertas em ordem natural:

1. **CM naked short em novos ativos (DOT/AVAX/LINK 2025-H2)** — hipótese mais barata (reuso direto de v4b engine, 3 runs, ~7min), testa Padrão 20 em universo ampliado.
2. **CN 4h BTC/ETH/SOL** (engines existentes re-testadas em 4h, 9-12 runs) — testa robustez de timeframe.
3. **CY Donchian+filter** (9-18 runs) — rescue engine refutada, probabilidade médio-baixa.

Recomendação: **CM primeiro** (menor custo, hipótese direta). Se CM PASS, amplia stack naturalmente. Se FAIL em 3/3 altcoins, Padrão 20 se fortalece cross-asset (é regra crypto major OU todo crypto?) e aí CN 4h seria o próximo salto de diversificação.

## Critério de sucesso desta ADR

1. ✅ Ingest tooling validada funcional sem modificação
2. ✅ 15 datasets novos adicionados ao manifest (9 altcoins 1h + 6 majors 4h)
3. ✅ Todos com sha256, row_count, zero gaps
4. ⏳ Próxima série (CM ou CN) usa esses datasets
5. ⏳ STATE.md atualizado (próximo)
