# 0112 — Série CS pré-registro: replicação opt-in v2 long grandfather (BTC/SOL 2024-H2)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0111 (schema normalization), Padrão 25/26 (ADR-0106/0108/0109)

## Motivação

ADR-0111 identificou 5 combos "grandfather" pré-Padrão 25 no stack:
- v2 ETH 2024-H1 + ETH 2025-H1 (companion pair — cross_window_via_companion já OK)
- v2 BTC 2024-H2 (single_window)
- v2 SOL 2024-H2 (single_window)

BTC/SOL 2024-H2 são os únicos combos no stack ativo sem cross-window evidence formal. Grandfathered sob protocolo v1 (pré-Padrão 25). Opt-in upgrade requer replicação regime-matched.

## Escopo

4 runs, engine v2 long (bollinger window=30, num_std=1.5, long_only=true) + filter bollinger_width 250 bps:

| Tag | Symbol | Janela | Regime esperado |
|---|---|---|---|
| CS.1 | BTC | 2024-H1 | chop pre-bull |
| CS.2 | BTC | 2025-H1 | chop |
| CS.3 | SOL | 2024-H1 | chop pre-bull |
| CS.4 | SOL | 2025-H1 | chop |

Baseline 2024-H2 é bull-com-chop. Janelas alternativas mais chop-heavy — regime-matched por proxy (ambas têm drawdowns para mean-reversion long funcionar).

## Gates pré-registrados

Por combo (BTC 2024-H2 ou SOL 2024-H2), contra 2 janelas adicionais:

- **Strict upgrade**: ≥1 janela adicional com Sh ≥ 1.0 + trades ≥ 20 (gate relaxado vs 30 original — pequena amostra é aceitável pra cross-window evidence, não pra entrada nova no stack)
- **Contextual upgrade**: ≥1 janela com Sh ≥ 0.5 + trades ≥ 15 (proporcional)
- **Rollback/flag stack risk**: ambas janelas Sh < 0 → combo vira candidato a remoção do stack em próxima revisão (não remoção automática; levantar issue)
- **Status quo**: ambas janelas Sh entre 0 e 0.5 → mantém `single_window` grandfather

Expectativa base (com histórico observado): v1 approved_combos excluded listou BTC 2024-H1 Sh=0.41, SOL 2024-H1 Sh=0.30, SOL 2025-H1 Sh=0.62 — todos dentro da faixa "status quo" ou borderline contextual.

## Racional do re-teste

Dados históricos já sugerem status quo provável, mas:
1. Valores históricos são de v1 protocolo (4-fold WF, seed diferente, filter params potencialmente diferentes)
2. ADR-0038 reconfirmou que params corretos (30/1.5) diferem do que rodou originalmente em algumas sensibilidades
3. Re-rodar com protocolo v2 atual + gate Padrão 25 refinado = resultado auditável e classificável

Timebox: 4 runs ~15-20min wall. ADR-0113 closeout decide upgrades.

## Saída esperada

- `teste/results/validation/cs-v2-*` (4 diretórios)
- ADR-0113 closeout com classificação per combo
- Edit em `exports/approved/bollinger_width_regime_20260418_v2.json` atualizando `cross_window_status_summary.status_per_combo`
