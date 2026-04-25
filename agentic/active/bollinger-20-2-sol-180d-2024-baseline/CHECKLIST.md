# CHECKLIST.md — J.1 Bollinger 20/2 SOL 180d 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (primeiro da Série J; 4º do protocolo).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-sol-180d-2024-baseline/`.
- [x] Dataset 2024-H2 ingerido (`solusdt_1h_20240705_20241231_binance_spot`).

## Invariantes

- [x] ADR-0019 16ª confirmação (`fee+10 ≡ spread+10 = 10335.23`).
- [x] ADR-0010 monotonicity.
- [x] ADR-0026 causalidade (via property tests I.1).

## Ranking

- [ ] Rank pendente de J.2/J.3 + rerun ranking N=18.
- [x] fold_max=88.24%; fold_min=47.06%; 4/4 folds cruzam 45%.
- [x] MC p5=10046.92 (> capital inicial, primeiro do protocolo).

## Release

- [x] `canary_only` registrado.
- [ ] Execução bloqueada por `canary-trade` inexistente.
- [ ] Handoff BotBinance pendente de J.2/J.3 + OOS Sharpe + aprovação.
