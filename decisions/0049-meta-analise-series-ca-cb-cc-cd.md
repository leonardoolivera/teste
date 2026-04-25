# 0049 — Meta-análise das Séries CA/CB/CC/CD + audit manifest

**Status:** Accepted — síntese; nenhuma nova execução
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Consolida:** ADRs 0039 (CA pré-reg), 0040 (CA closeout), 0041 (CB pré-reg), 0042 (CB closeout), 0043 (trend_htf arquitetura), 0044 (CC pré-reg), 0045 (CC closeout), 0046 (CD pré-reg), 0047 (CD closeout), 0048 (audit manifest).

## Context

4 séries cross-period executadas em sequência (CA→CB→CC→CD), 46 runs totais. Todas falharam no gate principal. Entre elas, ADR-0043 introduziu `TrendHTFRegimeFilter`. ADR-0048 auditou o único manifest sobrevivente. O padrão é inequívoco demais pra continuar abrindo séries sem síntese.

Essa ADR consolida **o que foi testado, o que falhou, o que passou, e o que isso implica pro resto do projeto**.

## Inventário das séries

| Série | ADRs | Estratégia | Filtro | Matriz | Gate principal | Achado de segundo nível |
|---|---|---|---|---|---|---|
| CA | 0039, 0040 | Donchian 20/10 | atr_regime | 5 SOL recortes × 2 atr_bps = 10 | **FAIL 2/10** (só SOL 2023-H2) | Sharpe negativo em 8/10 recortes |
| CB | 0041, 0042 | RSI 14/30/70 | atr_regime | 3 ativos × 3 recortes = 9 | **FAIL 2/9** | "canary_only" em 2024 era artefato do rank híbrido ADR-0025 |
| CC | 0044, 0045 | Bollinger 20/1.5 | and(atr_regime, trend_htf 4h/50) | 3 × 3 = 9 filt + 9 base | **FAIL 0/9 principal; PASS 7/9 lift** | Filtro reduz risco mas não gera edge em mean-reversion |
| CD | 0046, 0047 | Donchian 20/10 | trend_htf 4h/50 (isolado) | 3 × 3 = 9 filt + 9 base | **FAIL 1/9 principal; PASS 6/9 lift_both; PASS 2/3 Gate 8** | trend_htf alinha direcionalmente com trend-following, mas magnitude insuficiente |
| Audit | 0048 | manifest v2 (Bollinger 30/1.5 + bollinger_width) | — | SOL 2024-H2 com 3 seeds + no-filter + SOL 2025-H1 = 5 | **Manifest validado** | Composição width+mean-rev é o único "filtro salva estratégia" confirmado do projeto; SOL 2025-H1 = Sharpe −0.15 |

Total: 46 runs de validate, 10 runs de audit.

## Padrão 1 — "PASS OOS único-recorte" não generaliza

CA (SOL 2023-H2 passou 2/2 variantes atr) e CD (SOL 2023-H2 único PASS completo, Sharpe 3.15) são ambos no mesmo recorte. SOL 2023-H2 foi altseason bull extremo — **qualquer estratégia long-only ganha lá**. O "sucesso" vira evidência sobre o regime, não sobre a estratégia.

Consequência metodológica: **um PASS cross-period tem que vir de ≥ 2 recortes com regimes distintos**. Um PASS isolado em bull forte é ruído de regime, não edge. Essa regra ficou implícita nos gates pré-registrados (≥6/9 etc), mas a ADR-0049 torna explícita: **N=1 passa nunca promove**.

## Padrão 2 — Filtros direcionais e estratégias direcionais têm assinatura previsível

Tabela cruzada das Séries CC e CD:

| Regime de mercado | Filtro + MeanRev (CC) | Filtro + TrendFollow (CD) |
|---|---|---|
| Bull forte (SOL 2023-H2) | 0 lift (Bollinger não precisa de filtro aqui) | +1.13 Sharpe (2.02 → 3.15) |
| Bull moderado (ETH/BTC 2023-H2) | Neutro | Destrói edge (BTC 1.09 → −0.82) |
| Chop (SOL 2025-H1) | +0.69 Sharpe flip (−0.45 → +0.24) | +3.23 Sharpe flip (−2.34 → +0.89) |
| Bear (2025-H2) | Reduz mdd, não vira retorno positivo | Reduz mdd, não vira retorno positivo |

