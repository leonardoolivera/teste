# 0155 — Série CZ19 closeout: filter internals ultra-plano 0/6, Bollinger family 100% sensibilizada

**Status:** Accepted — refutação screening. Filter internals canônicos robustos. Padrão 42 finalizado com 4 eixos Bollinger.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0154 (pré-reg), ADR-0151 (CZ17 threshold), Padrão 42 expandido

## Resultado

| Tag | Combo | filter ns | Tr | Sh | Lift | PnL% |
|---|---|---:|---:|---:|---:|---:|
| CZ19.1 | SOL short | 1.0 | 77 | 2.85 | +0.14 | 14.47 |
| CZ19.2 | SOL short | 2.0 | 125 | 2.88 | +0.17 | 19.78 |
| CZ19.3 | ETH short | 1.0 | 53 | 1.65 | -0.75 | 6.28 |
| CZ19.4 | ETH short | 2.0 | 101 | 2.22 | -0.19 | 12.01 |
| CZ19.5 | SOL long | 1.0 | 27 | 1.35 | -1.05 | 3.40 |
| CZ19.6 | SOL long | 2.0 | 63 | 1.68 | -0.72 | 5.90 |

Maior lift positivo: SOL short ns=2.0 (+0.17). Range de lift: [-1.05, +0.17].

## Avaliação gate

Gate ADR-0154:
- Upgrade convergente: ≥2/6 lift > 0.5 → CZ20
- Signal divergente: 1/6 lift > 0.5 → Padrão 41 bloqueia
- Refutação screening: 0/6 lift ≥ 0.5

**0/6 → refutação screening.**

## Interpretação

### Superfície ultra-plana em SOL short

SOL short: ns=1.0 (+0.14) e ns=2.0 (+0.17) praticamente iguais ao canônico 1.5. Threshold bps=300 está governando a seleção; internals do filter são quase irrelevantes. Isso é consistente — filter width faz combinação de dois effects (ns determina multiplicador desvio-padrão; bps determina threshold final), e no range estudado o threshold final relativo varia pouco.

Exemplo concreto: ns=1.0, bps=300 → bandwidth = 2×1.0×σ/ma precisa ≥ 0.03 (3%). ns=2.0, bps=300 → bandwidth = 2×2.0×σ/ma precisa ≥ 0.03. Na prática seleciona regimes similares (ambos captam alta vol).

### Ordem de degradação nos outros combos

ETH short e SOL long: ns=1.0 pior que ns=2.0 (bandas estreitas → threshold passa em mais regimes de baixa vol que não têm mean-reversion clara). SOL long com só 27 trades em ns=1.0 — sample muito pequeno.

## Padrão 42 expandido (final): 4 eixos Bollinger mapeados

Consolidação:

| Eixo | Série | Screening result | Range lift | Interpretação |
|---|---|---|---|---|
| Engine num_std | CZ14 | 1/6 divergente | [-1.82, +2.23] | Outlier refutado CZ15 |
| Engine window | CZ16 | 0/6 refutação | [-4.58, +0.45] | Rápido colapsa |
| Filter threshold | CZ17 | 0/6 refutação | [-1.14, +0.05] | Superfície plana |
| Filter internals | CZ19 | 0/6 refutação | [-1.05, +0.17] | Superfície ultra-plana |

Ordenação de sensibilidade empírica (por variância cross-combo):
1. **Engine window** — variância 5.0 (alta). Rápido destrói (-4.58 lift).
2. **Engine num_std** — variância 4.0 (alta, outliers). Outliers mas refutados cross-window.
3. **Filter threshold** — variância 1.2 (baixa). Canônicos levemente melhores.
4. **Filter internals** — variância 1.2 (baixa). Quase indistinguível.

**Regra prática final (Padrão 42 consolidado)**: para procurar upgrades em famílias mean-reversion, começar sempre pelos engine params (bounds explorado em CZ10-13, window em CZ16, period/num_std em CZ14/CZ18). Filter params dão menos retorno esperado e podem ser pulados quando orçamento de runs for escasso.

## Bollinger family: exploração completa

Canônicos w=20/30, ns=1.5, filter w=30/ns=1.5/bps=300/250 são robustos em 4 eixos paramétricos. Não há upgrade disponível via sensibilidade de 1 knob.

Próximas frentes possíveis (fora do escopo de 1-knob sensibilidade):
- Composição de filters (AND/OR)
- Cross-timeframe (HTF signals + LTF execution)
- Cross-asset/cross-engine meta-análise (correlação do stack)
- Ingest novos assets (DOT/AVAX/LINK) para matriz expandida

## Decisão

- Nenhuma edição manifest
- Bridge **não postado**
- Arquivar Bollinger sensibilidade 1-knob como "exploração completa, nada a ganhar"

## Ação executada

- ✅ ADR-0154 pré-reg
- ✅ CZ19 runs (6 runs)
- ✅ ADR-0155 closeout
- ✅ Padrão 42 finalizado com 4 eixos mapeados
- ⏳ STATE.md tarde-12 entry

## Não-alvo

- Não testar filter window interno (Padrão 42: internals ultra-plano, prior ≈ 0 de achado)
- Não re-testar knobs já mapeados
- Não promover nada sem gate convergente
