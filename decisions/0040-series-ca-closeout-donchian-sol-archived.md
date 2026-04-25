# 0040 — Série CA fechamento: FAIL, Donchian 20/10 SOL 1h arquivado

**Status:** Accepted — série encerrada
**Date:** 2026-04-19
**Deciders:** Usuário + agente.

## Resultado

**PASS count: 2/10.** Gate pré-registrado em ADR-0039 exigia `≥ 6/10`. Série **FAIL**.

| Tag | Period | atrbps | trd | Sh | MDD% | fe | cost_r | MC p5 | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| CA.1 | 2023-H2 | 100 | 53 | **1.91** | 5.12 | 11012 | 0.9757 | 9411 | **PASS** |
| CA.2 | 2024-H1 | 100 | 64 | -1.26 | 7.87 | 9471 | 0.9657 | 8608 | FAIL(Sharpe,fe) |
| CA.3 | 2024-H2 | 100 | 68 | -1.35 | 6.46 | 9574 | 0.9613 | 8762 | FAIL(Sharpe) |
| CA.4 | 2025-H1 | 100 | 70 | -1.96 | 11.88 | 9286 | 0.9639 | 8336 | FAIL(Sharpe,fe,MCp5) |
| CA.5 | 2025-H2 | 100 | 62 | -1.48 | 7.59 | 9608 | 0.9647 | 8923 | FAIL(Sharpe) |
| CA.6 | 2023-H2 | 80 | 59 | **2.14** | 5.09 | 11161 | 0.9713 | 9531 | **PASS** |
| CA.7 | 2024-H1 | 80 | 73 | -0.93 | 7.75 | 9582 | 0.9631 | 8712 | FAIL(Sharpe) |
| CA.8 | 2024-H2 | 80 | 83 | -1.45 | 7.27 | 9483 | 0.9561 | 8598 | FAIL(Sharpe,fe) |
| CA.9 | 2025-H1 | 80 | 83 | -1.86 | 9.33 | 9271 | 0.9579 | 8178 | FAIL(Sharpe,fe,MCp5) |
| CA.10 | 2025-H2 | 80 | 78 | -3.33 | 11.52 | 8987 | 0.9566 | 8123 | FAIL(Sharpe,fe,MCp5) |

## Análise

1. **Os únicos 2 pilotos PASS são o MESMO recorte (2023-H2)** com variação de `min_atr_bps`. Não são confirmações independentes — é 1 observação positiva tendo duas vistas do mesmo mercado.

2. **Todos os 8 recortes 2024-H1 → 2025-H2 têm Sharpe negativo.** Estratégia perde dinheiro sistematicamente em todo período pós-2023. Hit-rate implícito baixo + custos de fricção cumulativos.

3. **O piloto original canary_only (donchian-20-10-sol-1h-2024-regime-atr-100) reaparece como CA.3 (2024-H2, atrbps=100) com Sharpe -1.35 e fe=9574.** Não passa mais os gates novos. O "sucesso" original era marginal mesmo no gate híbrido ADR-0025 e depende do rank relativo, não de mérito absoluto.

4. **Conclusão:** o edge aparente em SOL 2023-H2 era **sorte do regime** (bull pós-bear do ciclo 2022). 2024+ é regime diferente — lateral/volátil com consolidações que queimam breakouts de 20 barras.

## Decisão

- **Donchian 20/10 SOL 1h = campo queimado.** Arquivado — não entregue ao bot, não testado em paper.
- **Nenhum manifest novo.** Manifest v2 Bollinger permanece intocado (bot segue paper-trading o que tem).
- **Bridge:** não posto ao bot. FAIL não muda decisão do lado dele (regra signal-only — ele não precisa agir).

## Disciplina do ciclo

Cumprimos as 3 disciplinas da memória `strategy_research_cycle`:

1. ✅ **Gate pré-registrado** (ADR-0039) — não movi a régua ao ver que 8/10 falharam.
2. ✅ **Timebox** — série fechou em ~15min real, dentro do budget de 1 dia.
3. ✅ **Arquivar sem cerimônia** — sem tentativa de salvar com tuning, janelas alternativas ou regime_filter mais exótico. Donchian 20/10 SOL 1h está encerrado. Se algum dia voltar, terá que ser por ADR **novo** com hipótese **diferente**, não extensão desta.

## Lições pra próxima candidata

1. **1 piloto positivo num dataset único não é sinal — é ruído.** CA estendeu de 1 para 10 e o sinal desapareceu. Começar direto com matriz multi-período evita gastar tempo em candidatas que eram coincidência.
2. **Donchian 20/10 parece fundamentalmente mal calibrado pra 1h em cripto pós-2023.** Janela curta demais pra trend-following num timeframe com muito ruído. Próxima tentativa de trend-following deveria ser janela maior (55/20 clássico Dunnigan) ou timeframe maior (4h).
3. **Sharpe negativo em 8/10 recortes é sinal forte de ausência de edge, não ausência de tuning.** Não vale a pena abrir Série CB tunando entry_window ou exit_window — é desperdício de timebox.

## Próximos passos

Aguardando usuário pra escolher próxima candidata. Opções mapeadas:

1. **RSI mean-reversion** (ADR-0027 existe, 6 pastas em `agentic/active/` com rsi-*, status desconhecido).
2. **MA crossover** (1 pasta em `agentic/active/`, status desconhecido).
3. **Donchian 55/20 ou timeframe 4h** — família não totalmente queimada, mas a Série CA mostrou que dá pra abandonar 20/10 1h completamente.
4. **Família totalmente nova** — ex: Keltner, RSI divergência, TSI, momentum composto.

Não abro nova série sem escolha explícita — pela disciplina de timebox, não entrar em mais de uma candidata em paralelo.
