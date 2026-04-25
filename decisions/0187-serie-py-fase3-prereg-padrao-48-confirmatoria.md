# 0187 — Série PY Fase 3 pré-reg: terceira engine em SOL 2025-H1 para confirmar Padrão 48

**Status:** Proposed
**Date:** 2026-04-21
**Deciders:** Usuário ("testa mais") + agente
**Relates to:** ADR-0180 (v4 spec + amendment #10), ADR-0184/0185 (PY Fase 1), ADR-0186 (PY Fase 2 + Padrão 48 candidato), ADR-0176 (ZS engine)

## Contexto

ADR-0186 deixou Padrão 48 em estado **candidato** (N=2 engines independentes: RSI 25/75 + trend_htf e BB 20/1.5 short + width, ambas passando gate mínimo pyramid em SOL 2025-H1 com degradação parcial de Sharpe e amplificação de PnL). Formalização requer confirmação em terceira engine independente.

User direcionou "testa mais" → piloto automático executa frente de valor informativo mais alto (ADR-0186 §"Próxima frente candidata" item 1).

## Escolha da terceira engine: zscore MR + width SOL 2025-H1

Critérios:
- **Distinct family**: não-RSI, não-BB. zscore é MR standalone (ADR-0175).
- **Baseline proven em SOL 2025-H1**: ZS.12 (ADR-0176 §Fase 3) rodou `zscore 20/2.0 short + bollinger_width:30/1.5/300bps` em SOL 2025-H1 com **Sh=4.94, trades=82, PnL=+33.84%**. Edge forte, in-era consistent (ZS.3 SOL 2025-H1 naked também passou Sh=3.01).
- **Compliant invariante #10** (ADR-0185): filter anexado (`bollinger_width`).

## Probe PY.7

Dataset: `solusdt_1h_20250105_20250704_binance_spot`
Engine: `zscore 20/2.0 short --no-long-only`
Filter: `bollinger_width:window=30:num_std=1.5:min_width_bps=300`
Sizing: `pyramid_equity`, `max_tranches=5`, `tranche_equity_fraction=0.20`, `rearm_cooldown=1`, `leverage=2.0`
Validação: `--n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 --mc-resamples 1000` (idêntico a ZS.12 baseline para apples-to-apples)

**Run ID:** `py-sol-zscore-short-width300-pyr-2025h1`

## Pré-registro (Padrão 4)

### Gate de confirmação Padrão 48

**Pass** se: `Sh ≥ 1.5 AND seqs ≥ 10 AND Sh ≥ 0.9 × Sh_baseline` (edge preservation).

Com ZS.12 baseline Sh=4.94, gate edge-preservation exige Sh ≥ 4.45. É um gate forte. Gate mínimo alternativo (Sh≥1.5 + seqs≥10) distingue entre "pyramid preserva edge" vs "pyramid degrada mas ainda acima threshold".

### Outcomes pré-registrados

- **Gate completo pass (Sh ≥ 4.45, seqs ≥ 10)**: Padrão 48 consolidado com N=3 engines independentes. ETA manifest v4 SOL 2025-H1 re-considerável (mas ainda falha Padrão 41 cross-asset/era → não promoção real, só Padrão 48 como observação).
- **Gate mínimo pass (Sh ≥ 1.5 AND seqs ≥ 10) mas não edge-preserv**: Padrão 48 consolidado em forma FRACA — SOL 2025-H1 tolera pyramid sizing sem colapsar, mas sempre com degradação de Sharpe significativa. Observação documentada, não actionable para deploy.
- **Gate mínimo fail (Sh < 1.5 OR seqs < 10 OR Sh negativo)**: Padrão 48 **refutado**. Os 2 passes anteriores (PY.1, PY.4) são artefato de engines correlacionadas (RSI e BB-short dependem de mean-reversion em MTF contexto similar; zscore MR é categorical diferente). Fracasso aqui descarta "SOL 2025-H1 é regime pyramid-friendly genérico".

### Hipótese

Prior esperado: ~45% (ligeiramente maior que ADR-0186 §1 estimava 40%, ajustado para cima porque zscore+width já mostrou robustez Sh=4.94 naked vs baselines 2.00 e 2.71 de PY.1/PY.4, sugerindo "headroom" maior para absorver pyramid degradação sem cair abaixo de 1.5).

## Não-alvo

- Não testar leverage=1× nem 5× (ADR-0186 consolidou 2× como padrão estabelecido).
- Não testar outras janelas além de SOL 2025-H1 nesta fase (a Fase é *confirmatória* do padrão já hipotetizado; cross-asset/era é exatamente o que já falhou em PY.5/PY.6 e não tem retest value).
- Não emitir manifest v4. ADR-0180 §approval gate exige cross-window strict pass, que não ocorreu e não ocorrerá neste sub-espaço.

## Ação

1. Tool `run_py3_sweep.py` + `summarize_py3.py`.
2. 1 run PY.7.
3. ADR-0188 closeout (consolidação ou refutação Padrão 48).
4. STATE.md update.

## Relação com handoff bot

- v4 stand-down (ADR-0183) permanece. PY.7 não altera isso.
- Nada novo a reportar ao bot até closeout. Se Padrão 48 confirmado, bridge post opcional para observação (não muda decisão do bot — stack canônico v3 inalterado).
