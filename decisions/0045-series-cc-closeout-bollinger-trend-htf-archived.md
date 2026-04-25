# 0045 — Série CC closeout: Bollinger + trend_htf arquivada (FAIL principal, lift PASS)

**Status:** Accepted — closeout
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Supersedes:** —
**Relates to:** ADR-0043 (arquitetura trend_htf), ADR-0044 (pré-registro CC).

## Resultado

**Gate principal (ADR-0044 §1-6): FAIL 0/9**. Zero pilotos filtrados atingiram `trades≥25, Sharpe≥1.0, MDD≤20%, fe>9800, cost_r≥0.95, MC p5>9200` simultaneamente.

**Gate 7 lift: PASS 7/9**. Em 7 dos 9 recortes, filtered > baseline em `final_equity` ou `max_drawdown`.

Tabela completa:

| Tag | Asset | Período | filt trd | filt Sh | filt fe | base fe | lift fe | lift mdd |
|---|---|---|---:|---:|---:|---:|---|---|
| CC.1 | ETH | 2023-H2 | 5 | 0.82 | 10019 | 10042 | ✗ | ✓ |
| CC.2 | BTC | 2023-H2 | 14 | -1.49 | 9901 | 9989 | ✗ | ✓ |
| CC.3 | SOL | 2023-H2 | 26 | -0.61 | 9833 | 10117 | ✗ | ✗ |
| CC.4 | ETH | 2025-H1 | 18 | -0.75 | 9909 | 10309 | ✗ | ✓ |
| CC.5 | BTC | 2025-H1 | 21 | -1.10 | 9868 | 10142 | ✗ | ✓ |
| CC.6 | SOL | 2025-H1 | 27 | 0.24 | 10034 | 9814 | ✓ | ✓ |
| CC.7 | ETH | 2025-H2 | 7 | -3.50 | 9732 | 10312 | ✗ | ✗ |
| CC.8 | BTC | 2025-H2 | 13 | -1.92 | 9908 | 9866 | ✓ | ✓ |
| CC.9 | SOL | 2025-H2 | 16 | -2.49 | 9743 | 9429 | ✓ | ✓ |

Dados crus: `exports/diag/cc_series_summary.json`. Sweep script: `tools/run_cc_sweep.py`. Summarizer: `tools/summarize_cc.py`.

## Leitura

Duas conclusões **simultaneamente verdadeiras** e importantes:

### 1. Hipótese "filtro HTF reduz risco" — corroborada qualitativamente, insuficiente quantitativamente

O lift 7/9 (e o flip de Sharpe de -0.45 → +0.24 em CC.6) mostra que `trend_htf:4h:sma=50:long_only` altera a distribuição de resultados na direção prevista: **menos drawdown, equity final marginalmente melhor**. Em 2/9 casos inverte Sharpe negativo. Em 5/9 casos adicionais, preserva fe e reduz mdd.

Isto **não é ruído**: lift consistente em 7/9 com mesma direção qualitativa (mdd filtered < mdd baseline em 7/9) é sinal estrutural, não random draw. Bias HTF "faz algo".

### 2. Hipótese "filtro HTF resgata generalização cross-period da estratégia LTF" — rejeitada

O gate principal (ADR-0044 §1-6) existia para testar isso. Falhou em 9/9. Razões dominantes:
- **trade count insuficiente** (8/9 pilotos < 25 trades): filtro corta ~50-75% das barras, resultando em 5-26 trades por piloto (vs 10-66 na baseline). Com poucos trades, Sharpe fica ruidoso (vide CC.7 ETH 2025-H2 com 7 trades → Sharpe -3.50, que é principalmente artefato de amostra pequena).
- **fe não melhora materialmente**: lift de fe ocorre em apenas 3/9 casos, e quando ocorre é marginal (+50 a +300 sobre base 10000). Não compensa perda de amostra.

Em recortes "bons pra Bollinger sozinho" (ETH 2025-H1 fe=10309 Sharpe 1.11, ETH 2025-H2 fe=10312 Sharpe 1.34), o filtro HTF é **custo puro** — corta trades que eram bons. Filtro não sabe distinguir "bearish útil" de "bearish ruidoso".

