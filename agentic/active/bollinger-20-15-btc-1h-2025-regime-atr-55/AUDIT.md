# AUDIT.md - AD.1

> Gate: **auditoria**.

## Hipótese × evidência

Hipótese: num_std=1.5 preserva edge OOS 2025 em BTC (generalizando AC.1).

**Resultado:** hit 44.44% < 45% (critério 1 ADR-0025 violado)

## Comparação com AC.1

- AC.1 ETH 20/1.5+atr:105 2025: fe 10465 hit 64.15% 53 trades — **EDGE PRESERVED**
- AD.1 BTC: fe 9985.53 hit 44.44% 54 trades

**Implicação:** AC.1 é ETH-específico; 1.5 std não generaliza para BTC OOS.

## Blockers

Nenhum bloqueio técnico.

## Release

release_decision: `fail`

## ADR-0019

Stress fee+10 ≡ spread+10 = 9769.78. 1 nova confirmação.
