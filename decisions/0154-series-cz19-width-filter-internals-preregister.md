# 0154 — Série CZ19 pré-registro: width filter internals (num_std + window) sensibilidade

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário ("só vai, proxima") + agente escolheu B
**Relates to:** ADR-0151 (CZ17 threshold), Padrão 42 (ordem: bounds > window > threshold > internals), Padrão 41

## Motivação

Filter `bollinger_width` tem 3 params internos: `window`, `num_std`, `min_width_bps`. CZ17 varreu threshold (0/6 refutação). Falta internals (w + ns) — Padrão 42 classifica como prioridade 4 (mais baixa), mas nunca testado e canônicos sempre ns=1.5/w=30.

Predição Padrão 42: superfície deve ser ainda mais plana que CZ17 threshold (filter internals = segunda ordem da segunda ordem). Ótimo local canônico esperado.

## Escopo

3 combos top × 2 variantes em UM internal (num_std) = 6 runs. Fixo w=30 interno; se num_std refutar, window interno não vale testar separadamente (mesma família).

| Tag | Combo | Janela | filter ns interno |
|---|---|---|---:|
| CZ19.1 | SOL short ns=1.5 w=20 | 2025-H1 | 1.0 |
| CZ19.2 | SOL short ns=1.5 w=20 | 2025-H1 | 2.0 |
| CZ19.3 | ETH short ns=1.5 w=20 | 2025-H1 | 1.0 |
| CZ19.4 | ETH short ns=1.5 w=20 | 2025-H1 | 2.0 |
| CZ19.5 | SOL long ns=1.5 w=30 | 2024-H2 | 1.0 |
| CZ19.6 | SOL long ns=1.5 w=30 | 2024-H2 | 2.0 |

Mantém: engine ns=1.5 w=20/30, threshold bps=300/250, filter w=30 interno. Apenas varia filter `num_std` interno (1.0 captura bandas mais estreitas = mais regimes passam; 2.0 mais largas = menos regimes).

## Gate pré-registrado

- **Upgrade convergente**: ≥2/6 lift > 0.5 → CZ20 cross-window
- **Signal divergente**: 1/6 lift > 0.5 → Padrão 41 bloqueia
- **Refutação screening**: 0/6 lift ≥ 0.5 → Padrão 42 confirmado (internals segunda ordem robustos), arquivar

Timebox: ~5min. Closeout em ADR-0155.

## Não-alvo

- Não variar filter window interno (segunda ordem da segunda ordem; se ns refutar, prior de w também não vale)
- Não tocar threshold (CZ17 já cobriu)
- Não tocar engine params
