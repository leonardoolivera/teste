# 0161 — Série DB closeout: AND(width, trend_htf) refutado + Padrão 17 FAIL em RSI

**Status:** Accepted — dupla refutação. Composição AND não viável.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0160 (pré-reg), Padrão 17 (pernas isoladas)

## Resultado

| Tag | Combo | Trades | Sharpe | Baseline | Lift | PnL% |
|---|---|---:|---:|---:|---:|---:|
| DB.0 | RSI+trendhtf isolado BTC (perna) | 46 | **-0.348** | — | — | -0.96 |
| DB.1 | RSI+AND BTC | 26 | 1.182 | 1.69 | -0.51 | 2.10 |
| DB.2 | RSI+AND ETH | 47 | 1.262 | 1.96 | -0.70 | 4.55 |
| DB.3 | RSI+AND SOL | 50 | 1.653 | 2.02 | -0.37 | 7.75 |

## Avaliação dupla

**1. Padrão 17 FAIL**: DB.0 (trend_htf ISOLADO em RSI 30/70 BTC) Sh=-0.35, PnL=-0.96%. trend_htf isolado em RSI 30/70 BTC **não tem edge** — destrutivo. Padrão 17 exige que **ambas pernas passem isoladas** antes de composição; falha aqui invalida AND mesmo se AND funcionasse.

**2. Gate upgrade FAIL**: DB.1-3 lift = (-0.51, -0.70, -0.37). 0/3 > +0.5. Refutação screening.

Dupla falha: AND composition não funciona E Padrão 17 bloqueia procedimentalmente.

## Interpretação

### trend_htf SMA50 4h é asset-específico em RSI

Recap dos resultados RSI + trend_htf ISOLADO:
- **SOL 2025-H1 RSI 25/75 + trendhtf**: Sh=2.00 (cz10.5, live)
- **BTC 2025-H1 RSI 30/70 + trendhtf**: Sh=-0.35 (DB.0, novo)

Mesma trend_htf, mesmo asset-class (crypto majors 1h), janela sobreposta. Diferença = RSI bounds (25/75 vs 30/70) E asset (SOL vs BTC). Possíveis explicações:
- BTC tem tendências 4h menos limpas que SOL em 2025-H1 (SOL teve downtrend mais persistente)
- 30/70 é menos seletivo que 25/75; com trend_htf top-down, entradas 30 são prematuras
- Interação específica RSI-bounds × asset-vol

Insight: **"SMA50 4h short-only trend_htf é edge asset-específico, não universal** (Padrão 41 aplicável — era-específico/asset-específico).

### AND degrada porque interseção corta demais

DB.1 só 26 trades em 6 meses BTC (vs 77 do width-só baseline). trend_htf corta ~66% dos trades. Mesmo que cada trade remanescente fosse melhor, perda estatística domina. AND = min(edges das pernas), não soma.

### Heurística informal: AND só ajuda se **ambas pernas têm edge forte isolado**

Width BTC isolado: Sh=1.69 (edge). trend_htf BTC isolado: Sh=-0.35 (anti-edge). AND herda o pior — **filtro anti-edge arrasta para baixo** mesmo com filter bom como parceiro. Generalizável: AND preserva/amplifica **pior perna**, não melhor.

Isso formaliza Padrão 17 empiricamente: sem FAIL isolado positivo das DUAS pernas, AND é irrelevante.

## Decisão

- Nenhuma edição manifest
- Stack permanece canônico RSI+width e RSI+trendhtf ambos via combos separados (Padrão 43: assim já está diversificado)
- Não testar OR composição sem ADR dedicado (escopo diferente)
- **AND composição** arquivada como linha de pesquisa: sem FAIL isolado de trend_htf ampliado, não há espaço para ativá-la

## Ação executada

- ✅ ADR-0160 pré-reg
- ✅ 4 runs DB
- ✅ ADR-0161 closeout

## Não-alvo

- Não varrer outros (asset, bounds) para encontrar trend_htf BTC isolado que passe (escopo Padrão 41, janela-específica)
- Não OR-compose sem hipótese nova
- Não tocar stack

## Próxima frente

Frente 4 (ingest DOT/AVAX/LINK): escopo bem maior. Decidir se prossegue agora ou arquiva backlog.
