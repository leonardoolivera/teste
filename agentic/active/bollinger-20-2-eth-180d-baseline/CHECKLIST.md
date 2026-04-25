# CHECKLIST.md — I.3 Bollinger 20/2 ETH 180d

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (terceiro do protocolo; trio completo).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-eth-180d-baseline/`.
- [x] leaderboard N=15 em `results/ranking/20260418T103335Z.json`.

## Invariantes

- [x] ADR-0019 15ª confirmação (`fee+10 ≡ spread+10 = 9729.39`).
- [x] ADR-0010 monotonicity.
- [x] ADR-0026 causalidade (via property tests I.1).

## Ranking

- [x] rank 3/15 (score 7.12); top-3 ocupado inteiramente por Bollinger I.1/I.2/I.3.
- [x] fold_max=73.33%; fold_min=50.00%; 4/4 folds cruzam 45%.

## Release

- [x] `canary_only` registrado.
- [ ] Execução bloqueada por `canary-trade` inexistente.
- [ ] Handoff BotBinance pendente de OOS Sharpe + aprovação.
