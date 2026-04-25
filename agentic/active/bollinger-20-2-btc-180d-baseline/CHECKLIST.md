# CHECKLIST.md — I.2 Bollinger 20/2 BTC 180d

## Gates (pesquisa → implementação → validação → backtest → auditoria)

ADR-0020 estrito. `release_decision: canary_only` (segundo do protocolo).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-btc-180d-baseline/`.
- [x] leaderboard N=15 em `results/ranking/20260418T103335Z.json`.

## Invariantes

- [x] ADR-0019 14ª confirmação (`fee+10 ≡ spread+10 = 9703.27`).
- [x] ADR-0010 monotonicity.
- [x] ADR-0026 causalidade (via property tests I.1).
- [x] Cross-asset compare I.1 ↔ I.2 possível no mesmo tape.

## Ranking

- [x] rank 1/15 (score 7.70).
- [x] fold_max=69.23%; fold_min=44.44% (marginalmente abaixo de 45%).

## Release

- [x] `canary_only` registrado.
- [ ] Execução efetiva bloqueada por ausência de módulo `canary-trade`.
- [ ] Handoff BotBinance pendente de OOS Sharpe + aprovação usuário.
