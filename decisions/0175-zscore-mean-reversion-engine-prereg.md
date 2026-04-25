# 0175 — Série ZS (zscore MR) engine + pré-reg Fase 1

**Status:** Accepted — engine implementado, probe Fase 1 em execução
**Date:** 2026-04-20
**Deciders:** Usuário (piloto automático) + agente
**Relates to:** ADR-0169 (candidatos lista), ADR-0174 (Keltner closeout → próximo)

## Motivação

ADR-0169 listou zscore MR como **Candidato A** para próxima família após BB/RSI/Donchian/MA-X/Keltner.
Prior declarado em 0169: **90% redundante com Bollinger**, mas existem 2 diferenças estruturais
não-testadas que justificam probe barato antes de arquivar:

1. **Semântica de threshold discreta** — Bollinger compara `close` vs `mean ± k·σ` (banda absoluta);
   zscore compara `z = (close-μ)/σ` vs `±k` (dimensão normalizada).
   Matemática equivalente em regime estacionário. **Diferente** quando σ varia bar-a-bar
   (não é a mesma decisão edge-triggered em transições).
2. **Exit em zero-crossing** vs exit em volta à banda — Bollinger ADR-0026 sai em `close >= mean`
   (i.e., cruza a banda central). zscore sai em `z cruza 0`. Em janelas curtas, `mean` do close
   e `z=0` divergem ligeiramente — o exit timing **não** é idêntico.

## Decisão

Implementar `src/alpha_forge/strategies/families/zscore/strategy.py`:

- `ZScoreMeanReversionStrategy(window, threshold, long_only=True)`
- `z_now = (c[t-1] - μ_now) / σ_now`, `z_prev = (c[t-2] - μ_prev) / σ_prev`
- Entry long edge-triggered: `z_now < -threshold AND z_prev >= -threshold`
- Entry short analog (se `long_only=False`)
- Exit long-only: **zero-crossing** — `z_now >= 0 AND z_prev < 0`
- Simultaneidade long+short → HOLD
- Warm-up: `len(window) < window_size + 3` → HOLD
- sigma=0 → HOLD (degenerado)

CLI wiring: `--strategy zscore --zscore-window 20 --zscore-threshold 2.0`.

19 unit tests (param validation, warm-up, sinais, causalidade, statelessness, sigma=0).

## Pré-registro probe Fase 1

Mesma forma canônica Padrão 41 que KE/DE:

- **Datasets:** `btc-usdt-1h-2025-h1`, `eth-usdt-1h-2025-h1`, `sol-usdt-1h-2025-h1`
- **Params:** `--zscore-window 20 --zscore-threshold 2.0 --no-long-only`
- **Budget:** capital 10000, fração 0.10 notional, alavancagem 5
- **Custos:** taker 10bps, spread 10bps, slippage 0
- **Stress:** `fee+10:10:0:0` e `spread+10:0:0:10`
- **Folds:** 5 expanding, train 0.7
- **MC:** 1000 resamples, seed 42

**Gate:** Padrão 41 — ≥2/3 `annual_sharpe ≥ 1.5 AND trades ≥ 30`.

## Decisão condicional (piloto automático — ADR feedback memory)

- **Se pass (≥2/3):** cross-window H2 automática + cross-era 2024-H2 + gate Padrão 43 de diversificação;
  se tudo passar, **export manifest direto** para handoff BotBinance. Sem pausa.
- **Se fail:** ADR closeout zscore, Candidato A arquivado, avançar para:
  1. Revisitar hipóteses vivas com filtros composição (BB+RSI, BB+Keltner),
  2. Mudança de escopo (cross-sectional, portfolio spread),
  3. Pausa e STATE.md status "pesquisa exaurida frentes atuais" se esgotado.

## Prior

**Pessimista.** Expectativa: 0-1/3 pass (redundância com Bollinger → provavelmente mesma performance,
e BB 1h 2025-H1 já foi refutado fora de filtro específico). Probe serve para **eliminar** a
família, não para confirmar edge. Custo do probe: ~3min compute, 3 runs walk-forward.

## Não-alvo

- Não tunar window/threshold antes do probe cego
- Não assumir edge por analogia com Bollinger (testes independentes)
- Não testar 4h (lição ADR-0174: sparse por construção em 6 meses)
