# 0047 — Série CD closeout: Donchian + trend_htf (FAIL principal, lift forte corroborado)

**Status:** Accepted — closeout
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0043 (trend_htf), ADR-0045 (hipótese forward), ADR-0046 (pré-registro CD).

## Resultado

Três gates pré-registrados, resultados diferentes:

| Gate | Requisito | Resultado | Veredicto |
|---|---|---|---|
| 1-6 (piloto viável) | ≥6/9 | 1/9 | **FAIL** |
| 7 (lift BOTH fe>base AND mdd<base) | ≥6/9 | 6/9 | **PASS** |
| 8 (Sharpe>0 em ≥2/3 recortes 2025) | ≥2/3 | 2/3 | **PASS** |
| Overall | 1-6 AND 7 AND 8 | — | **FAIL** |

**Série CD FAIL no overall.**

Tabela completa:

| Tag | Asset | Período | filt trd | filt Sh | filt fe | filt MDD% | base Sh | base fe | base MDD% | lift both |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| CD.1 | ETH | 2023-H2 | 34 | -0.77 | 9875 | 3.37 | 0.06 | 10007 | 2.64 | ✗ |
| CD.2 | BTC | 2023-H2 | 35 | -0.82 | 9895 | 1.96 | 1.09 | 10215 | 2.77 | ✗ |
| **CD.3** | **SOL** | **2023-H2** | **33** | **3.15** | **11591** | **4.45** | 2.02 | 11104 | 5.09 | **✓** |
| CD.4 | ETH | 2025-H1 | 31 | 0.25 | 10057 | 4.30 | -0.29 | 9882 | 7.60 | ✓ |
| CD.5 | BTC | 2025-H1 | 42 | -0.18 | 9972 | 2.47 | 0.70 | 10145 | 2.47 | ✗ |
| CD.6 | SOL | 2025-H1 | 34 | 0.89 | 10214 | 2.48 | -2.34 | 9072 | 10.61 | ✓ |
| CD.7 | ETH | 2025-H2 | 29 | -3.61 | 9465 | 5.70 | -2.01 | 9449 | 8.43 | ✓ |
| CD.8 | BTC | 2025-H2 | 33 | -5.24 | 9444 | 5.65 | -4.17 | 9295 | 7.61 | ✓ |
| CD.9 | SOL | 2025-H2 | 33 | -3.00 | 9391 | 8.05 | -3.05 | 9012 | 13.31 | ✓ |

CD.3 único PASS completo. 6/9 lift both. Dados crus: `exports/diag/cd_series_summary.json`.

## Leitura

### 1. Hipótese forward ADR-0045 **corroborada direcionalmente**

> "`trend_htf` + trend-following gera edge aditivo, porque direção do filtro se alinha."

CD confirma com força comparada a CC:
- **Lift both 6/9** (CC tinha 3/9 no lift both se aplicássemos critério equivalente)
- **SOL 2025-H1**: Sharpe flipou de **-2.34 → +0.89**, mdd caiu de 10.61% → 2.48%, fe flipou de 9072 → 10214. Flip quádruplo numa janela — não é ruído.
- **SOL 2025-H2**: Sharpe manteve negativo (mercado bear), mas mdd caiu de 13.31% → 8.05% e fe de 9012 → 9391. Filtro protegeu capital numa janela onde Donchian puro sangrava.

O alinhamento direcional faz o que a teoria prevê.

### 2. Mas não é suficiente pra piloto standalone

Gate 1-6 FAIL 1/9. Razões:
- **2023-H2 ETH/BTC**: baselines eram **melhores** sem filtro. Donchian puro ETH 2023-H2 teve Sharpe 0.06 (neutro), BTC 1.09 (bom). Filtro HTF cortou trades em bull moderado, produzindo amostra menor e Sharpe pior. CD.2 BTC foi onde o filtro **destruiu Sharpe 1.09 → -0.82** — em bull consistente, HTF bias long redundante corta ruído útil pra sharpe positivo de breakout.
- **2025-H2 todos**: mercado dominantemente bear. Até com filtro (que reduz mdd), retorno absoluto fica negativo — breakout em bear não prospera mesmo protegido. Filtro vira "reduzir perda" só, não gerar ganho.
- **Único PASS (CD.3)**: SOL 2023-H2 é outlier — altseason bull brutal. Sharpe 2.02 baseline → 3.15 filtered. Piloto isolado não vira manifest (regra anti-curve-fitting: N=1 é sorte).

