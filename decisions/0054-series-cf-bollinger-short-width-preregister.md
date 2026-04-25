# 0054 — Série CF: Bollinger short + BollingerWidthFilter cross-period (pré-registro)

**Status:** Accepted — pré-registro; execução inicia imediatamente
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0048 (manifest audit), ADR-0049 (meta-análise), ADR-0051 (short side impl), ADR-0053 (closeout CE).

## Context

ADR-0053 arquivou Série CE (short puro) com FAIL 2/18 no Gate 1, mas observou que **4-5 pilotos 2025-H1 têm Sharpe > 0.5 e fe > 10k**, bloqueados apenas em cost_r e MC p5. Dois especificamente marcantes:

- CE.5 (Bollinger short ETH 2025-H1): Sharpe **2.45**, fe 11496, MDD 7.00, cost_r 0.94 (1pp abaixo do gate), MC p5 9978
- CE.6 (Bollinger short SOL 2025-H1): Sharpe **1.92**, fe 11346, MDD 6.29, cost_r 0.94, MC p5 9675

Magnitudes **comparáveis ao manifest v2** (Sharpe 1.21-2.40 nos 4 combos aprovados). O edge existe; só não passa o stress de custo +10bps/+10bps.

Audit ADR-0048 estabeleceu que `BollingerWidthFilter` é **load-bearing** no manifest long:
- Bollinger 30/1.5 puro: Sharpe 1.62, MC p5 9968 — FAIL gate
- Bollinger 30/1.5 + width≥250: Sharpe 2.50, MC p5 10254, trades −18% — PASS gate

Filtro cortou 12 trades de 67 (regime de baixa width = squeeze = falso sinal mean-rev) e elevou Sharpe +0.89. **Hipótese simétrica testável**: se filtro eleva Bollinger long em bull-com-chop, também deve elevar Bollinger short em chop — e em particular elevar o cost_r dos pilotos CE.5/CE.6 acima de 0.95 (edge puro forte, só precisa de menos turnover).

## Decisão

Executar 9 pilotos composicionais (Bollinger short + BollingerWidthFilter) cross-period. Se passar gate, é o **segundo combo composicional** do projeto — primeira evidência de simetria long/short em mean-rev.

### Matriz de pilotos

| # | Recorte | Dataset-id sufixo | Ativo | Regime rótulo |
|---:|---|---|---|---|
| CF.1 | 2024-H2 | `20240705_20241231` | BTC | bull forte |
| CF.2 | 2024-H2 | `20240705_20241231` | ETH | bull forte |
| CF.3 | 2024-H2 | `20240705_20241231` | SOL | bull forte |
| CF.4 | 2025-H1 | `20250105_20250704` | BTC | chop/correction |
| CF.5 | 2025-H1 | `20250105_20250704` | ETH | chop/correction |
| CF.6 | 2025-H1 | `20250105_20250704` | SOL | chop/correction |
| CF.7 | 2025-H2 | `20250705_20251231` | BTC | bull moderado |
| CF.8 | 2025-H2 | `20250705_20251231` | ETH | bull moderado |
| CF.9 | 2025-H2 | `20250705_20251231` | SOL | bull moderado |

Estratégia: `bollinger window=20 num_std=1.5 long_only=False`.
Filtro: `bollinger_width:window=30:num_std=1.5:min_width_bps=250` (idêntico ao do manifest long v2, preservando semântica de "regime de volatilidade estrutural").

**Apenas 9 runs** (sem baseline pair) — reusa dados de CE como baseline. `summarize_cf.py` lê CE runs existentes pra computar lift vs sem-filtro.

### Parâmetros de engine (idêntico a CA-CE)

- capital 10000, fracao 0.1, alavancagem 2.0
- taker 5bps, slippage 2bps, spread 0
- n-folds 5, rolling, train_fraction 0.5, min_test_bars 50
- mc_resamples 1000, mc_seed 42
- stress `fee+10:10:0:0`, `spread+10:0:0:10`
- `--no-long-only`

### Gates pré-registrados

**Gate 1 — principal**: ≥ **3/9** pilotos passam critério manifest completo:
- trades ≥ 30
- Sharpe ≥ 1.0
- MDD ≤ 20
- MC p5 > 9500
- cost_stress_ratio ≥ 0.95

Densidade 3/9 ≈ 33%, igual ao manifest v2 (4/15 ≈ 27%) e ao gate CA-CD de 6/9.

**Gate 2 — lift vs CE** (load-bearing filter): em **≥ 6/9** pilotos, filtered deve ter:
- cost_r > cost_r do CE correspondente (filtro reduziu turnover a ponto de melhorar stress)

