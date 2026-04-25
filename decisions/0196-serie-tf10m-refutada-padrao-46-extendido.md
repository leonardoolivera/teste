# 0196 — Série TF10m refutada + Padrão 46 extendido (intra-hour timeframes all refuted)

**Status:** Accepted
**Date:** 2026-04-21
**Deciders:** Usuário + agente
**Relates to:** ADR-0195 (pré-reg TF10m), ADR-0177/0178 (TF15m), ADR-0179 (TF30m), Padrão 46/47, ADR-0192 (autopilot Padrão 47 round 3)

## Contexto

Usuário redirecionou pós-autopilot-pausa-2 + ST refutado pedindo timeframe 10 minutos. Infra extendida: `TIMEFRAME_DELTAS` e `_TIMEFRAME` schema regex com `10m`, script novo `scripts/resample_timeframe.py` (5m→10m OHLCV, origin=epoch, label=left), ingestão de 5m ETH/SOL nas 3 janelas canônicas, 9 datasets 10m resampled adicionados ao manifest.

## Resultado TF10m (9 probes, BB+width 20/2.0 short, gate Sh≥1.5 AND trades≥30)

| Tag | Combo | Tr | Sh | PnL% | FE |
|---|---|---:|---:|---:|---:|
| TF10.1 | BTC 2024-H2 | 36 | 0.760 | +0.86 | 10086 |
| TF10.2 | ETH 2024-H2 | 60 | 1.276 | +2.12 | 10212 |
| **TF10.3** | **SOL 2024-H2** | **98** | **1.774** | **+4.99** | **10499** |
| TF10.4 | BTC 2025-H1 | 23 | -0.333 | -0.35 | 9965 |
| TF10.5 | ETH 2025-H1 | 85 | -1.974 | -5.67 | 9433 |
| TF10.6 | SOL 2025-H1 | 140 | -1.025 | -4.37 | 9563 |
| TF10.7 | BTC 2025-H2 | 15 | +0.145 | +0.19 | 10019 |
| TF10.8 | ETH 2025-H2 | 76 | -1.667 | -4.07 | 9593 |
| TF10.9 | SOL 2025-H2 | 114 | -1.530 | -4.79 | 9521 |

**Gate pass ≥2/9: 1/9 → FAIL.** Só TF10.3 (SOL 2024-H2) passa.

## Análise

**1 probe passa** (TF10.3 SOL 2024-H2 Sh=1.77) = Padrão 45 aplicado: outlier isolado, N=1 insuficiente para consolidar padrão. Consistência com ADR-0186 Padrão 48 candidato (SOL 2024-H2/2025-H1 = regime pyramid/BB-friendly) é sugestiva mas circunstancial — a janela é diferente (2024-H2 aqui vs 2025-H1 em PY) e engine idêntica (BB+width), então não adiciona evidência independente.

**5/9 com Sharpe negativo e ≥30 trades** (TF10.5, TF10.6, TF10.8, TF10.9 explicitamente; TF10.4 tem trades<30 e Sh<0). Todos em 2025. O padrão "2024-H2 = benigno, 2025-H1/H2 = hostil" replica o comportamento observado em TF30m/TF15m.

**3/9 trade count inadequado** (TF10.1=36, TF10.4=23, TF10.7=15): 10m é fast o bastante para emitir mais sinais em SOL (98-140 trades) mas em BTC fica abaixo do limiar, sugerindo que a vol regime-specific de BTC em 2024-H2/2025-H2 suprime entradas BB+width nesse TF.

## Extensão de Padrão

**Padrão 46 (ADR-0178) foi**: "BB+width short 15m cross-window refuta edge". **Extensão formal agora**: todo timeframe intra-hour testado (10m / 15m / 30m) com BB+width short **refuta edge cross-window cross-asset**.

- TF30m: 0/9 (ADR-0179)
- TF15m: 0/9 (ADR-0178)
- TF10m: 1/9 (ADR-0196, este — outlier Padrão 45)

Total intra-hour: **1/27 = 3.7% pass rate.** Um outlier SOL 2024-H2 não reverte a classificação — consistente com noise floor (sob H0 aleatório em gate `Sh≥1.5 AND N≥30`, esperaríamos ~2-5% pass rate).

**Hipótese operacional consolidada**: edge BB+width em crypto é um fenômeno de **1h sweet spot**. TFs menores destroem o edge (noise dominance + fee erosion relativa); TF maior (4h) destroem o edge por undertrading (Padrão 44, ADR-0096). Não há evidência para testar 5m / 1m — prior ~0 dado o gradiente 30m→15m→10m todos refutados.

## Decisão

1. **TF10m refutado**: arquivamento da frente "timeframes intra-hour alternativos".
2. **Padrão 46 extendido**: renomear escopo para "intra-hour timeframe refutado" (cobrindo 10m/15m/30m).
3. **Infra 10m preservada**: `TIMEFRAME_DELTAS`, schema regex, `scripts/resample_timeframe.py` ficam. Reativável custo-zero se aparecer nova hipótese (ex: portfolio intraday ou microstructure).
4. **9 datasets 10m resampled preservados** em manifest (custo baixo em disco, regeneráveis do 5m). `data/processed/{BTC,ETH,SOL}USDT/10m/` e entradas `*_resampled` em `datasets.yaml`.
5. **Stack 13 combos v3 inalterado.** Nenhum export. Nenhum manifest emitido.
6. **Autopilot**: **não retoma automaticamente.** Este foi um redirect explícito do user (10m timeframe), não continuação de autopilot. Retomada requer novo input — opções residuais em ADR-0183 (portfolio/cross-sectional, microstructure, 5m ultra-fast, aceitar stack).

## Diagnóstico do outlier SOL 2024-H2 (TF10.3)

Sharpe 1.77 com 98 trades, PnL +5% em 6 meses OOS. Possíveis causas não-mutuamente-exclusivas:
- Regime SOL 2024-H2 teve consolidações frequentes de curto prazo que 10m capta e 30m/15m perdem (timing-específico).
- Volatilidade realizada de SOL no período permitiu BB bands expandirem o suficiente para width-filter acionar sem abafar sinais.
- Random — 1 em 9 ≈ 11% é dentro da distribuição null.

**Decisão de não-ação**: não promover, não investigar mais (custo de confirmação ≥ 9 runs adicionais em asset×window variados; prior muito baixo dado 0/9 em outros ativos). Registrado como **Padrão 45** (outlier isolado).

## Total padrões: 47 (46 extendido, 48 candidato/SOL-2025-H1, 49 candidato/composite-MR, sem consolidação).
