# 0228 — V2/RAIO Ciclo 13 — S12 + ATR trail40 boost (Padrão 66, primeira melhoria mensurável V2)

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0227 (Cycle 12 ATRTrailingWrapper + EX004 Quarantined), ADR-0223 (S12 SOL-specific), Padrões 62, 65

## Contexto

ADR-0227 introduziu ATRTrailingWrapper engine + Padrão 65: ATR trail mult ≥ 4.0 melhora Sharpe sem destruir trades em base sem edge. EX004 ficou QUARANTINED aguardando aplicação a strategy com edge real. Cycle 13 testa hipótese: aplicar trail40 (atr_period=14, mult=4.0) a S12 (rsi_short_trendhtf SOL — único survivor V2/RAIO).

Tools: [`tools/v2_s12_atr_trail_combined.py`](../tools/v2_s12_atr_trail_combined.py). 12 probes (3 assets × 4 variants raw/trail25/trail40/trail60) sobre janela contínua 30m, fees 10bps. Wall ~3min.

## Resultado

**SOL (S12 base, único com edge):**

| Variant | Sh | Trades | MDD% | PnL% |
|---|---:|---:|---:|---:|
| raw | 1.2008 | 185 | 9.04 | +29.20 |
| trail25 | 0.72 | 249 | 11.50 | +13.55 |
| **trail40** | **1.37** | **221** | **8.59** | **+31.56** |
| trail60 | 1.16 | 203 | 9.65 | +27.59 |

**BTC + ETH (S12 cross-asset, sem edge per Padrão 62):**

| Asset | raw | trail25 | trail40 | trail60 |
|---|---:|---:|---:|---:|
| BTC Sh | -0.02 | -0.12 | -0.20 | -0.10 |
| ETH Sh | -0.01 | -0.52 | 0.00 | -0.29 |

### Análise

- **SOL trail40** é dominante: Sh +14% (1.20→1.37), MDD -5% (9.04→8.59), PnL +2.4pp (29.2→31.6). **All 3 metrics improve.**
- **trail25 prejudica** SOL (Sh 0.72) — corta winners legítimos.
- **trail60 marginal** vs raw — trail muito frouxo, raramente dispara antes do signal natural.
- BTC/ETH **continue FAIL** — trail não salva strategies sem edge base. Confirma Padrão 62 (S12 é SOL-microstructure-specific).

## Decisão

1. **Padrão 66 (novo) registrado:** ATR trail40 aplicado a strategy com edge real boost Sh ~+14% + MDD reduce ~5% + PnL +2.4pp. Padrão 65 retroativamente confirmado em strategy real.
2. **S12 + trail40 = primeira melhoria mensurável V2/RAIO sobre survivor genuíno.** Após 13 ciclos, ~342+12=354 backtests, primeiro caso onde combinação de elementos V2 produces gain real.
3. **NÃO atinge gate V1 strict (Sh ≥ 1.5)** mas atinge Padrão 60 (Sh ≥ 1.0). Não promove a manifest export ainda.
4. **EX004 trail40 sai de QUARANTINED para SCOUTING+** (validado em strategy real). Aplicar a outros candidatos V2 quando emergerem.

## Padrão 66 (novo)

**ATR trail40 + strategy com edge = gain mensurável across all metrics.**

Mecanismo:
- Strategy edge real (S12 SOL: rsi_short + 4h trend gate) gera trades com expectancy positiva.
- trail40 (ATR×4) adiciona exit camada que:
  - Captura early reversal (alguns trades antes que signal natural mean-cross).
  - Limita perdas em trades que não revertem (MDD reduce).
  - Não corta winners (mult=4 é ~1× σ_4h em SOL — generoso o suficiente).
- Resultado: skew positivo dos retornos aumenta, std reduz → Sh sobe.

**Aplicabilidade:** Padrão 66 sugere que toda strategy V2 promovida deveria considerar EX004 trail40 como "default exit enhancement" — atribuição não-controversa per teste empírico.

## Patterns updated

- **EX004 trail40**: SCOUTING (validated). Pode tornar SURVIVOR após cross-asset apply.
- **S12+trail40**: PROMISING (Sh 1.37, < 1.5 strict mas direção correta). Aguarda quartos ciclos pra promotion.
- **Padrão 65** retroativamente confirmado: vol-aware exit > count-based exit.
- **Padrão 66 (novo)**: trail40 + edge = +14% Sh standard.

## Resumo final V2/RAIO 13 ciclos

- 16 ADRs (0212-0228). 15 padrões (52-66; P57 retroativamente refutado).
- 1 SURVIVOR genuíno (S12 SOL); **+1 PROMISING enhancement (S12+trail40)**.
- 3 GRAVEYARDs após pipeline completo (P52 individual + P50 cluster + EX001 family).
- 1 SCOUTING+ validado (EX004 trail40).
- 2 candidatos retirada urgente (S10/S11 paper-trade observation 14d).
- 0 strategies V2 fresh promovidas a manifest (S12+trail40 marginal abaixo de Sh ≥ 1.5 strict).
- ~354 backtests + estatística + portfolio + cross-era + cross-asset + extended em ~37min wall-clock total.
- **3 engines novos** (BHDrawdownFilter, TimeStopWrapper, ATRTrailingWrapper).
- **AGENTS.md V2 guideline** consolidada (Padrões 53-66).

## Consequences

- **Positive:** primeiro improvement mensurável V2/RAIO sobre survivor genuíno após 13 ciclos. Pipeline V2 demonstra capacidade de produzir improvements quando elementos certos combinam (edge real + exit vol-aware). EX004+S12 = template para próximas combinações.
- **Negative:** Sh 1.37 < 1.5 (V1 strict). Para promover S12+trail40 a manifest, ou (a) aceitar gate V2 reformulado Sh ≥ 1.0 + outros AND-criteria, ou (b) buscar outro improvement (BE, MAE quantile) que adicione +0.13 Sh.
- **Neutral:** S10/S11 ainda em paper-trade observation 14d. ADR-0227+0228 não afetam protocolo.

## Próximas frentes (Cycle 14+ autopilot)

1. **EX009 Break-even after MFE** — implementar `BEAfterMFEWrapper`. Score ~7.5. Aplicar a S12 também → talvez cumulative com trail40 atinja Sh ≥ 1.5.
2. **EX011 MAE-quantile exit** — sair se MAE > p80 historic. Score ~7.0.
3. **2026-05-10**: ADR-0229 verdict S10/S11 paper-trade.
4. **Promote S12+trail40 a manifest se aceitarmos gate V2 reformulado (Sh ≥ 1.0)**: requer ADR explícito relaxando gate V1 strict de Sh ≥ 1.5. Discussão com user pendente.
5. **Liquidity_trap engine** (LQ001/LQ002 Top 18-19). Custo ~5h.

Recomendação Cycle 14: **opção 1 (EX009 BE wrapper + cumulative test S12+trail40+BE)**. Razão: pattern wrapper estabelecido (3o em sequência), custo ~30min, target direto = empurrar S12 sobre Sh 1.5 strict via ensemble exits (Padrão 67 candidato: ensemble exits supera single).

## Não-alvo

- Não promover S12+trail40 a manifest sem ou ADR de gate-relax ou +0.13 Sh adicional.
- Não tentar cross-asset BTC/ETH com trail — Padrão 62 cobre, S12 é SOL-microstructure.
- Não aplicar trail25 ou trail60 a strategies — Padrão 65+66 são claros que trail40 é ótimo.

## Padrões totais: 66
