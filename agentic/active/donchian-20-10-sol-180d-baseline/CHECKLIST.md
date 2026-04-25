# CHECKLIST.md — H.10 Donchian 20/10 SOL 180d

## Gates (pesquisa → implementação → validação → backtest → auditoria)

ADR-0020 estrito. `release_decision: fail` por critério 1; corroboração (fold máx > 45%) passa via fold 0 = 47.62%.

## Artefatos

- [x] 6 .md + 4 .json.

## Invariantes

- [x] ADR-0019 12ª confirmação (`fee+10 ≡ spread+10 = 8709.91`).
- [x] ADR-0010 monotonicity.
- [x] Cross-asset compare contra H.1 BTC possível (2 flags diff esperado).
