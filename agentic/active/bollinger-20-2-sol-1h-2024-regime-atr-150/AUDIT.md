# AUDIT.md — R.2 Bollinger SOL 1h 2024 + atr_regime:150

## Hipótese × evidência

Hipótese: threshold 150 bps é **over-filtering** — corta sinais
válidos, amostra pequena, edge instável.

Evidência: 26 trades (vs 87 J.1 → −70%; vs 65 R.1 → −60%). hit=65.38%
**abaixo de J.1 (67.82%) e R.1 (70.77%)**. fe=10420.94 **abaixo de R.1
(10803.68)**. MC p5=10074.98 **abaixo de R.1 (10212.03)**. **Hipótese
confirmada: threshold 150 é over-filter em SOL 1h.**

## Ranking dimensional (R.2 vs vizinhos curva)

| Dim | J.1 (—) | Q.1 (50) | **R.1 (100)** | R.2 (150) |
| --- | ------: | -------: | ------------: | --------: |
| trades | 87 | 87 | 65 | **26** |
| hit | 67.82% | 67.82% | **70.77%** | 65.38% |
| fe | 10684 | 10716 | **10803** | 10420 |
| MC p5 | 10046 | 10064 | **10212** | 10074 |
| ratio | 0.9673 | 0.9674 | 0.9758 | **0.9899** |
| mdd | 3.94% | 3.94% | 3.38% | **2.92%** |

R.2 melhor apenas em **ratio e mdd** — ambos triviais via menor
exposição (amostra pequena corta custo acumulado e drawdown). **R.2 é
dominado por R.1 em fe, hit, MC p5, e trades efetivos.**

## Curva de utilidade SOL+atr — forma

`— → 50 → 100 → 150` traçam **U invertido com plateau esquerdo**:
- 50 é inativo (threshold abaixo do 1º decil ATR SOL).
- 100 é sweet spot (remove ~25% sinais, quantile ≈20).
- 150 é over-filter (remove ~70% sinais, quantile ≈60).

**Operacional**: R.1 é o ponto ótimo para SOL 1h 2024-H2. R.2 mapeia
o lado caro da curva — não é deployable, mas é **evidência crítica
da forma da curva**.

## Release

release_decision: `canary_only` **com caveat operacional**: passa os
3 gates ADR-0025 mas amostra de 26 trades é insuficiente para
confiança estatística. **Dominado por R.1 — não promove sobre R.1.**

## Blockers

Nenhum bloqueio técnico. Caveat operacional: amostra 26 trades (R.2)
insuficiente para deploy; R.1 é o ponto deployable da curva.

## ADR-0019

41ª confirmação. `fee+10 ≡ spread+10 = 10316.21`. 4ª vez stress >
10000 (R.1=10542.34, R.2=10316.21, P.2=10028.59, Q.1=10379.49).
Ratio 0.9899 é o **maior do protocolo** (trivialmente).

## Finding — protocolo N=41

**Universalidade de filtro é questão de calibração. Curva de utilidade
é não-monotônica com sweet spot em quantile-15-25 do ATR do asset.**
Série R estabelece método: mapear 3 pontos (baixo/médio/alto) para
localizar sweet spot antes de deploy.

## Próximo

Série T sugerida: replicar mapeamento curva para BTC (thresholds
35/70/100) e ETH (50/75/120) para confirmar método cross-asset.
