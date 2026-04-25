# AUDIT.md — S.1 RSI 14/30/70 BTC 1h 2024 + atr_regime:50

## Hipótese × evidência

Hipótese: filtro `atr_regime:14:50` generaliza cross-family para RSI.

Evidência:
- N.2 raw BTC RSI: hit 67.19%, fe 10117.76, 64 trades, ratio 0.9747.
- S.1 BTC RSI + atr:50: hit 65.45%, fe 10097.54, 55 trades, ratio 0.9782.
- Δ: **−1.74pp hit, −20 fe, −14% trades, +0.0035 ratio**.

**Hipótese refutada: filtro ATR não generaliza cross-family para RSI.**
Em Bollinger, ATR agrega (P.2: +5.79pp hit, +134 fe sobre H.1). Em
RSI, ATR é net wash (perde edge, ganha marginal em ratio).

## Por que difere?

**Bollinger (mean-reversion em bandas σ)** entra em extremos de
volatilidade localizada — filtro ATR_min preserva apenas regimes onde
extremos têm follow-through estatístico. **RSI (mean-reversion em
momentum)** entra em extremos de RSI — sinal já é independente de
volatilidade absoluta; filtro ATR descarta oversells válidos em baixa
vol sem ganho compensatório.

**Filtro de volatilidade é específico de família de sinal, não
universal.** Valor do ATR em Bollinger vem da interação
(banda_σ × ATR_min) que RSI não tem.

## Ranking dimensional

S.1 não domina N.2 em nenhuma métrica exceto ratio (trivialmente via
amostra menor). Esperado rank abaixo de N.2 no N=41.

## Release

release_decision: `canary_only` — passa os 3 gates ADR-0025 (hit
65.45% > 45%, mdd OK, ratio 0.9782 > 0.95). Mas **dominado por N.2
raw** (fe e hit maiores, trades maiores) → não promover sobre N.2.

## Blockers

Nenhum bloqueio técnico. Caveat operacional: stress < 10000 (9877.57)
sugere margem fina contra custos; usar N.2 raw em vez de S.1.

## ADR-0019

41ª confirmação. `fee+10 ≡ spread+10 = 9877.57`. **Stress < 10000**
(3ª vez no protocolo que stress cai abaixo de capital inicial).

## Finding — protocolo N=41

**Filtro ATR é valioso em Bollinger, não em RSI.** Valor do filtro
depende da interação família_sinal × filtro, não propriedade absoluta
do filtro. Implicação: cada família nova precisa validar filtro
separadamente (não pode transferir do Bollinger).

## Próximo

- Testar `sma_slope` em RSI (família trend em vez de vol).
- Testar filtro específico de momentum (RSI-regime ou price-trend)
  em RSI.
- Série T (threshold sweep cross-asset) continua sendo Bollinger-only.
