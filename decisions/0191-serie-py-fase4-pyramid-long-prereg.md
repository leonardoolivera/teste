# 0191 — Série PY Fase 4 pré-reg: pyramid long-side em BB long + width proven

**Status:** Proposed
**Date:** 2026-04-21
**Deciders:** Usuário ("faz o que achar melhor") + agente
**Relates to:** ADR-0180 (v4 spec + amendment #10), ADR-0186/0188 (PY short refutado), ADR-0028 (BB long + width aprovado)

## Contexto

ADR-0188 refutou pyramid short-side cross-engine. ADR-0186 §"Próxima frente candidata" item 3 sugeriu pyramid long-side como frontier orthogonal remanescente. Hipótese user original (ADR-0186): "pyramid long é menos propenso a blowup que short em crypto (caudas longas limitadas pelo zero, short cauda infinita)".

Último frontier cheap. Se falhar, Padrão 47 round 3 formal + stop autopilot + snapshot handoff-ready round 2.

## Baselines (do manifest `bollinger_width_regime_20260418.json`)

BB long config canônica: `window=30, num_std=1.5, long_only=true, filter bollinger_width:30:1.5:250`.

| Combo | Sh baseline | PnL% | Trades |
|---|---:|---:|---:|
| ETH 2024-H2 BB+w | 1.834 | 4.68 | 38 |
| BTC 2024-H2 BB+w | 1.559 | 2.24 | 30 |
| SOL 2024-H2 BB+w | 2.401 | 8.01 | 69 |

Baselines Sh 1.56-2.40: faixa **middling** (mesma onde PY.1 e PY.4 passaram gate mínimo com pyramid). Prior Padrão 48-insight: ~30-40% de passar gate mínimo em ≥1/3, ~20% em ≥2/3.

## Probes

| Tag | Combo | Config |
|---|---|---|
| PY.8 | BTC 2024-H2 BB long 30/1.5 + width + pyr 2× | long_only=true |
| PY.9 | ETH 2024-H2 idem | long_only=true |
| PY.10 | SOL 2024-H2 idem | long_only=true |

**Regime filter**: `bollinger_width:window=30:num_std=1.5:min_width_bps=250`.
**Pyramid**: `max_tranches=5`, `tranche_equity_frac=0.20`, `rearm_cooldown=1`, `leverage=2.0`.
**Validação**: `--n-folds 3 --scheme rolling --train-fraction 0.5 --min-test-bars 50 --mc-resamples 1000`.

## Gate pré-registrado

### Fase 4 pass (promoção manifest v4 long-pyramid):
- ≥2/3 pass Sh≥1.5 AND seqs≥10 AND Sh ≥ 0.9 × baseline

### Fase 4 pass fraco (observação, sem promoção):
- ≥2/3 pass Sh≥1.5 AND seqs≥10 (sem edge preservation)

### Fase 4 refutada:
- 0/3 ou 1/3 pass gate mínimo

## Outcomes pré-registrados

**Pass forte (≥2/3 com edge preservation)**: ADR-0192 promoção. Implementar `manifest_v4.schema.json` e emitir primeiro manifest v4. Notificar bot via bridge com urgência (v4 implementation requerido).

**Pass fraco (≥2/3 min, 0/3 edge)**: Observação documentada. Não promover. Trade-off Sharpe vs PnL conhecido. Stack 13 inalterado. Snapshot round 2.

**Refutada (0/3 ou 1/3 min)**: Pyramid definitivamente arquivado (todas variantes testadas). Padrão 47 round 3 formal. Snapshot round 2. Stop autopilot.

## Hipótese long-side específica

1. **Cauda long vs short**: em crypto, pullbacks em uptrend têm magnitude limitada (asset não vai a zero rapidamente em 1h); pullbacks em downtrend (short context) podem explodir ao upside (short squeeze). Pyramid long acumula em pullback, short acumula em rally — rally expansions são mais extremas em crypto 1h.

2. **Baseline middling**: todos 3 baselines em faixa 1.56-2.40. Se degradação pyramid é função linear de baseline (ADR-0188 insight), degradação esperada 19-31% → Sharpe final esperado ~1.1-1.9. Gate mínimo 1.5 → algumas combos passarão, outras cairão.

3. **2024-H2 diferente de 2025-H1**: Padrão 45 consolidado, ETH/SOL ambos têm edge em 2024-H2 mas perfis diferentes de 2025. Pyramid pode reagir diferente.

## Não-alvo

- Não testar em outros windows (2025-H1, 2025-H2) nesta fase — 2024-H2 é onde baselines foram consolidados via ADR-0028.
- Não variar leverage (fica em 2× conforme padrão PY).
- Não testar short + long simultâneo (fora de escopo).

## Ação

1. `run_py4_sweep.py` + `summarize_py4.py`
2. 3 runs PY.8-10
3. ADR-0192 closeout (promoção ou refutação)
4. STATE.md update
5. Se refutação → ADR-0193 snapshot round 2 + bridge post final
