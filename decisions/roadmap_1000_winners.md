# Roadmap 1000 — Vencedoras

Registro incremental dos probes que passaram algum gate durante execução do roadmap_1000.

**Gates:**
- **Sh**: annual_sharpe >= 1.5 AND trades >= 30
- **alfa**: pnl_pct_probe > bh_pct / leverage (=2)
- **Ambos**: Sh AND alfa

Cross-era = 3 windows (2024-H2, 2025-H1, 2025-H2). Isolated = single window.

---

## Batch MA01 — ma_crossover long 10m, grid 10/30 + 15/45 × ETH/SOL (10 probes)

**Data:** 2026-04-21
**Agregado:** Sh=0/10, alfa=3/10, ambos=0/10

### alfa-only (sem Sh)

| Tag | Params | Label | Tr | Sh | PnL% | B&H% | alfa | Nota |
|---|---|---|---:|---:|---:|---:|---:|---|
| MA01.02 | 10/30 | ETH 2025-H1 | 420 | -0.91 | -4.17 | -47 | +19.33 | bear-avoidance (Padrão 50) |
| MA01.05 | 10/30 | SOL 2025-H1 | 390 | -0.80 | -4.34 | -40 | +15.66 | bear-avoidance (Padrão 50) |
| MA01.08 | 15/45 | ETH 2025-H1 | 264 | +0.98 | +3.96 | -47 | +27.46 | único PnL>0, bear-avoidance |

### Padrão reforçado

**Padrão 50 (trend-following bear-avoidance 10m)** agora com **4 peças de evidência** (MA01.02/05/08 + TF10I.5 20/50 ETH 2025-H1 Sh=+1.61). Todas em bear 2025-H1 (ETH/SOL). Nenhum pass em bull/flat. **Ainda regime-specific, não cross-era.**

**Sweet spot MA**: 20/50 > 15/45 > 10/30 (Sharpe decresce com períodos curtos por whipsaw).

---

## Batch MA02 — ma_crossover long 10m, grid 15/45 SOL + 25/75 ETH/SOL + 30/90 bear (10 probes)

**Data:** 2026-04-21
**Agregado:** Sh=1/10, alfa=5/10, **ambos=1/10**

### Sh+alfa (ambos os gates)

| Tag | Params | Label | Tr | Sh | PnL% | B&H% | alfa | Nota |
|---|---|---|---:|---:|---:|---:|---:|---|
| **MA02.04** | 25/75 | ETH 2025-H1 | 154 | **+1.91** | **+7.98** | -47 | **+31.48** | **2ª pass Sh+alfa do roadmap** |

### alfa-only (sem Sh)

| Tag | Params | Label | Tr | Sh | PnL% | B&H% | alfa |
|---|---|---|---:|---:|---:|---:|---:|
| MA02.01 | 15/45 | SOL 2025-H1 | 252 | -0.01 | -0.35 | -40 | +19.65 |
| MA02.07 | 25/75 | SOL 2025-H1 | 147 | -0.22 | -1.37 | -40 | +18.63 |
| MA02.09 | 30/90 | ETH 2025-H1 | 126 | +1.39 | +5.70 | -47 | +29.20 (Sh quase) |
| MA02.10 | 30/90 | SOL 2025-H1 | 121 | +0.01 | -0.26 | -40 | +19.74 |

### Curva de sharpe-vs-params (ETH 2025-H1, bear −47%)

| Params | Sh | PnL% | alfa |
|---|---:|---:|---:|
| 10/30 | -0.91 | -4.17 | +19.33 |
| 15/45 | +0.98 | +3.96 | +27.46 |
| 20/50 | +1.61 | +6.75 | +30.25 (TF10I.5) |
| **25/75** | **+1.91** | **+7.98** | **+31.48 (MA02.04)** |
| 30/90 | +1.39 | +5.70 | +29.20 |

**Curva em sino**, pico em 25/75. Padrão 50 robusto ao parâmetro MA em ETH 2025-H1.

### Padrão 50 — status

- **Sh+alfa pass**: 2/total (TF10I.5 20/50 + MA02.04 25/75) — **ambos ETH 2025-H1**
- **alfa-only**: 8 probes (1 BTC, 3 SOL 2025-H1 e 4 ETH em diversos MA curtos)
- **Cross-era ainda falha**: 2024-H2 e 2025-H2 todos alfa−, Sh−
- **ETH > SOL em risco-ajustado**: SOL 2025-H1 tem alfa+ mas nunca Sh+
- **Conclusão parcial**: Padrão 50 **confirma regime-dependência** em 2025-H1 bear alt. Sem operacionalização sem regime detection.

---

## Batch ST01 — supertrend 10m bear-val ETH/SOL 2025-H1, grid atr×mult×direction (10 probes)

**Data:** 2026-04-21
**Agregado:** Sh=3/10, alfa=10/10, **ambos=3/10**

### Sh+alfa (ambos)

| Tag | Params | Label | Tr | Sh | PnL% | alfa |
|---|---|---|---:|---:|---:|---:|
| **ST01.03** | atr=10 mult=4.0 bi | ETH 2025-H1 | 165 | **+1.95** | **+8.30** | **+31.80** |
| **ST01.05** | atr=14 mult=3.0 bi | ETH 2025-H1 | 245 | +1.55 | +6.48 | +29.98 |
| **ST01.09** | atr=20 mult=3.0 bi | ETH 2025-H1 | 247 | +1.61 | +6.85 | +30.35 |

### alfa-only

7 probes (todas ETH/SOL 2025-H1 com alfa+, porém Sh<1.5). Nota: **todas 10/10 probes ST01 passam alfa**.

