# 0042 — Série CB fechamento: FAIL, RSI 14/30/70 1h arquivado

**Status:** Accepted — série encerrada
**Date:** 2026-04-19
**Deciders:** Usuário + agente.

## Resultado

**PASS count: 2/9.** Gate pré-registrado em ADR-0041 exigia `≥ 6/9`. Série **FAIL**.

| Tag | Asset | Period | atrbps | trd | Sh | MDD% | fe | cost_r | MC p5 | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| CB.1 | ETH | 2023-H2 | 105 | 6 | 0.82 | 0.45 | 10032 | 0.9976 | 9900 | FAIL(trades,Sharpe) |
| CB.2 | BTC | 2023-H2 | 55 | 24 | 1.92 | 0.87 | 10162 | 0.9890 | 10018 | FAIL(trades) |
| CB.3 | SOL | 2023-H2 | 100 | 39 | **1.85** | 2.07 | **10522** | 0.9817 | 10032 | **PASS** |
| CB.4 | ETH | 2025-H1 | 105 | 36 | -0.76 | 3.94 | 9801 | 0.9812 | 9177 | FAIL(Sharpe,MCp5) |
| CB.5 | BTC | 2025-H1 | 55 | 33 | **1.04** | 2.27 | **10174** | 0.9803 | 9865 | **PASS** |
| CB.6 | SOL | 2025-H1 | 100 | 53 | 0.13 | 8.03 | 10029 | 0.9718 | 9161 | FAIL(Sharpe,MCp5) |
| CB.7 | ETH | 2025-H2 | 105 | 34 | 0.71 | 2.11 | 10151 | 0.9846 | 9583 | FAIL(Sharpe) |
| CB.8 | BTC | 2025-H2 | 55 | 36 | -1.98 | 3.19 | 9685 | 0.9832 | 9364 | FAIL(Sharpe,fe) |
| CB.9 | SOL | 2025-H2 | 100 | 48 | -0.08 | 5.33 | 9967 | 0.9765 | 9189 | FAIL(Sharpe,MCp5) |

## Análise

1. **2 PASS sem padrão claro**: SOL 2023-H2 e BTC 2025-H1. Nem mesmo ativo, nem mesmo período. Ruído, não edge.

2. **Falha do atr threshold em 2023-H2**: CB.1 (ETH, 6 trades) e CB.2 (BTC, 24 trades) falharam por `trades<30` — o `min_atr_bps` calibrado pra 2024 corta sinais demais em 2023-H2 (volatilidade menor/diferente). Isso sozinho invalidaria a hipótese "mesmos hiperparâmetros generalizam temporalmente".

3. **Sharpe fraco sistêmico**: 6/9 pilotos com Sharpe < 1.0, incluindo 3 com Sharpe **negativo** (ETH 2025-H1 = -0.76, BTC 2025-H2 = -1.98, SOL 2025-H2 = -0.08). RSI mean-rev perde dinheiro em metade dos recortes pós-2024.

4. **final_equity ≈ breakeven** (8/9 acima de 9800, 5/9 acima de 10000): isso **não é edge** — é baixa fricção de custos + RSI oscilando perto do par. Sharpe fraco confirma ausência de edge direcional real; é hit-rate moderado sobre oscilações pequenas.

5. **Re-interpretação do "7/8 canary_only" pré-CB**: os AUDIT.md da Série N/AB (2024 única) davam `canary_only` por **rank relativo** sob ADR-0025 híbrido, não por mérito absoluto. Extendido pra 9 recortes com gate absoluto, o sinal desaparece. **O perfil original era artefato de critério, não edge estrutural.**

## Padrão observado (Série CA + CB)

Ambas as séries cross-period seguem o mesmo resultado: **1-2 pilotos PASS em recortes que parecem coincidência, maioria dos recortes com Sharpe fraco ou negativo**. O que está sendo rejeitado consistentemente:

- Donchian 20/10 SOL 1h (ADR-0040)
- RSI 14/30/70 1h ETH/BTC/SOL (este ADR)

Hipótese emergente: **gates strict absolutos cross-period são muito difíceis em 1h cripto pós-2023**. O manifest Bollinger v2 passou por usar combos específicos (2024-H1 ETH, 2025-H1 ETH, 2024-H2 BTC/SOL) que funcionaram individualmente, sem impor gate cross-period. Repetir o filtro cross-period nele provavelmente também falharia em maioria.

## Decisão

- **RSI 14/30/70 1h long-only = arquivado.** Não entregue ao bot, não testado em paper.
- **Nenhum manifest novo.** Manifest v2 Bollinger intocado.
- **Bridge:** não posto ao bot. FAIL não muda decisão dele (regra signal-only).

## Disciplina

1. ✅ Gate pré-registrado ADR-0041 — não movi a régua ao ver 2/9.
2. ✅ Timebox — fechou em ~10min.
3. ✅ Arquivamento sem cerimônia — sem abrir Série CC com `oversold=25`, `period=21`, ou outro regime filter pra tentar salvar.

## Lições

1. **"Canary_only em janela única" = quase nunca sinal real.** Padrão confirmado 2 vezes (CA Donchian SOL 2024, CB RSI 2024). Pilotos de janela única sob ADR-0025 híbrido são fracamente informativos; daqui pra frente, pré-registrar gate cross-period desde o início se possível, em vez de usar AUDIT.md de 1 janela como evidência.

2. **atr_regime threshold é regime-específico.** `min_atr_bps` calibrado pra 2024 corta sinais demais em 2023-H2 (CB.1, CB.2). Pra séries futuras: ou calibrar threshold por período (anula teste "mesmos hiperparâmetros") ou usar threshold que produza trades ≥30 em todos os períodos (pré-check antes de rodar gates).

3. **final_equity alto sem Sharpe alto = não-edge.** Pilotos com `fe ≈ 10000` e `Sharpe < 1.0` são breakeven por baixa atividade + fricção baixa, não por edge. Daqui pra frente, Sharpe é o ponto sensível, não final_equity.

4. **Duas séries cross-period consecutivas falharam** (CA + CB, ambas com ~2/N PASS). Não tratar isso como bad luck — tratar como pattern. Próxima candidata deveria **explicitamente ter razão teórica pra esperar generalização cross-period**, não só "parece promissor numa janela".

## Próximos passos

Aguardando usuário. Opções mapeadas:

1. **MA crossover** (1 pasta em `agentic/active/`). Trend-following simples; mesmo risco de CA.
2. **Donchian 55/20 ou 4h** (família já magoada na CA, mas 20/10 foi o problema — 55/20 é espectralmente diferente).
3. **Timeframe novo**: 4h ou 15m (campos menos explorados). Maior custo de dataset se faltar, mas potencial upside se o 1h for saturado.
4. **Família nova com razão teórica pra cross-period**: ex, **momentum de médio prazo** (MA 50/200 ou breakout 55/20 estilo Turtles) — tem literatura mostrando estabilidade cross-period em commodities/forex.
5. **Parar e re-avaliar estratégia de pesquisa inteira** dado que 2/2 séries pós-realinhamento falharam. Discutir se problema é (a) estratégias testadas, (b) gate calibrado errado, (c) 1h cripto pós-2023 genuinamente sem edge capturável com regras simples.

Minha recomendação honesta: **opção 5 antes de 1-4**. Dois fails consecutivos merecem uma pausa de meta-análise antes de abrir terceiro.