**O filtro `trend_htf` é mais útil para trend-following que mean-reversion**, conforme predição teórica (ADR-0045). Mas a magnitude **nunca atinge gate pré-registrado de piloto standalone** — é modulador, não gerador de edge.

## Padrão 3 — O único "filtro salva edge" confirmado tem assinatura específica

Audit B (ADR-0048):
- Bollinger 30/1.5 puro em SOL 2024-H2: Sharpe 1.62, MC p5 **9968** (abaixo do gate 10000).
- Mesma config + `BollingerWidthFilter(30,1.5,250)`: Sharpe **2.50**, MC p5 10254.

Isso é **a única evidência positiva do projeto** de que um filtro arquitetural eleva estratégia LTF de canary_only pra semi_robust_2d. A assinatura da composição que funciona:

- **Filtro de volatilidade estrutural** (width, não ATR) — capta spread de bandas, ortogonal a ATR de candle.
- **Estratégia mean-reversion** (Bollinger, não breakout).
- **Recorte bull-com-chop** (SOL 2024-H2: trend up com pullbacks → squeeze de width desqualifica falso-sinal de pullback raso).

Observação crítica: `BollingerWidthFilter` e `BollingerMeanReversionStrategy` compartilham `window` e `num_std`. Não é filtro ortogonal — é **a própria estrutura do sinal filtrando-se** (pede width ≥250bps antes de operar mean-rev dentro dessa mesma banda). Isso pode ser feature ou bug conceitual — merece entrada na revisão de vocabulário.

## Padrão 4 — Regime temporal domina edge estrutural

Audit C mostrou que SOL 2024-H2 → 2025-H1, **engine idêntica**, Sharpe 2.50 → −0.15. Nenhuma mudança de parâmetro, nenhuma mudança de código. **O regime 2025-H1 destrói o edge**.

4 séries cross-period confirmam mesma direção: edge calibrado em qualquer recorte único não sobrevive 9/9 (CA,CB,CC,CD) em outros recortes com hiperparâmetros fixos.

Implicação forte: **o vocabulário atual (3 estratégias LTF long-only + 4 filtros) não captura a dimensão temporal necessária pra ter edge estável**. Duas hipóteses alternativas:

- **H1: edge estável não existe neste universo** (BTC/ETH/SOL 1h, period 180d, long-only, sem macro). Se verdade, AF deve virar pesquisa sobre **como escolher regime** (classifier) e **quando não operar**, não sobre estratégias individuais.
- **H2: edge estável existe mas exige ferramental ausente** (short side, multi-TF native strategies, regime classifier dinâmico, cross-asset, regime-aware sizing). Se verdade, AF precisa expandir vocabulário antes de mais séries.

Não decidimos H1 vs H2 aqui — isso é conteúdo da ADR-0050 (revisão de vocabulário).

## Padrão 5 — Pré-registro funcionou bit a bit

Todas as 4 séries: gate declarado pré-execução, nenhum gate movido post-hoc, nenhuma variante retunada pra rescue. Em CD, o gate de 3 partes (1-6 + 7 + 8) capturou nuance que um gate binário teria perdido: **filtro é útil direcionalmente mas não suficiente standalone**.

Método está validado. É um ativo transferível — vale documentar em `vision/` ou `system/` como playbook padrão, não como prática ad-hoc das séries C. (Fora do escopo desta ADR; anotado pra futura ADR de documentação de processo.)

## Padrão 6 — "Lift sem fe" tem uso limitado em engine fixed-notional

CC e CD mostraram lift de risco sem lift de retorno. Com `fracao=0.1` fixo, isso é **perda de eficiência de capital**: risco menor num sizing que não re-aloca o capital liberado. O filtro "desperdiça" sua contribuição.

Para aproveitar lift sem ganho de retorno absoluto, seria preciso:

- **Fracao dinâmica** (mais capital quando filtro ativo). Rejeitado em CD (fora de escopo).
- **Risk budget por trade** em vez de sizing fixo. Seria um ADR separado.
- **Composição com outras estratégias** no mesmo portfolio, só operando quando filtro ativo. Fora do escopo AF atual.

Anotação: AF hoje entrega **um sinal binário por estratégia**, não um portfolio. Até que haja camada de portfolio, o "lift de risco sem lift de retorno" é **dado inútil pro bot**, mesmo sendo estruturalmente correto. Outro item pra revisão de vocabulário (ADR-0050).