### Descoberta

**Padrão 50 é engine-general**: passa em **2 engines independentes** (ma_crossover e supertrend) no mesmo regime (ETH 2025-H1). Este é um upgrade significativo — antes era candidato single-engine/regime, agora é **candidato cross-engine/single-regime**.

**Promoção ainda bloqueada por**: falta cross-era validation (2024-H2 e 2025-H2 todos negativos em MA01/MA02).

### Roadmap passes cumulativos Sh+alfa (todos ETH 2025-H1)

| Tag | Engine | Params | Sh | PnL% | alfa |
|---|---|---|---:|---:|---:|
| TF10I.5 | ma_crossover | 20/50 long | +1.61 | +6.75 | +30.25 |
| MA02.04 | ma_crossover | 25/75 long | +1.91 | +7.98 | +31.48 |
| ST01.03 | supertrend | atr=10 m=4.0 bi | **+1.95** | **+8.30** | **+31.80** |
| ST01.05 | supertrend | atr=14 m=3.0 bi | +1.55 | +6.48 | +29.98 |
| ST01.09 | supertrend | atr=20 m=3.0 bi | +1.61 | +6.85 | +30.35 |

**5 passers. Único regime: ETH 2025-H1.** Sweet spot universal: trend-following long-or-bi com parâmetros que reduzem whipsaw.

---

## Batch BT01 — BTC cross-era sweet-spot MA+ST 10m (10 probes)

**Data:** 2026-04-21
**Agregado:** Sh=0/10, alfa=4/10, ambos=0/10

### alfa-only (todas BTC 2025-H1, alfa marginal)

| Tag | Params | Sh | PnL% | alfa |
|---|---|---:|---:|---:|
| BT01.02 | MA 25/75 | -0.50 | -1.40 | +2.60 |
| BT01.05 | ST 10/4.0 bi | -0.95 | -2.52 | +1.48 |
| BT01.08 | ST 14/3.0 bi | -1.36 | -3.65 | +0.35 |
| BT01.10 | MA 30/90 | -0.31 | -0.89 | +3.11 |

### Descoberta

**Padrão 50 é ASSET-specific (alts, não BTC)**. Alfas em BTC 2025-H1 são ~10× menores que ETH 2025-H1 (+1 a +3 vs +27 a +32). Bull periods (BTC 2024-H2, 2025-H2) destroem o edge (alfa -10 a -38).

**Refino do Padrão 50**: trend-following long-or-bi 10m → bear-avoidance **requer drawdown profundo (≥35%) em altcoin**. BTC bear-8% é raso demais; BTC bull é punição absoluta.

### Tabela-síntese Padrão 50 por asset × regime

| Regime | ETH | SOL | BTC |
|---|---|---|---|
| Bull 2024-H2 | alfa− | alfa− | alfa− |
| Bear 2025-H1 | **alfa+, Sh+ múltiplos** | alfa+, Sh− | alfa≈0 marginal |
| Bull 2025-H2 | alfa− | alfa− | alfa− |

**Conclusão consolidada**: Padrão 50 opera apenas em **ETH bear ≥40%**. Sem detecção de regime, não operacionalizável.

---

## Batch AE01 — asset expansion 1h DOT/LINK/AVAX (10 probes)

**Data:** 2026-04-21
**Agregado:** Sh=0/10, **alfa=10/10**, ambos=0/10

### alfa-only (todas)

| Tag | Params | Label | Sh | PnL% | B&H% | alfa |
|---|---|---|---:|---:|---:|---:|
| AE01.01 | BB 20/2.0 | DOT 2025-H1 | -1.08 | -3.93 | -56.2 | +24.18 |
| AE01.02 | BB 20/2.0 | DOT 2025-H2 | +0.68 | +2.91 | -47.1 | +26.46 |
| AE01.03 | BB 20/2.0 | LINK 2025-H1 | -0.37 | -1.76 | -44.0 | +20.21 |
| AE01.04 | BB 20/2.0 | LINK 2025-H2 | +0.20 | +0.61 | -7.6 | +4.43 |
| AE01.05 | BB 20/2.0 | AVAX 2025-H1 | -1.91 | -7.91 | -58.2 | +21.18 |
| AE01.06 | BB 20/2.0 | AVAX 2025-H2 | -0.99 | -4.27 | -30.9 | +11.16 |
| AE01.07 | MA 20/50 | DOT 2025-H1 | -1.82 | -7.46 | -56.2 | +20.65 |
| AE01.08 | MA 20/50 | LINK 2025-H1 | -1.70 | -8.55 | -44.0 | +13.43 |
| AE01.09 | MA 20/50 | AVAX 2025-H1 | -0.27 | -1.68 | -58.2 | +27.41 |
| AE01.10 | ST 10/3.0 | AVAX 2025-H1 | +0.23 | +0.80 | -58.2 | +29.89 |

### Descoberta — refino do Padrão 50

**Padrão 50 é ALT-bear-general, não ETH-específico**. Em alts que caíram severamente em 2025-H1 OU H2 (DOT/LINK/AVAX), estratégias longas/bi geram alfa positiva **em qualquer TF (1h aqui)**. O que é ETH-único é o **Sh+** (risco-ajustado): só ETH 2025-H1 em 10m passou.

**Refino consolidado**:
- **Alfa via bear-avoidance** = padrão amplo, aplicável a alts em bear profundo (≥30% drawdown).
- **Sharpe positivo** = exige confluência: TF curto (10m) + ETH + bear severo específico.
- **1h não gera Sh** em nenhum asset/direction/regime (0/10).

