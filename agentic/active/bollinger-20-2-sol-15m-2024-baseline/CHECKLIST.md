# CHECKLIST.md — L.1 Bollinger 20/2 SOL 15m 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: fail` (primeiro `fail` do protocolo; 23º piloto).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-sol-15m-2024-baseline/`.
- [x] Dataset 15m 2024-H2 ingerido (`solusdt_15m_20240705_20241231_binance_spot`, sha256=`589d8165`).
- [x] `TIMEFRAME_DELTAS` estendido com `15m` e `30m` (suíte preservada 337 passed).

## Invariantes

- [x] ADR-0019 23ª confirmação (`fee+10 ≡ spread+10 = 9088.47`).
- [x] ADR-0010 monotonicity.
- [x] ADR-0026 causalidade preservada (mesma implementação de I.1/J.1).

## Release

- [x] `fail` registrado — critério 3 de ADR-0025 violado (spread+10/baseline=0.871 < 0.95).
- [x] Primeiro `fail` operacional do protocolo após 22 pilotos (10 `canary_only` + 12 `rejected`).
- [ ] Não candidato a handoff. Migração 15m formalmente refutada.
- [ ] Série M pendente (Bollinger 4h ou RSI mean-reversion 1h).
