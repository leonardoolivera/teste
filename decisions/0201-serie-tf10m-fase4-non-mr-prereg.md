# 0201 — Série TF10m Fase 4 pré-reg: non-MR strategies em 10m (ma_crossover, donchian, supertrend)

**Status:** Accepted — probe em execução
**Date:** 2026-04-21
**Deciders:** Usuário ("testa outras coisas no 10 min") + agente
**Relates to:** ADR-0200 (Fase 3 closeout + Padrão 48), ADR-0008 (ma_crossover), ADR-0011 (donchian), ADR-0193 (supertrend)

## Motivação

Após Fase 3 refutada cobrir MR cross-engine em 10m (Padrão 46 escopo final), user pediu **testar outras coisas no 10m**. Engines non-MR disponíveis no alpha_forge:

| Strategy | Tipo | Status histórico | Canonical params |
|---|---|---|---|
| ma_crossover | trend-following | ADR-0008, stack legacy | short=20, long=50 |
| donchian | breakout | ADR-0011, refutado genericamente | entry=20, exit=10 |
| supertrend | trend-following ATR | ADR-0193, refutado | atr_period=10, atr_mult=3.0 |

Total: 9 + 9 + 9 = **27 probes**.

**Nota de escopo**: Padrão 46 é específico de MR intra-hour. Non-MR não herda a refutação. Porém trend-following tipicamente falha em TFs pequenos (noise > trend), então prior permanece baixo — mas valor informacional alto dado gap na cobertura.

## Decisão (pré-reg)

### Bloco I — ma_crossover 10m (TF10I.1-9)
- `--strategy ma_crossover --long-only --short-window 20 --long-window 50`
- BTC/ETH/SOL × 2024-H2 / 2025-H1 / 2025-H2
- Long-only (canonical trend-following; shorting crossover é divergente e não-stack).

### Bloco J — donchian 10m (TF10J.1-9)
- `--strategy donchian --long-only --entry-window 20 --exit-window 10`
- BTC/ETH/SOL × 2024-H2 / 2025-H1 / 2025-H2
- Long-only breakout canonical (ADR-0011).

### Bloco K — supertrend 10m (TF10K.1-9)
- `--strategy supertrend --no-long-only --supertrend-atr-period 10 --supertrend-atr-mult 3.0`
- BTC/ETH/SOL × 2024-H2 / 2025-H1 / 2025-H2
- Bidirectional (supertrend canonical flipa long/short; ADR-0193).

Config comum: capital=10k, fracao=0.1, alavancagem=2, fees=5bps, slippage=2bps/notional, folds=5 rolling, train=0.5, MC=1000 seed=42, stress fee+10 e spread+10. Sem regime filter (naked baseline).

Annualização Sharpe: `sqrt(144 × 365) ≈ 229.25`.

## Gate

**Gate por bloco**: ≥2/9 `annual_sharpe ≥ 1.5 AND trades ≥ 30`.

**Gate agregado Fase 4**: ≥2/27 probes passing.

**Gate alpha-vs-B&H**: para qualquer passer, computar B&H comparável (mesma asset+window) e exigir `pnl_pct_probe > pnl_pct_bh / alavancagem` para promoção real. Lembrete ADR-0200 note: TF10H.3 SOL 2024-H2 +10% alavancado 2x = alfa negativa vs SOL +46% naked B&H. **Alfa < B&H/leverage = não é edge real**.

## Decisão condicional

- **Algum bloco ≥2/9 AND alfa > B&H/leverage**: promove engine para validação cross-era 10m densa.
- **Algum bloco ≥2/9 AND alfa ≤ B&H/leverage**: registra pattern ("regime-bound não-alfa"), closeout bloco.
- **Todos blocos 0-1/N**: refutação non-MR 10m; frente TF10m cobertura total (MR + non-MR) exauridazgewcz. Arquivamento definitivo.
- **Passers clusterizados em SOL 2024-H2**: mais uma evidência Padrão 48 (regime window), não engine edge.

## Prior

**Pessimista-moderado.** Trend-following em 10m tipicamente falha (noise > signal no curto prazo; whipsaws destruidores). MA crossover 20/50 pode gerar trades demais em 10m. Donchian breakout 20/10 similar. Supertrend com atr_mult=3.0 mais restritivo, talvez trade count decente.

- Prior bloco individual ≥2/9: **~8-12%**.
- Prior agregado Fase 4 ≥2/27: **~20%**.
- Prior passers concentrarem SOL 2024-H2: **~30-40% condicional** (dado 4/4 prior em MR — mas non-MR pode ter padrão diferente).
- Prior de alfa > B&H/leverage em qualquer passer: **~5%** (crypto 2024-H2 foi bull forte).

Valor informacional: fecha frente TF10m com cobertura ≥8 engines (5 MR + 3 non-MR), decisão completa sobre 10m viabilidade.

## Integrity guard

- Mesmos 9 datasets 10m resampled (ADR-0196).
- Invariantes runtime (open@t+1, fixed_notional, exit_wins_on_tie).
- Engines ma_crossover/donchian/supertrend já existem — sem infra nova.

## Não-alvo

- Não tunar params engine-specific pré-probe.
- Não adicionar regime filter (naked baseline vs ADR-0008/0011/0193).
- Não testar short-only ma_crossover ou donchian (canonical é long-only).
- Não rodar 5m/1m.