## Padrão 7 — Filtros herdam o problema da estratégia

`trend_htf:4h:50:long_only` é **long_only** por design (reflete bias direcional). Num engine long-only (todas estratégias atuais), ele não pode filtrar short — só silenciar long quando bearish. Metade do seu valor teórico (operar short em bear alinhado) é inacessível.

Isso não é bug — é consequência arquitetural. Mas é outra evidência de que **expandir filtros sem expandir short side é aperto sem saída**.

## Síntese unificada

Após 4 séries cross-period e 1 audit:

1. **Edge isolado cross-period não existe** no universo atual (3 estratégias × 3 ativos × múltiplos recortes, long-only, 1h, sem macro). 46 runs convergem pra isso.
2. **Edge composto (estratégia + filtro) também não generaliza cross-period** — exceto pelo caso extremamente específico Bollinger+BollingerWidthFilter em recorte bull-com-chop, e mesmo esse não sobrevive 2025-H1.
3. **`trend_htf` é modulador direcional útil** (lift de risco confirmado), mas só entrega valor em engine com sizing dinâmico ou portfolio — AF não tem isso.
4. **Pré-registro + audit funcionam**. São ativos metodológicos sólidos, não gargalos.
5. **O problema não é de execução, é de vocabulário** (próxima ADR).

## Implicações práticas

**Pro manifest oficial:**
- Permanece como está (ADR-0048 validou).
- Não adicionar novos combos via sweep LTF único-recorte. ADR-0044 estilo pra qualquer promoção.
- Se `expansion_policy` for relaxada no futuro, a regra "N≥2 recortes distintos" deve ser explícita.

**Pro bot paper-trading:**
- Sem mudança de comportamento imediata. Bot continua com manifest v2.
- **Bridge não posta sobre esta meta-análise**: nenhuma decisão muda para o bot (signal-only rule). Meta-análise é documento interno AF.

**Pra pesquisa futura:**
- Nenhuma Série CE/CF/CG antes da revisão de vocabulário (ADR-0050 próxima).
- Candidatos a eixos novos (pra ADR-0050 tratar): short side, multi-TF native strategies, regime classifier, cross-asset, sizing dinâmico, macro context.
- Candidatos a eixos **não** a explorar: mais combinações de filtros existentes (diminishing returns), tuning intra-recorte (histórico de curva-fit), ADR-0025 rank híbrido (artefato já documentado).

**Pra método (documentação de processo):**
- Playbook pré-registro funcionou; merece entrar em `system/` ou `playbooks/` como padrão (ADR futura de documentação).
- Auditoria tipo ADR-0048 funcionou; merece ser padrão antes de meta-análises, não improvisado.

## Consequences

**Positive:**
- Síntese consolidada das 46 runs + 5 audit. Evita que próximas decisões repitam análise já feita nas séries individuais.
- 7 padrões documentados viram input explícito pra ADR-0050. Revisão de vocabulário não começa do zero.
- Dois ativos metodológicos (pré-registro, audit) identificados como padrão promovível.

**Negative:**
- Projeto está oficialmente sem direção de pesquisa produtiva dentro do vocabulário atual. Próxima série útil depende de decisões arquiteturais (ADR-0050), não de mais sweep.
- Reconhecimento explícito: **manifest depende criticamente de 1 combo em 1 recorte específico**. Se mercado degradar estruturalmente, AF não tem fallback dentro do vocabulário atual.

**Neutral:**
- Código permanece intacto: nenhuma remoção, nenhuma adição. `TrendHTFRegimeFilter` continua disponível para uso futuro.
- Usuário aprovou sequência de 4 ADRs (0049, 0050, próxima série) — esta é a primeira. Segue pra ADR-0050.

## Fora do escopo desta ADR

- Qualquer decisão sobre H1 (edge não existe) vs H2 (vocabulário insuficiente). Isso é conteúdo da ADR-0050.
- Qualquer nova série de pesquisa. Depois de ADR-0050.
- Promoção do método pré-registro/audit pra `playbooks/` ou `system/`. ADR separada, baixa prioridade.
- Mudanças no bot paper-trading. Signal-only rule: nenhuma atualização cross-bridge.
