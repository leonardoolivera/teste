# CHECKLIST.md — I.1 Bollinger 20/2 SOL 180d

## Gates (pesquisa → implementação → validação → backtest → auditoria)

ADR-0020 estrito. `release_decision: canary_only` (primeiro do protocolo).

## Artefatos

- [x] 6 .md (SPEC, IMPLEMENTATION, VALIDATION, BACKTEST, AUDIT, CHECKLIST).
- [x] 4 .json (run, walk_forward, monte_carlo, cost_stress) em
      `results/validation/bollinger-20-2-sol-180d-baseline/`.
- [x] leaderboard N=13 em `results/ranking/20260418T102235Z.json`.

## Invariantes

- [x] ADR-0019 13ª confirmação (`fee+10 ≡ spread+10 = 9859.11`). Primeira sobre mean-reversion.
- [x] ADR-0010 monotonicity — baseline > slip+5 > {fee+10, spread+10}.
- [x] ADR-0026 causalidade — property `test_bollinger_causal.py` verde em 100 examples.
- [x] ADR-0003 — MC seed=42 reprodutível; p5/p50/p95 persistidos.
- [x] Cross-family compare I.1 ↔ H.10 possível no mesmo dataset.

## Ranking

- [x] rank 1/13 (composite_score=7.66, +2.17 sobre rank 2).
- [x] fold_max=76.47% (fold 3); fold_min=50.00% (fold 2) — ambos > 45%.

## Release

- [x] `canary_only` registrado em AUDIT.md.
- [ ] Execução efetiva de canary bloqueada por ausência de módulo `canary-trade` (neutra, ADR-0005).
- [ ] Handoff BotBinance pendente de: (a) OOS Sharpe explícito; (b) aprovação do usuário.
