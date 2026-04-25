# 0186 — Série PY Fase 2 closeout: pyramid v4 refutada cross-asset/era, SOL 2025-H1 outlier emergente

**Status:** Accepted — PY refutada Fase 2; pyramid v4 não-promoção; observação candidata a Padrão 48.
**Date:** 2026-04-21
**Deciders:** Usuário ("ok, continue então") + agente
**Relates to:** ADR-0184/0185 (PY Fase 1 + constraint), ADR-0180 (v4 spec + amendment), Padrão 41, Padrão 45

## Resumo

PY Fase 2 re-testou pyramid v4 em 3 combos **BB short + width proven** (stack v3 faithful, todos com filter compliant ao invariante #10). **Gate 1/3 FAIL**. Pyramid v4 refutada como paradigma broadly-aplicável. Nova observação: **SOL 2025-H1 é regime pyramid-friendly** em 2 engines independentes (Padrão 48 candidato).

## Resultados PY Fase 2

| Tag | Combo | Sh (v4) | Sh baseline | ΔSh | PnL% (v4) | PnL baseline | ΔPnL% |
|---|---|---:|---:|---:|---:|---:|---:|
| PY.4 | SOL 2025-H1 BB 20/1.5 short + width(300) + pyr 2×lev | **1.87** | 2.71 | -0.84 | **+78.30** | +17.47 | +60.83 |
| PY.5 | ETH 2025-H1 idem | -1.46 | 2.40 | -3.86 | -50.39 | +12.16 | -62.55 |
| PY.6 | SOL 2024-H2 idem | -0.05 | 1.38 | -1.43 | -14.30 | +6.64 | -20.94 |

Gate ≥2/3 Sh≥1.5 AND preserva edge (Sh ≥ 0.9×baseline): **0/3**. Gate mínimo Sh≥1.5 AND seqs≥10: **1/3**.

## Consolidação PY (Fase 1 + Fase 2, 4 probes válidas)

| Probe | Config | Sh pyr | Sh base | Gate min (Sh≥1.5) | Edge preservation |
|---|---|---:|---:|:---:|:---:|
| PY.1 | SOL 2025H1 RSI 25/75 + tHTF | 1.61 | 2.00 | ✓ | ✗ (80.5%) |
| PY.2 | SOL 2025H2 RSI naked — invalido estrutural | — | 2.30 | N/A | N/A |
| PY.3 | BTC 2025H2 RSI naked — invalido estrutural | — | 1.64 | N/A | N/A |
| PY.4 | SOL 2025H1 BB short + width | 1.87 | 2.71 | ✓ | ✗ (69.0%) |
| PY.5 | ETH 2025H1 BB short + width | -1.46 | 2.40 | ✗ | ✗ |
| PY.6 | SOL 2024H2 BB short + width | -0.05 | 1.38 | ✗ | ✗ |

**2/4 válidas passam gate mínimo**, 0/4 preservam edge. **Ambos os passes são SOL 2025-H1**.

## Interpretação: pyramid v4 é regime-específico SOL 2025-H1

### Evidência

2 engines independentes (RSI 25/75 + tHTF vs BB 20/1.5 + width) testadas em SOL 2025-H1 com pyramid 2×lev: ambas preservam acima de gate Sharpe 1.5 (1.61 e 1.87) com PnL amplificado 3.6× e 4.5× respectivamente. Outros 3 combos testados (SOL 2025H2, 2024H2, ETH 2025H1, BTC 2025H2) colapsam — Sharpe negativo ou fortemente degradado.

SOL 2025-H1 é janela onde:
- Pyramid **preserva parcialmente** Sharpe (degradação 20-31% em vez de 100%+)
- Pyramid **amplifica PnL 3-4×** vs baseline fixed_notional
- Engines de famílias distintas (trend-filtered RSI, width-filtered BB) **ambos respondem** positivamente ao mesmo paradigma de sizing

### Hipótese candidata (Padrão 48, pré-formalização)

**"Crypto 1h SOL 2025-H1 é regime estatisticamente favorável a pyramid-sizing: trends locais curtos + retornos assimétricos de curto prazo permitem tranches múltiplas acumularem MTM antes do regime flip. Outros assets/janelas têm volatilidade mais simétrica ou mean-reversion rápida demais, onde pyramid + leverage amplifica drawdown no momento errado."**

N=2 engines independentes, mesmo asset+window. Não cumpre ainda critério Padrão 43 (cross-era) — SOL 2025-H2 e 2024-H2 explicitamente falham. Formalização requer confirmação em terceira engine na mesma janela.

### Por que SOL 2025-H1 é especial?

Hipótese empírica:
- Asset SOL em 2025-H1 teve múltiplos pullbacks dentro de range estrutural (não full trend, não full consolidation)
- Width filter (≥300 bps) capturou períodos de volatilidade expansiva com trend direcional curto
- Pyramid acumula short tranches em cada rejeição da banda superior, fecha quando width cai (volatilidade contrai) ou filter vira
- **Mean reversion intra-range + entries escalonadas = tranches acumulam antes de reverter**

Contra-exemplo SOL 2024-H2: mesmos filter, mesmo asset, Sh pyramid=-0.05. 2024-H2 teve trends mais extendidos e pullbacks mais simétricos — pyramid catch falling knife em cada touch da banda.

## Padrão 45 reiterado

PY Fase 2 também confirma Padrão 45 no espelho: em vez de ETH-only outlier, agora SOL-only em window específica. Mensagem operacional: **single-asset single-window edges em crypto 1h NÃO generalizam cross-asset/era com pyramid v4 sizing**. Padrão 45 aplica-se ao paradigma sizing, não só ao paradigma signal.

## Decisão

- **PY refutada** em Fase 2 (cross-asset/era 1/3 gate). Não prosseguir Fase 3.
- **Pyramid v4 NÃO promoção** ao stack. Gate mínimo insuficiente + edge preservation falha.
- **Manifest v4 schema continua não escrito**. ADR-0180 amendment #10 permanece documentado para uso eventual futuro.
- **Padrão 48 candidato** — formalizar se terceira engine independente passar em SOL 2025-H1 com pyramid.
- **Não dev adicional em v4**. Infra permanece dormente.
- **Stack 13 combos v3 faithful inalterado**.

## Implicações para handoff bot

- v4 stand-down (ADR-0183) **permanece**. Bot não precisa adapter.
- Nada novo a reportar ao bot nesta iteração. Stack canônico v3 inalterado.

## Não-alvo

- Não testar terceira engine em SOL 2025-H1 nesta sessão para confirmar Padrão 48 (user pode solicitar)
- Não tentar pyramid com leverage=1× (já temos dados com 2× e 5×, padrão estabelecido: leverage amplifica degradação fora de SOL 2025-H1)
- Não emitir manifest v4 sem cross-window strict pass (ADR-0180 §approval gate exige)

## Próxima frente candidata (para user decidir)

PY closed como pyramid-sizing refutada broadly. Frentes ainda unexplored cheap:

1. **Confirmar Padrão 48 com terceira engine em SOL 2025-H1**: ex. zscore MR + width + pyramid. Se passa 3/3 SOL 2025-H1 com pyramid, formalizar padrão "pyramid-friendly regime = window signature". (Prior ~40%, valor de informação alto.)
2. **ADR-0184 Fase 2 single-era cross-engine**: reverse da dimensão — fix SOL 2025-H1 + 3 engines pyramid, em vez de fix engine + 3 combos. (Mesmo teste de 1 acima, framing diferente.)
3. **Pyramid em combos long-side** (proven em v2 bollinger long + width): 4 combos existentes no stack, baselines Sh 1.21-2.40. Hipótese: pyramid long é menos propenso a blowup que short em crypto (caudas longas limitadas pelo zero, short cauda infinita).
4. **Aceitar pyramid como dead e escolher outra frente** (composite BB+RSI, cross-sectional, etc).

## Ação executada

- ✅ run_py2_sweep.py + summarize_py2.py
- ✅ 3 runs PY.4-6 (BB short + width + pyramid)
- ✅ Analysis cross-Fase (4 válidas = 2 pass min gate, ambas SOL 2025-H1)
- ✅ ADR-0186 closeout (este)
- ⏭️ STATE.md update (próximo)
