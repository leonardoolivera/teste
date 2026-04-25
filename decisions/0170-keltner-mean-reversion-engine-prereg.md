# 0170 — Keltner mean-reversion engine: pré-registro + implementação

**Status:** Pre-registered — implementação autorizada "piloto automático".
**Date:** 2026-04-20
**Deciders:** Usuário ("vai no piloto automatico até ter uma estrategia que de para mandar para o nosso bot binance") + agente
**Relates to:** ADR-0169 (assessment), ADR-0026 (Bollinger canônico), ADR-0051 (short side), Padrão 42 (eixos sensibilizados), Padrão 43 (asset > filter > engine)

## Motivação

ADR-0169 avaliou 5 candidatos a novos engines; Candidato C (ATR/Keltner) é o único com **hipótese estrutural diferenciável** sem mudança arquitetural:

- Bollinger usa **desvio padrão** sobre closes → sensível a outliers (spikes).
- Keltner usa **ATR** (média de true range) → robusto a outliers, captura volatilidade baseada em range.
- Em regimes com flash crashes / spikes discretos, BB "infla" bandas temporariamente; Keltner mantém envelope estável.

Prior: correlação com BB ~+0.7. Payoff baixo-médio mas é a única hipótese diferenciável. Custo ~120 linhas engine + 150 linhas wiring CLI + testes.

## Hipótese testável

**H0**: Keltner não diferencia de BB → corr >+0.85 com BB em mesmos combos, Sh similar (± 0.3).
**H1**: Keltner adiciona dimensão → corr <+0.7, Sh diferenciado em ≥1 asset.

## Design do engine (causal, ADR-0030 friendly)

Inspirado em BB ADR-0026 para manter simetria long/short:

### Entrada

Dado `closes = window["close"].iloc[:-1]` e `highs`, `lows` alinhados:

- `tr[i] = max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))`
- `atr_now` = média simples de `tr` nas últimas `atr_period` barras (Wilder smoothing é legal mas usamos SMA para paridade com BB)
- `ema_now` = EMA sobre `closes` com span=`ema_window`
- `upper_now = ema_now + atr_mult × atr_now`
- `lower_now = ema_now - atr_mult × atr_now`

Mesma computação para `_prev` (janela shift -1).

### Sinais (edge-triggered, simétrico com BB)

- **Long entry**: `c[t-1] < lower_now AND c[t-2] >= lower_prev`
- **Short entry** (`long_only=False`): `c[t-1] > upper_now AND c[t-2] <= upper_prev`
- **Exit long-only**: `c[t-1] >= ema_now AND c[t-2] < ema_prev`
- **Reverse-on-signal** em `long_only=False` (ADR-0012/0051)
- Warm-up: HOLD enquanto `len(window) < max(ema_window, atr_period) + 3`

### Defaults canônicos (1-knob pesquisa)

- `ema_window=20` (paridade com BB short canônico)
- `atr_period=14` (RSI-like clássico)
- `atr_mult=2.0` (paridade com BB ns=2.0)

## CLI

Flags novas:
- `--keltner-window` (int, default 20): span EMA
- `--keltner-atr-period` (int, default 14)
- `--keltner-mult` (float, default 2.0)

`AVAILABLE_STRATEGIES` += `"keltner"`.

## Probes (Fase 1: 3 runs)

Alinhado com baseline BB short (CZ canônicos):

| Tag | Combo | Dataset | Baseline BB Sh |
|---|---|---|---:|
| KE.1 | Keltner 20/14/2.0 short | BTC 2025-H1 | 0.85 (bol short canônico) |
| KE.2 | Keltner 20/14/2.0 short | ETH 2025-H1 | 0.68 |
| KE.3 | Keltner 20/14/2.0 short | SOL 2025-H1 | 1.44 |

RSI/BB short 2025-H1 são mais fortes que long — escolher short por ter mais stack ativo para comparação.

## Gate pré-registrado

- **Upgrade convergente**: ≥2/3 Sh ≥ 1.5 AND trades ≥ 30 → Fase 2 (cross-window 2025-H2)
- **Signal divergente (Padrão 41)**: 1/3 Sh ≥ 1.5 → bloqueia, arquiva Keltner naked
- **Refutação**: 0/3 ≥ 1.0 → arquivar engine

Se Keltner passa Fase 1, Fase 2 cross-window H2 com mesmos 3 combos. Gate: ≥2/3 Sh≥1.0 AND mean lift vs BB > +0.2.

Se Fase 2 passa, Fase 3: cross-era 2024-H2 (Padrão 40) + meta-análise correlação vs BB em mesmos assets. Gate corr < +0.7 para promoção.

## Non-targets (compromisso de escopo)

- Não testar múltiplos `atr_mult` (1.5, 2.5) em Fase 1 — foco 1-knob
- Não testar EMA vs SMA — EMA default, mudança é ADR separado
- Não testar filtros compostos nesta série — pure engine comparison primeiro
- Não modificar BB engine

## Critério de handoff ao bot (objetivo final)

Caminho para manifest:
1. Keltner passa Fase 1 (3/3 probes)
2. Keltner passa Fase 2 (cross-window)
3. Keltner passa Fase 3 (cross-era)
4. Meta-análise correlação: adiciona diversificação real
5. Manifest v6.2 inclui combo(s) Keltner com gate export ADR-0030 (sharpe≥1.0, MDD≤20%, trades≥30, OOS clean)

Se falhar em qualquer fase → arquivar, reavaliar próximo candidato (A: zscore, D: cross-sectional, ou pausar).

## Implementação

Ordem:
1. `src/alpha_forge/strategies/families/keltner/strategy.py` + `__init__.py`
2. Wiring CLI em `src/alpha_forge/cli/app.py`
3. Testes unitários `tests/unit/test_keltner_strategy.py`
4. Smoke test via `alpha-forge run-demo --strategy keltner`
5. Probe script `tools/run_ke_sweep.py`
6. ADR-0171 closeout Fase 1

## Não-alvo administrativo

- Não editar manifest antes de handoff aprovado
- Não skipar testes (AGENTS.md §6)
- Não mudar signature de `Strategy.decide` (trabalho só em `decide`)
