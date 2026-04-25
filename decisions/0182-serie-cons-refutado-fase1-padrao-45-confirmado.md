# 0182 — Série CONS closeout Fase 1: refutada, Padrão 45 re-confirmado

**Status:** Accepted — CONS/BB-short-pyramid arquivado em Fase 1.
**Date:** 2026-04-21
**Deciders:** Usuário (piloto automático) + agente
**Relates to:** ADR-0180 (runtime v4 pyramid), ADR-0181 (pré-reg), ADR-0172 (Keltner closeout + Padrão 45), Padrão 41

## Resumo executivo

Gate ADR-0181 Fase 1 (Sh≥1.5 AND sequences≥10, ≥2/3 assets): **1/3** — ETH isolado outlier. BTC catastrófico, SOL nulo. Padrão 45 (ETH-only outlier em engine naked/light-filter) confirmado em terceiro engine (DE, KE, agora CONS).

## Resultados Fase 1

| Tag | Asset | Trades | Seqs | Sharpe | PnL% | Gate |
|---|---|---:|---:|---:|---:|:---:|
| CONS.1 | BTC 2025-H1 | 84 | 38 | **-3.175** | -46.98 | ✗ |
| CONS.2 | ETH 2025-H1 | 36 | 25 | **+3.349** | +30.47 | ✓ |
| CONS.3 | SOL 2025-H1 | 11 | 11 | **-0.624** | -2.50 | ✗ |

**1/3 pass** vs gate 2/3 — **FAIL**.

## Interpretação

### Pyramid funciona mecanicamente, mas amplifica em ambos os lados

Dev v4 completou 3 runs sem erro (engine + filter + 26/26 unit tests). Stack de tranches abriu/fechou conforme contrato:
- Seqs BTC=38, ETH=25, SOL=11 → tranches convertidos em sequências distintas (exit_timestamp único).
- Trades/seqs ratio 2.2-2.0 em BTC/SOL e 1.44 em ETH sugere que pyramid pegou 2-3 tranches antes do regime flip.

Portanto **v4 contract está funcional**. O problema é a *hipótese de edge*, não a execução.

### BTC -47% catastrófico é assinatura de "BB short em range wide"

BTC 2025-H1 teve múltiplos momentos de ruptura da banda superior (bull squeeze) em janelas curtas. Pyramid 5×20% com leverage 5× significa exposição efetiva até 5×5=25×capital em pior caso de stack cheio. Quando o filter demora 1 bar para detectar breakout (rearm=1), o tail do stack come PnL catastrófico — confirmado empiricamente pelo -47% em 84 trades.

Implicação: **pyramid+leverage em mean-reversion short sem hard-stop é patologicamente assimétrico** quando o regime muda. Mesmo com filter bollinger_width max=200bps que em teoria cortaria sinal em breakout, o lag de 1 bar (rearm) destrói a proteção.

### ETH +30% isolado = Padrão 45 (v4 idem v3)

Padrão 45 (ADR-0172): "Engines vanilla em crypto 1h tendem a produzir Padrão 41 em ETH 2025-H1. Adicionar filter canônico normaliza sinal cross-asset, mas não cria edge ≥1.5."

CONS.2 ETH Sh=3.35 com filter bollinger_width max_width_bps=200 confirma: mesmo com v4 pyramid, ETH 2025-H1 continua outlier. Em BTC/SOL o mesmo engine+filter destrói capital. **N=3 engines (DE trend_htf, KE Keltner, CONS BB-pyramid) todos mostram ETH-outlier sem reprodução cross-asset.**

### Padrão 45 re-confirmado → promover a Padrão consolidado

Evidência agora N=3 engines independentes, 3 famílias distintas (trend, mean-rev on ATR, mean-rev on stdev+pyramid). Formalizar:

**Padrão 45 (consolidado):** "ETH 2025-H1 é outlier sistemático em engines mean-reversion/trend-following 1h crypto. Qualquer descoberta single-asset de Sh≥1.5 em ETH 2025-H1 *sem replicação em BTC E SOL na mesma janela* deve ser tratada como evidência de Padrão 41, não de edge estrutural. Filter+engine normaliza mas não destrava edge cross-asset."

Implicação operacional: **Futuros pré-regs devem exigir cross-asset desde Fase 1** (não relaxar para single-era) quando a hipótese se basear em behavior de ETH observado.

## Decisão

- **CONS Fase 1 refutada**. Não prosseguir Fase 2 cross-era.
- **Runtime v4 pyramid_equity_based preservado** — infraestrutura vale manter (engine + filter + 26/26 testes). Pode ser reutilizado em hipótese futura diferente (ex: pyramid_equity + long-only + trend_htf, ou timeframe 4h).
- **Manifest v4 schema NÃO será escrito nesta sessão** — ADR-0180 previa dev somente se Fase 1 passasse. Fica como dev-on-demand.
- **Bridge inbox bot**: postar "v4 dev stand-down; v3 stack inalterado" para cancelar a expectativa de adapter.
- **Stack 13 combos inalterado.**
- **Padrão 45 promovido** a padrão consolidado (N=3 engines independentes).

## Implicação para handoff bot

Objetivo permanece handoff ao bot. CONS era a última frente cheap single-session. Frentes restantes todas com custo elevado ou prior pessimista:

1. **Pyramid long-only + trend_htf** (reutilizar v4 infra): pode destravar assimetria; **prior moderado ~25%**.
2. **BB short v4 pyramid 4h timeframe** (menos trades, pegar menos falsos breakouts): prior moderado ~20%.
3. **Orderbook**: alto custo, não single-session.
4. **Multi-asset cross-sectional**: mudança de framework.

Alternativa forte: **parar pesquisa de novos engines, exportar manifest v6.2 do stack atual 13 combos**. Stack existente atende ADR-0030, handoff já possível. User decide.

## Não-alvo

- Não rodar Fase 2 CONS cross-era (gate 1/3 em single-era torna Fase 2 prior ~5%).
- Não implementar manifest v4 schema nesta sessão.
- Não testar variantes 4h/long-only nesta sessão sem user input (diminishing returns sem prior forte).

## Ação executada

- ✅ ADR-0180 runtime v4 pyramid
- ✅ ADR-0181 pré-reg CONS
- ✅ Dev completo engine + filter + CLI + 26/26 testes
- ✅ 3 runs CONS.1-3 executados
- ✅ Summarize + gate check
- ✅ ADR-0182 closeout
- ⏭️ Bridge post "v4 stand-down" (próximo)
- ⏭️ STATE.md update (próximo)
