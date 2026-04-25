# 0168 — Série DE closeout: trend_htf 1d em RSI short 1h refutado, Padrão 41 dispara

**Status:** Accepted — refutação + Padrão 41 em 1/3. Cross-timeframe variant arquivada.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0167 (pré-reg), Padrão 41

## Resultado

Primeiro attempt (SMA=50): 0 trades em todos 3 combos — SMA=50 em htf=1d requer ≥50 dias disponíveis por fold, e 2025-H1 (181 dias)/4 folds ≈ 45 dias/fold. Filter impossível.

Retry SMA=20:

| Tag | Combo | Trades | Sh | Baseline 4h | Lift | PnL% |
|---|---|---:|---:|---:|---:|---:|
| DE.1b | BTC RSI+trendhtf1d(sma20) | 20 | 0.04 | 1.69 | **-1.65** | 0.03 |
| DE.2b | ETH RSI+trendhtf1d(sma20) | 35 | 1.55 | 0.50 | **+1.05** | 5.36 |
| DE.3b | SOL RSI+trendhtf1d(sma20) | 14 | 0.33 | 2.00 | **-1.67** | 0.97 |

## Avaliação

1/3 lift > +0.5 (ETH) → **Padrão 41**: signal divergente, janela-específica provavelmente.

BTC/SOL: 20 e 14 trades respectivamente — **sample pequeno demais** para Sharpe confiável. trend_htf 1d SMA=20 seleciona regimes bastante estritos (cerca de 1-2 semanas de downtrend daily SMA confirmado), corta 70-85% dos trades.

## Interpretação

### 1d com SMA curto é muito seletivo para execução 1h

4h sma=50 baseline dá 200+ hours de bias ≈ 8 dias, captura tendências táticas. 1d sma=20 dá bias de ~20 dias — semana/quinzena. Esse timeframe é **macro**, captura bias de regime inteiro mas rejeita 70-85% dos momentos em que RSI 1h gera sinal. Desbalance temporal: filter muito lento, sinal muito rápido.

### Filter 1d dá 1 fire-event por semana em média

SMA 1d flip cross lane tipicamente ocorre 2-4x por mês em crypto. 2025-H1 SOL teve talvez 6-8 flips total. Cada flip dá ~30% do período elegível → ~90 dias short-allowed × 24 = 2160 horas elegíveis por fold de 45 dias, mas trades de RSI são ~1 por 50 horas quando filter ativo → ~40 trades por fold esperados. Observado 3-5 por fold. **Interação filter+RSI é multiplicativa**, não simplesmente gate.

### ETH parcial: possivelmente coincidência 2025-H1

ETH 2025-H1 teve sequência única de downtrends daily claros (preço caiu $3700 → $2000 continuamente). trend_htf 1d capturou essa fase. Prior: não generaliza em H2 (ETH consolidou).

## Decisão

- Nenhuma edição de manifest
- trend_htf 1d SMA=20 em engine 1h: **arquivado**. Filter timeframe (1d) muito distante do signal timeframe (1h); desbalance estrutural
- Padrão 41 prevalece — ETH outlier não é promoção.
- Cross-timeframe variants baratas efetivamente **exauridas** no toolkit atual. Exploração produtiva requer HTF *signals* (não só filter) — exige mudança de código, fora do escopo.

## Padrão informal 44 (candidato — não formalizado)

**"Quando filter HTF tem período muito maior que signal timeframe (ex. 1d filter + 1h signal), filter é effectively macro-gate e corta >70% das oportunidades. Sharpe pode inflar em outlier mas sample cai abaixo de thresholds estatísticos (<40 trades). Sweet spot filter/signal ratio parece ser 4x-8x (4h/1h, 4h/30m) — não 24x (1d/1h)."**

Não formalizar agora — só 1 observação (DE). Re-revisitar se outra série mostrar mesma assinatura.

## Ação executada

- ✅ ADR-0167 pré-reg
- ✅ 3+3 runs DE (primeira tentativa SMA=50 zero trades; segunda SMA=20 completou)
- ✅ ADR-0168 closeout
- ✅ Cross-timeframe variants arquivadas

## Não-alvo

- Não re-testar SMA intermediários (25/30/40) em 1d — prior: mesma classe de problema de sample
- Não testar 1W — CZ4b já refutou em 4h; 1h seria ainda pior
- Não formalizar Padrão 44 sem replicação

## Próxima frente

Novos engines (zscore MR, vol breakout, donchian v2 ou similar) — escopo requer novo código em src/alpha_forge/strategies/. ADR de escopo a seguir.
