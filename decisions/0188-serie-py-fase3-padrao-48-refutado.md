# 0188 — Série PY Fase 3 closeout: Padrão 48 candidato refutado (terceira engine colapsa)

**Status:** Accepted — Padrão 48 não promovido; pyramid v4 definitivamente refutado cross-engine em SOL 2025-H1.
**Date:** 2026-04-21
**Deciders:** Usuário ("testa mais") + agente
**Relates to:** ADR-0186 (Padrão 48 candidato), ADR-0187 (pré-reg Fase 3), ADR-0176 (baseline ZS.12)

## Resultado PY Fase 3

| Tag | Combo | Sh (v4) | Sh baseline | ΔSh | PnL% (v4) | PnL baseline | ΔPnL% | Gate min | Edge preserv |
|---|---|---:|---:|---:|---:|---:|---:|:---:|:---:|
| PY.7 | SOL 2025-H1 zscore+width 300 + pyr 2× | **1.459** | 4.94 | -3.48 | +46.66 | +33.84 | +12.82 | ✗ | ✗ |

Gate mínimo (Sh≥1.5 AND seqs≥10): **FAIL por 0.041** (Sh=1.459 vs threshold 1.5). Seqs=35 adequado. Edge preservation (Sh ≥ 0.9×baseline = 4.45): FAIL (29.5% retention).

Fold equities (capital=10k cada): 8942, 13021, 10169, 12386. Média fold +9.1%, alta variance entre folds.

## Interpretação: Padrão 48 refutado por gate pré-registrado

Pré-registro (ADR-0187) dizia: **Gate mínimo fail (Sh < 1.5) → Padrão 48 refutado**. Os 2 passes anteriores (PY.1 e PY.4) são artefato de engines correlacionadas.

Sh=1.459 está 0.041 abaixo. Padrão 4 (pré-registro) exige honrar threshold mesmo em proximidade. **Refutado.**

## Por que zscore colapsa mais que RSI e BB-short?

Degradação de Sharpe sob pyramid v4 cresce com força do baseline:

| Engine | Baseline Sh | Pyramid Sh | Degradação | PnL amplif |
|---|---:|---:|---:|---:|
| PY.1 RSI 25/75 + tHTF | 2.00 | 1.61 | -19.5% | 3.6× |
| PY.4 BB 20/1.5 + width | 2.71 | 1.87 | -31.0% | 4.5× |
| PY.7 zscore 20/2.0 + width | 4.94 | 1.46 | -70.5% | 1.4× |

Hipótese emergente: **baselines de alta Sharpe exploram eficientemente windows de baixa volatilidade** (entry preciso + hold curto + exit limpo = alto Sharpe). Pyramid adiciona tranches durante high-vol regimes (quando filter é aprovador), **diluindo** a eficiência de entry. Efeito é menor em baselines middling (Sh 2-2.7) onde pyramid's PnL amplification domina sobre variance cost, mas domina sobre Sharpe em baselines já excellent.

Implicação: o "pyramid-friendly regime SOL 2025-H1" observado em ADR-0186 era **efeito de seleção**. Engines com Sharpe intermediário têm headroom estatístico para pyramid preservar gate ≥1.5; engines com Sharpe forte falham justamente porque partem de cima.

## Consolidação PY completa (3 Fases, 5 probes válidas de 7 rodadas)

| Probe | Combo | Sh pyr | Sh base | Gate min | Edge preserv |
|---|---|---:|---:|:---:|:---:|
| PY.1 | SOL 2025H1 RSI + tHTF | 1.61 | 2.00 | ✓ | ✗ |
| PY.2 | SOL 2025H2 RSI naked | — invalido (no filter) | — | N/A | N/A |
| PY.3 | BTC 2025H2 RSI naked | — invalido (no filter) | — | N/A | N/A |
| PY.4 | SOL 2025H1 BB short + width | 1.87 | 2.71 | ✓ | ✗ |
| PY.5 | ETH 2025H1 BB short + width | -1.46 | 2.40 | ✗ | ✗ |
| PY.6 | SOL 2024H2 BB short + width | -0.05 | 1.38 | ✗ | ✗ |
| PY.7 | SOL 2025H1 zscore + width | 1.459 | 4.94 | ✗ | ✗ |

**2/5 válidas passam gate mínimo**, **0/5 preservam edge**. Os 2 passes são **mesmo asset+window** mas engines distintas. Padrão 48 requeria ≥3 engines independentes → não confirmado.

## Padrão 48 stand-down (não formalizado)

- **Observação**: existe alguma susceptibilidade de SOL 2025-H1 a pyramid sizing em engines de Sharpe intermediário. Insuficiente para padrão.
- **Não vira padrão numerado**. Stand-down como "observação sem ação".
- Se, hipoteticamente, alguma futura engine for testada em SOL 2025-H1 com baseline Sh 2-3 e passar pyramid, re-considerar. Até lá, pyramid v4 é refutado genericamente.

## Decisão

- **Padrão 48 refutado** (sub-registrado, fica só Padrão 45 como meta-pattern sobre outliers single-asset).
- **Pyramid v4 definitivamente refutado** cross-engine em SOL 2025-H1. Qualquer combo futuro pyramid precisaria de nova justificativa forte (nova engine, nova janela, nova hipótese).
- **Stack 13 combos v3 faithful inalterado**. 
- **Manifest v4 schema permanece não escrito** (ADR-0180 amendment #10 permanece documentado para uso eventual).
- **v4 stand-down ao bot permanece** (ADR-0183).
- **Infra v4 permanece dormente no repo** (sem remoção — custo zero manter, reativável se user direcionar).

## Implicações para handoff bot

Nada novo a reportar. Stack canônico v3 faithful inalterado. v4 stand-down (ADR-0183) permanece.

## Não-alvo

- Não retestar leverage diferente (1× ou 5×) em PY.7 — ADR-0186 consolidou 2× como padrão, mudar leverage agora é fishing.
- Não reimagined pyramid como "only for middling-Sharpe engines" — seria ad-hoc post-hoc; Padrão 4 rejeita.
- Não abrir nova frente pyramid automaticamente — pyramid foi explorado 3 Fases, 7 runs, refutado.

## Próxima frente candidata (autopilot continua?)

PY fechada. Frentes remanescentes de ADR-0183 / ADR-0186:

1. **Pyramid long-side em BB long + width proven** (4 combos no stack, baselines Sh 1.21-2.40). Opção 3 do ADR-0186. Prior reduzido pós-PY.7: ~20% (curva de aprendizado: Sharpe alto não sobrevive pyramid).
2. **Composite engines BB+RSI** (dev 2-4h, prior ~25%).
3. **Cross-sectional / portfolio** (dev ~1 dia, prior incerto).
4. **Stack atual como handoff-target**, focar bot paper-trade (status atual).
5. **Aceitar autopilot exhausted (Padrão 47 re-confirmado)** e aguardar direção user.

Autopilot recomendação: se "testa mais" vier de novo, executar frente (1) pyramid long-side como probe rápido (baseline já existe). Se falhar, escalar para pausa formal Padrão 47 round 3 e pedir direcionamento.

## Ação executada

- ✅ run_py3_sweep.py + summarize_py3.py
- ✅ PY.7 run (zscore+width SOL 2025-H1 + pyramid 2×)
- ✅ ADR-0188 closeout (este)
- ⏭️ STATE.md update
