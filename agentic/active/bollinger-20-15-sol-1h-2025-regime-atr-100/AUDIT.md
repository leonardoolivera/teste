# AUDIT.md - AD.2

> Gate: **auditoria**.

## Hipótese × evidência

Hipótese: num_std=1.5 preserva edge OOS 2025 em SOL (generalizando AC.1).

**Resultado:** hit 46.67% > 45% OK; mdd 9% OK; ratio 0.9678 > 0.95 OK — mas fe < 10000 (perde capital)

## Comparação com AC.1

- AC.1 ETH 20/1.5+atr:105 2025: fe 10465 hit 64.15% 53 trades — **EDGE PRESERVED**
- AD.2 SOL: fe 9264.75 hit 46.67% 75 trades

**Implicação:** AC.1 é ETH-específico; 1.5 std não generaliza para SOL OOS.

## Blockers

Nenhum bloqueio técnico.

## Release

release_decision: `canary_only`

## ADR-0019

Stress fee+10 ≡ spread+10 = 8966.53. 1 nova confirmação.
