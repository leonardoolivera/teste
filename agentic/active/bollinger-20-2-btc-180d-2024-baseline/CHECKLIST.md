# CHECKLIST.md — J.2 Bollinger 20/2 BTC 180d 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (5º do protocolo).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-btc-180d-2024-baseline/`.

## Invariantes

- [x] ADR-0019 17ª confirmação (`fee+10 ≡ spread+10 = 9911.98`).
- [x] ADR-0010 monotonicity.

## Ranking

- [ ] Rank pendente de rerun N=18 após J.3.
- [x] fold_max=72.73%; fold_min=64.71%; std=3.48 pp (**mínimo do protocolo**).

## Release

- [x] `canary_only` registrado.
- [ ] Handoff BotBinance: candidato primário (menor mdd + maior homogeneidade).
