# AUDIT.md - AD.3

> Gate: **auditoria**.

## Hipótese × evidência

Hipótese: num_std=1.5 preserva edge OOS 2025 em ETH (generalizando AC.1).

**Resultado:** hit 62.62% > 45%; fe > 10000; ratio 0.9575 > 0.95 (marginal) — controle confirma 1.5 std tem edge em ETH sem filtro

## Comparação com AC.1

- AC.1 ETH 20/1.5+atr:105 2025: fe 10465 hit 64.15% 53 trades — **EDGE PRESERVED**
- AD.3 ETH: fe 10071.02 hit 62.62% 107 trades

**Implicação:** Controle: ETH sem filtro mantém edge mas ratio marginal.

## Blockers

Nenhum bloqueio técnico.

## Release

release_decision: `canary_only`

## ADR-0019

Stress fee+10 ≡ spread+10 = 9643.32. 1 nova confirmação.
