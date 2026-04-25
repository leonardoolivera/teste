# CHECKLIST.md — H.9 Donchian 20/10 ETH 180d + SMA

## Gates (pesquisa → implementação → validação → backtest → auditoria)

ADR-0020 estrito. `release_decision: fail` por critério 1 — primeiro piloto com fe > 10000.

## Artefatos

- [x] 6 .md + 4 .json.

## Invariantes

- [x] ADR-0019 11ª confirmação (`fee+10 ≡ spread+10 = 10119.56`, primeira com fe>10000).
- [x] ADR-0010 monotonicity.
- [x] Cross-asset compare H.3 ↔ H.9 = 2 flags diff.
