# 0231 — V2/RAIO Ciclo 16 — LiquidityTrapStrategy engine + LQ001/LQ002 GRAVEYARD + Padrão 69

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0230 (Cycle 15 S12 Sensitivity P68), ROADMAP_V2 (LQ001-LQ027 family Top 18-19), ADR-0226+0227 (engines novos pattern)

## Contexto

Após 15 ciclos refutando V1 inheritance via Padrões 60-68, conclusão: pipeline V2 não vai produzir candidate genuíno apenas combinando V1 engines + V2 exits. Para resultado real, mecanismo causal **fundamentalmente novo**. Cycle 16 implementa **LiquidityTrapStrategy** — primeira engine V2 com lógica não-derivada de bollinger/rsi/etc.

## Implementação

[`src/alpha_forge/strategies/families/liquidity_trap/strategy.py`](../src/alpha_forge/strategies/families/liquidity_trap/strategy.py):

- LQ001 (false break high → ENTER_SHORT): `high[t-1] > prev_high AND close[t-1] < prev_high`.
- LQ002 (false break low → ENTER_LONG): `low[t-1] < prev_low AND close[t-1] > prev_low`.
- prev_high/low: max/min sobre `lookback` bars excluindo a barra t-1.
- Exit: close cruza SMA(`exit_mean_window`) (proxy VWAP-like, dentro de 0.1% tolerance).
- Bidirectional (LQ001+LQ002 conjunto). `long_only=True` filtra para apenas LQ002.

CLI flags: `--lq-lookback N --lq-exit-mean-window M`. AVAILABLE_STRATEGIES estendido. Smoke test ✓: SOL 30m gera 828 trades em 4 folds (alto trade count — primeira red flag).

## Scout LQ (RAIO Nível 1)

Tools: [`tools/v2_lq_scout.py`](../tools/v2_lq_scout.py). 18 probes (3 assets × 3 lookbacks × 2 variants raw/trail40) sobre janela contínua 30m, fees 10bps. Wall ~26s.

### Resultado catastrófico

| Asset | Lookback | raw Sh | trail40 Sh | trade ct | MDD% | PnL% |
|---|---:|---:|---:|---:|---:|---:|
| BTC | 15 | -3.10 | -3.47 | 1083+1128 | 41-44% | -39 a -42% |
| BTC | 20 | -2.10 | -2.38 | 906+950 | 30-32% | -27 a -29% |
| BTC | 30 | -1.42 | -1.69 | 666+703 | 22-24% | -17 a -20% |
| ETH | 15 | -2.22 | -2.49 | 1005+1064 | 45-48% | -41 a -44% |
| ETH | 20 | -1.57 | -1.69 | 844+895 | 35-36% | -29 a -30% |
| ETH | 30 | -1.40 | -1.43 | 625+667 | 30% | -24% |
| SOL | 15 | -0.40 | -0.41 | 977+1023 | 26% | -14% |
| **SOL** | **20** | **+0.17** | +0.13 | 828+866 | 22% | +1.8 a +2.9% |
| SOL | 30 | +0.05 | +0.04 | 641+675 | 14-15% | -0.7% |

**Pass count Padrão 60: 0/18.**

### Análise

- **Trade count 640-1130** por probe — LQ dispara excessivamente. Exit signal "close cruza SMA10" é frouxo demais; cada flip de direção gera novo trade. Em janela 30m com 21,672 bars, ~5% das bars geram signal — alto demais.
- **Fees 10bps × 1000 trades ≈ 10% drag** elimina qualquer edge marginal.
- **Trail40 piora** (consistent com over-trading): cada trail breach + reentry agrega slippage.
- **SOL menos catastrófico** porque vol natural amortece signal-noise; lookback=20 dá Sh marginalmente positivo (+0.17) mas com MDD 22% inaceitável.

## Decisão

1. **LQ001/LQ002 naive implementation → GRAVEYARD em Scout.**
2. **LiquidityTrapStrategy engine preservado** (não revertido) — implementação serve como base para variantes filtradas (LQ005, LQ006, LQ011, LQ027 do roadmap V2 que adicionam volume/wick magnitude/HTF filter).
3. **Padrão 69 (novo) registrado.**

## Padrão 69 (novo) — Microstructure naive sem filter destrói edge via fees

