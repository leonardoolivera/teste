# 0207 — Governor de perdas (3/5/7-stop) no stack 13 — governor inerte

**Status:** Accepted (diagnóstico; governor não dispara no stack atual)
**Date:** 2026-04-22
**Deciders:** Usuário ("agora teste novamente mas usando a regra de gerenciamento, 3 stop diminui mao pra 50% no dia, 5 stop para o dia, 7 stop seguido para a semana") + agente
**Relates to:** ADR-0204 (pré-reg snowball), ADR-0205 (snowball closeout), ADR-0206 (fixed 100% closeout).

## Contexto

Após ADR-0206 (fixed_notional 100%/entrada, Sharpe ≈ baseline, PnL ~5×), user pediu aplicar **governor de perdas**:

- **3 perdas no dia** → sizing 50% pelo resto do dia.
- **5 perdas no dia** → bloqueio de novas entradas pelo resto do dia.
- **7 perdas consecutivas** (sem win entre elas) → bloqueio pelo resto da semana ISO.

"Perda" = trade fechado com `pnl < 0`. Engine não usa stop-loss (ADR-0030: `stop_loss: "disabled"`); EXIT vem da estratégia/regime filter. Trade skipado não conta para os contadores. Trade em half-size (50%) ainda conta como perda se pnl escalado < 0.

Implementação: replay do stream de trades do `run_backtest` (FIXED_NOTIONAL 100%/entrada) através de uma state machine com reset em **dia UTC** e **semana ISO** (segunda 00:00 UTC). Stream de trades é sizing-invariant (estratégia só lê preços), então factor ∈ {0, 0.5, 1.0} escala pnl linearmente.

Script: [`scripts/run_governor_stops_stack13.py`](../scripts/run_governor_stops_stack13.py). Artefato: [`exports/diag/governor_stops_stack13_20260422.json`](../exports/diag/governor_stops_stack13_20260422.json).

## Resultado principal

**Governor não dispara em nenhum dos 13 combos.** Em 13/13:

- `full_size` trades = 100% dos trades do baseline.
- `halved` = 0, `skipped_day` = 0, `skipped_week` = 0.
- PnL, Sharpe, MDD **idênticos** ao fixed_100 (ADR-0206 sizing B).

Diagnóstico do porquê (máximo de perdas por dia e maior streak consecutiva de perdas nos 13 combos):

| # | Combo | trades | losses | max L/dia | max consec L |
|---:|---|---:|---:|---:|---:|
| 1 | BB-long ETH 2024-H1 | 43 | 15 | 2 | 3 |
| 2 | BB-long ETH 2025-H1 | 54 | 13 | 1 | 3 |
| 3 | BB-long BTC 2024-H2 | 29 | 9 | 1 | 2 |
| 4 | BB-long SOL 2024-H2 | 66 | 16 | 1 | 3 |
| 5 | BB-bidir SOL 2024-H2 | 129 | 53 | 2 | 4 |
| 6 | BB-bidir BTC 2025-H1 | 59 | 24 | 1 | 4 |
| 7 | BB-bidir ETH 2025-H1 | 119 | 36 | 2 | 4 |
| 8 | BB-bidir SOL 2025-H1 | 139 | 55 | 2 | 5 |
| 9 | RSI-long ETH 2024-H2 | 40 | 15 | 2 | 3 |
| 10 | RSI-short BTC 2025-H2 | 118 | 41 | 1 | 6 |
| 11 | RSI-short SOL 2025-H2 | 108 | 40 | 1 | 3 |
| 12 | RSI-short trendhtf SOL 2025-H1 | 53 | 17 | 1 | 2 |
| 13 | RSI-short width BTC 2025-H1 | 58 | 29 | 1 | 5 |

- **Máx. perdas em qualquer dia único** ∈ {1, 2} em todos os combos. Threshold 3 **nunca atingido**.
- **Máx. streak consecutiva** = 6 (combo #10, BTC RSI-short 2025-H2). Threshold 7 **nunca atingido**.

## Interpretação

As regras do governor são desenhadas para **trading intraday de alta frequência** (scalping com dezenas de trades/dia). Nosso stack é **mean-reversion em 1h** com frequência baixa: 0.16–0.77 trades/dia em média. Em 6 meses o máximo de trades em qualquer dia único foi **2** (combos #1, #4, #5, #7-9). As regras são inertes neste perfil.

Cenários onde as regras disparariam:
- **Probes 5m/10m** (TF10m, ADR-0195-0202): 20-480 trades/6 meses → possivelmente >3 perdas/dia em dias adversos.
- **Stack futuro com scalping engine** (exotic/T4 do roadmap 1000): provável.
- **Aperto das regras para 1h**: ex. "3 perdas em 3 dias" ou "3 perdas consecutivas" (sem cláusula "no dia") bateriam em 10/13 combos.

## Consequences

- **Positive:** evidência de que o governor proposto **não afeta o stack atual** — nem para melhor nem para pior. PnL e risco são idênticos ao fixed_100. Se o user quisesse adotar essa política sem ajustes, o comportamento observado seria igual ao baseline.
- **Negative:** governor não oferece proteção mensurável neste regime de trade density. É proteção para cenário que não acontece.
- **Neutral:** infra de replay está construída e reutilizável para qualquer probe futuro, incluindo TF10m/5m onde o governor provavelmente dispararia.

## Alternatives considered

- **Aplicar sobre TF10m probes** (93 probes refutados em ADR-0195-0202): possível, mas todos refutados — não há manifest aprovado para aplicar. Skip.
- **Reescalar regras para 1h**: ex. `half_at=2, stop_day_at=3, stop_week_at_consec=5`. Efeito real, mas não foi o que user pediu. Registro aqui para referência futura; não rodado.
- **Regras sobre perdas por semana inteira** (não consecutivas): ortogonal. Se user quiser, implemento.
- **Governor em modo paper-trading real-time** (não backtest): fora de escopo AF; BotBinance teria que implementar.

## Follow-ups

- STATE.md atualizado.
- Nenhum handoff. Stack 13 inalterado. Manifests inalterados.
- Se user pedir governor mais apertado (ex. `half_at=2`), reusar [`run_governor_stops_stack13.py`](../scripts/run_governor_stops_stack13.py) ajustando as constantes no topo (`HALF_AT`, `STOP_DAY_AT`, `STOP_WEEK_AT`).