### 3. Distribuição do efeito

O padrão agora visível através de CC + CD:

| Regime de mercado | Efeito do `trend_htf` |
|---|---|
| Bull forte (SOL 2023-H2) | **Amplifica ganho** (Sharpe 2.02 → 3.15) |
| Bull moderado (ETH/BTC 2023-H2, BTC 2025-H1) | **Destrói edge** (corta trades úteis) |
| Chop (SOL 2025-H1) | **Reverte para positivo** (edge real aparece aqui) |
| Bear forte (todos 2025-H2) | **Protege capital** mas não gera retorno |

Filtro HTF **não é edge universal** — é **modulador de regime**. Só gera manifest-worthy piloto no cruzamento exato: trend-following + altseason bull forte. Isso não é estratégia, é "torcer pra 2021/2023-H2 voltar".

## Decisão

1. **Arquivar Série CD**. Donchian 20/10 + trend_htf não vai pra manifest. CD.3 isoladamente não qualifica (N=1).

2. **Não abrir Série CE** (testar `and(trend_htf, atr_regime)` no Donchian). Os 3 gates conjuntos já responderam a pergunta. Compor com atr_regime poderia melhorar marginalmente mas não muda conclusão estrutural: edge cross-período **não existe** com este vocabulário de filtros + estratégias.

3. **Terceiro arquivamento em série** (CA, CB, CC, CD). Padrão pede meta-análise, não próxima série.

4. **`TrendHTFRegimeFilter` permanece no código**. Validado produção; futuro regime classifier ou sizing dinâmico poderá usá-lo. Código é barato de manter.

## Consequences

**Positive:**
- Três gates conjuntos (1-6, 7, 8) separaram "piloto viável" de "arquitetura útil direcionalmente". Permite fechar a série FAIL com informação rica, não veredicto binário.
- Hipótese forward ADR-0045 **foi testada** — confirmada direcionalmente (6/9 lift, Gate 8 PASS), rejeitada como edge standalone. Isso é valor: agora sabemos que `trend_htf` sozinho não salva, o que muda a agenda.
- Pré-registro aplicado consistentemente em 4 séries (CA/CB/CC/CD). Método funciona: zero tentação de mover régua mesmo com dados "quase bons".

**Negative:**
- 4 séries cross-period consecutivas FAIL. Manifest continua com 1 piloto (Bollinger 20/1.5 + atr_regime 2024-H2 baseline).
- Hipótese "filtro regime salva edge LTF" foi testada em duas direções (mean-rev CC e trend-follow CD). Ambas falharam como standalone. Próximas séries na mesma linha serão diminishing returns — precisa novo eixo.

**Neutral:**
- Dois filtros sofisticados (`BollingerWidthFilter`, `TrendHTFRegimeFilter`) no código sem piloto canônico que os use. Precedente neutro: família disponível para composições futuras, custo zero.

## Sinal forte pra meta-análise

Com 4 FAILs cross-period, o padrão é claro demais pra continuar na mesma agenda. O próximo passo racional não é Série CE — é **consolidar aprendizado** das 4 séries e revisar a estratégia de pesquisa. Entregáveis candidatos:

1. **Meta-análise CA/CB/CC/CD** — padrões comuns de falha, taxonomia de modos, implicações pra vision/01-product.md.
2. **Audit do único manifest** (Bollinger 20/1.5 + atr_regime 2024-H2) — esse piloto sobreviveu onde 4 séries falharam. É genuíno ou artefato?
3. **Revisão do vocabulário de filtros** — os 4 filtros existentes capturam dimensões suficientes? Falta algo estrutural (regime classifier, cross-asset, macro)?
4. **Revisão do vocabulário de estratégias** — 3 estratégias (Donchian, Bollinger, RSI) todas long-only, todas LTF. Short side + HTF-native strategies + multi-asset são eixos ausentes.

Não vou abrir nenhum desses automaticamente. Meta-análise é trabalho discreto, não sweep — merece sua própria sessão com decisão explícita do usuário.

## Arquivos de referência

- Pré-registro: `decisions/0046-series-cd-donchian-trend-htf-cross-period-preregister.md`
- Sweep: `tools/run_cd_sweep.py`
- Summary: `tools/summarize_cd.py`
- Dados: `exports/diag/cd_series_summary.json`
- Runs: `results/validation/cd-don-20-10-*` (18 diretórios)