**Implementações naive de hipóteses microstructure (false breakout, wick rejection) sem filters de magnitude/contexto geram noise excessivo.**

Mecanismo:
- Definição estrita "high > prev_high AND close < prev_high" tem alta freq de match (cada vez que mercado quebra rastro e retorna).
- Em crypto 30m, rastros são quebrados frequentemente sem follow-through real.
- Sem filters (volume confirmation, ATR magnitude, wick rejection size, HTF context), match ≠ "real liquidity trap".
- Resultado: 700-1100 trades em 18 meses → fees consomem edge.

**Implicação ROADMAP_V2:** LQ001/LQ002 (Top 18-19 V2) explicitamente sob risk de match-without-context. Para implementação valid:
- LQ005 (wick rejection > 2 ATR): adicionar filter wick magnitude.
- LQ006 (wick + volume): adicionar volume relativo confirm.
- LQ011 (extension + volume): magnitude + volume joint.
- LQ027 (1h sweep aligned 4h level): HTF context confluence.

**Padrão 69 retroativo:** ROADMAP_V2 hipóteses microstructure implementadas sem filters genuínos = estatisticamente similar a entry random com over-trading. Para survive Padrão 60, **filters causais são parte essencial do mecanismo**, não enhancement.

## Resumo final V2/RAIO 16 ciclos

- 19 ADRs (0212-0231). 18 padrões (52-69; P57 retroativamente refutado).
- 1 SURVIVOR genuíno (S12 SOL — V1 inheritance, agora QUARANTINED P68).
- 6 GRAVEYARDs/Refutações pipeline-completo (P52, P50 cluster, EX001, EX009 em S12, P68 S12+trail40, P69 LQ001/002 naive).
- 1 SCOUTING+ validado (EX004 trail40).
- 2 candidatos retirada urgente (S10/S11 paper-trade observation 14d).
- 0 strategies V2 fresh promovidas a manifest.
- ~416 backtests + estatística + portfolio + cross-era + cross-asset + extended em ~47min wall-clock total.
- **5 engines novos**: BHDrawdownFilter + 3 wrappers exit_layer + LiquidityTrapStrategy.
- AGENTS.md V2 guideline expandida (Padrões 53-69).

## Consequences

- **Positive:** primeira engine V2 fundamentalmente nova implementada (não-derivada V1). Pattern para futuros engines microstructure validado. Padrão 69 é gate adicional crítico para family LQ futura.
- **Negative:** LQ naive zero edge — caminho microstructure exige feature engineering pesada (volume, wick mag, HTF context) ANTES de scout. Próximo LQ scout precisa LQ005/006 com filter genuine.
- **Neutral:** pipeline V2 16 ciclos ainda zero promotions. Confirma que universo (engines + datasets atuais) requer **dados ou features novas** para produzir survivor.

## Próximas frentes (Cycle 17+ autopilot)

1. **2026-05-10**: ADR-0232 verdict S10/S11 paper-trade.
2. **LQ005 wick rejection magnitude** — adicionar filter wick > N×ATR à LiquidityTrapStrategy. Mais 10-20 LoC; scout sobre 18 probes ~5min.
3. **Implementar volume signal em LiquidityTrapStrategy** (LQ006): require dataset com volume ≠ zeros (verificar). Se OK, scout LQ006.
4. **ADR de gate-relax discussion** — pendente input user. 16 ciclos zero promotion + 9-criteria gate AND-conjunto pode ser overly strict.
5. **EX011 MAE-quantile exit** (4o wrapper) — alternativa exit research.
6. **Sizing_layer engine** (PS001-027) — ADR-0030 invariants restringem; pesquisa permite com ADR.

Recomendação Cycle 17: **opção 2 (LQ005 wick magnitude filter)**. Razão: padrão escalável (engine pronto, só adicionar filter), custo baixo, e Padrão 69 explicit aponta filter como gate. LQ005 destrava family LQ V2.

## Não-alvo

- Não tentar mais variants LQ001/002 puro com diferentes lookbacks (Padrão 69 é claro).
- Não relax Padrão 60 strict para "salvar" LQ.
- Não revert LiquidityTrapStrategy — base para LQ005+ filtered.

## Padrões totais: 69
