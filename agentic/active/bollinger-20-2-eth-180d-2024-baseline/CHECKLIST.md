# CHECKLIST.md — J.3 Bollinger 20/2 ETH 180d 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (6º do protocolo; fecha trio Série J 3/3).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-eth-180d-2024-baseline/`.

## Invariantes

- [x] ADR-0019 18ª confirmação (`fee+10 ≡ spread+10 = 9637.58`).
- [x] ADR-0010 monotonicity.

## Ranking

- [ ] Rank pendente rerun N=18.
- [x] Hit=71.76% (máximo do protocolo); fold_min=62.50%; fold_max=83.33%.

## Release

- [x] `canary_only` registrado.
- [ ] Handoff BotBinance: **J.2 BTC 2024 candidato primário** (maior perfil risco/retorno).