### 3. Análise da tensão

As duas conclusões não são contraditórias — definem o escopo real do filtro: **`trend_htf` é um gerador de redução de risco, não de geração de edge**. Para um engine com sizing fixo (nosso caso, `fracao=0.1`), redução de risco sem ganho de retorno = perda de eficiência de capital.

Usos em que poderia ser ganho líquido:
- **Sizing dinâmico**: aumentar fracao quando filtro ativo, reduzir quando não — explorar o lift de Sharpe seletivamente. Fora do escopo AF atual.
- **Composição com strategy de trend-following** (não mean-reversion): se a estratégia já ganha com trend, filtro HTF alinhado amplifica. Bollinger é mean-reversion — o alinhamento inverso explica por que ganho é limitado.

## Decisão

1. **Arquivar Série CC.** Bollinger 20/1.5 + trend_htf 4h/50/long_only **não vai pra manifest**. Sem retry com parâmetros diferentes do `trend_htf` nesta ADR (regra pré-registro ADR-0044).

2. **`TrendHTFRegimeFilter` permanece no código** (ADR-0043). O filter não é o problema; a **aplicação no mean-reversion foi escolha ruim**. Mantido como cidadão de 1ª classe.

3. **Não tentar `htf=1d` ou `sma_window=20/100` no mesmo setup.** Regra pré-registro: falha cross-period → arquiva, não retune. Se quiser testar HTF bias de novo, deve ser em **estratégia diferente**.

4. **Bridge AF↔bot**: bot paper-trading Bollinger baseline já em andamento. Informar bot que a experiência HTF-bias no Bollinger fracassou (informação útil, mas muda 0 no comportamento atual do bot — signal-only rule ADR-0018: **não posta**).

## Hipótese forward

O lift observável em 7/9 é dado empírico que sustenta uma hipótese **nova e testável**:

> `trend_htf` combinado com uma estratégia trend-following (não mean-reversion) pode gerar edge aditivo, porque a direção do filtro se alinha com a da estratégia.

Candidatos óbvios: Donchian breakout (ADR-0011) com `trend_htf:long_only`. Donchian puro falhou cross-period (Série CA, ADR-0040), mas pela **razão oposta** ao Bollinger: Donchian perde em chop. `trend_htf` filtraria chop? Testável.

**Decisão**: abrir Série CD próximo ciclo com Donchian + trend_htf, se e quando o usuário aprovar. Não é automático — o padrão "3 séries FAIL seguidas" é sinal pra calibrar a hipótese de pesquisa, não continuar com mesmo template.

## Consequences

**Positive:**
- Pré-registro (ADR-0044) funcionou: gate declarado antes, separou "hipótese útil" (lift PASS) de "hipótese suficiente" (principal FAIL). Sem gate adicional de lift, teria vindo veredicto binário FAIL limpo — mas **perderia o sinal qualitativo** que informa Série CD.
- Dado produto: terceira arquivação pré-registrada, consistente com "agressivo + honesto". Usuário sabe que AF **reconhece edge fraco e arquiva**, não inventa narrativa.
- Implementação `trend_htf` validada em produção real (smoke + 18 runs) — zero bugs observados, resample HTF + composição AND funcionaram bit-a-bit com manifest.

**Negative:**
- 3 séries cross-period consecutivas FAIL (CA, CB, CC). Manifest continua com 1 piloto canônico (Bollinger 20/1.5 + atr_regime 2024-H2).
- Hipótese HTF-bias isolada ainda não-testada em trend-following; decisão de arquivar sem Série CD imediata adia confirmação/rejeição.

**Neutral:**
- `TrendHTFRegimeFilter` disponível na API mesmo sem estratégia canônica que o use. Precedente análogo: `BollingerWidthFilter` (terceira família, sem manifest dedicado atualmente).

## Arquivos de referência

- Pré-registro: `decisions/0044-series-cc-bollinger-trend-htf-cross-period-preregister.md`
- Sweep: `tools/run_cc_sweep.py`
- Summary: `tools/summarize_cc.py`
- Dados: `exports/diag/cc_series_summary.json`
- Runs: `results/validation/cc-boll-20-15-*` (18 diretórios)