Se o filtro for load-bearing como foi pro long (ADR-0048 Audit B), precisa mover **pelo menos** cost_r, que foi o corte crítico de CE. Fe/Sharpe são bônus.

**Gate 3 — falsificacionista**: em 2024-H2 (bull forte, 3 pilotos CF.1-3), **≤ 1/3 passa Gate 1**. Espelho do Gate 2 de CE: bull extendido ainda mata short, mesmo com filtro composicional. Se passar ≥2/3, investigar marcação de regime ou bug.

### Pipeline de dados

`tools/run_cf_sweep.py`: 9 runs, `run_id = cf-bol-20-15-<asset>-<suffix>-width30-250-short`.
`tools/summarize_cf.py`: lê 9 CF runs + 9 CE Bollinger runs existentes; aplica Gates 1-3.

### Regras anti-movimento de régua (idênticas a CE)

- Gates fixados. Não renegociáveis post-hoc.
- Se passar 2/9 no Gate 1, FAIL (não "quase").
- Re-rodar apenas se erro técnico (dataset ausente, crash).

### Timebox

- Execução: ~20min (9 runs).
- ADR-0055 closeout no mesmo dia.

## Hipóteses explícitas (pré-registradas)

1. **H-principal**: filtro resolve o problema de cost_r de CE. Pilotos 2025-H1 passam Gate 1 (3/3 ou 2/3 nesse recorte); possivelmente 1-2 de 2025-H2 também. **Esperado: 3-5/9**.
2. **H-falsificação** (Gate 3): filtro **não** resgata short em bull forte. Edge composicional é regime-dependente, não universal. ADR-0048 Audit B mostrou que filtro eleva long em bull 2024-H2; simétrico seria filtro eleva short em chop. Cross-regime (filtro long em chop, filtro short em bull) ambos devem falhar.
3. **H-lift**: filtered cost_r é > CE cost_r em **pelo menos 6/9** pilotos. Razão: filtro exclui barras de baixa width (falso-sinal mean-rev), reduzindo trades ruins → por trade, o edge sobrevive melhor ao stress +10bps.

## Saída da série

- Se Gate 1 + Gate 3 PASS: **elegível pra manifest v3** em ADR separada (não aqui — promoção precisa ADR própria e Série CE+1 não é parte do gate). Resultado positivo duplica universo de manifest composicional.
- Se Gate 1 FAIL: mean-rev short é arquivado como família. Próxima ADR pivota pra §D3/§D5 de ADR-0050.
- Bot BotBinance não notificado durante a série (signal-only rule).

## Alternativas consideradas

### Rodar 18 pilotos (3 recortes × 3 ativos × 2 estratégias — Bollinger E RSI com width)

Rejeitado. `BollingerWidthFilter` é semanticamente feito pra casar com **Bollinger**. Aplicá-lo em RSI é tecnicamente possível (filtros são independentes) mas conceitualmente estranho: width é métrica de volatility structural, RSI já tem sua própria métrica de momentum. Se width+RSI passasse, seria acidente. Manter disciplina: um filtro composicional por vez, alinhado semanticamente.

### Gate 1 em 4/9 (40%)

Rejeitado. Manifest v2 passou com 4/15 (27%). Exigir 4/9 (44%) seria **mais estrito** que o próprio manifest que é referência. 3/9 (33%) é o ponto de simetria.

### Adicionar `min_width_bps=200` e `=300` como pilotos adicionais

Rejeitado. Isso é grid-search. Pilotamos com o valor exato do manifest (250) — se esse não passar, a família morre. Se passar, grid fica pra ADR de promoção (tunar depois que se confirma o conceito).

### Rodar baselines novos (CE runs já existem)

Rejeitado. CE runs com mesmos parâmetros de engine estão em `results/validation/ce-bol-20-15-*`. Reusar economiza 9 runs de compute e garante comparação apples-to-apples (mesmo seed MC, mesmo WF scheme).

## Consequences

**Positive:**
- Testa hipótese falsificável específica (simetria com manifest v2 long).
- Baixo custo: 9 runs + 2 ADRs + tooling reusa padrão CE.
- Se passar, desbloqueia manifest v3 com combo short.

**Negative:**
- Se falhar, meta-análise consolida 3ª rejeição consecutiva pra família mean-rev em geral (CE short puro + CF short+width + audit long puro).
- Próxima ADR teria que pivotar pra §D3/§D5, que são mais caras.

**Neutral:**
- Manifest v2 permanece intacto durante série.
- Bot não muda comportamento.

## Critério de sucesso

1. 9 runs completam sem crash.
2. `summarize_cf.py` avalia Gates 1-3.
3. ADR-0055 escrita no mesmo dia decidindo promoção ou arquivamento.
