# 0051 — Short side ativo para Bollinger e RSI

**Status:** Accepted — design + implementação neste mesmo ciclo
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0012 (engine reverse-on-signal), ADR-0013 (Donchian simétrico — template), ADR-0026 (Bollinger long-only), ADR-0027 (RSI long-only), ADR-0050 §Decisão 2.

## Context

ADR-0050 decidiu que **short side** é a próxima expansão arquitetural. Engine já suporta `Signal.ENTER_SHORT` via ADR-0013 (Donchian simétrico) + ADR-0012 (reverse-on-signal com custo duplo). `ma_crossover` também é simétrico via ADR-0012. **Bollinger (ADR-0026) e RSI (ADR-0027) bloqueiam** com `NotImplementedError` quando `long_only=False`.

Esta ADR remove esses bloqueios de forma conservadora e simétrica.

## Decisão

Implementar `long_only=False` em `BollingerMeanReversionStrategy` e `RSIMeanReversionStrategy` seguindo a mesma pattern de ADR-0013: no modo simétrico, não há `EXIT` explícito — o fechamento ocorre via reversão, coordenada pelo engine.

### Bollinger short side — regra exata

Seja `closes = window["close"].iloc[:-1]`:

- `mu_now`, `sigma_now` sobre `closes.iloc[-window:]`
- `mu_prev`, `sigma_prev` sobre `closes.iloc[-window-1:-1]`
- `upper_now = mu_now + num_std * sigma_now`; `upper_prev = mu_prev + num_std * sigma_prev`
- `lower_now = mu_now - num_std * sigma_now`; `lower_prev = mu_prev - num_std * sigma_prev`

Sinais edge-triggered (cruzamento estrito):

- **Entrada long** (inalterada): `c_tm1 < lower_now AND c_tm2 >= lower_prev`
- **Entrada short**: `c_tm1 > upper_now AND c_tm2 <= upper_prev` (cruzou pra cima da banda superior)
- Warm-up: `HOLD` enquanto `len(window) < window_size + 3`

Mapeamento (`long_only=False`):

- `long_entry` apenas → `ENTER_LONG`
- `short_entry` apenas → `ENTER_SHORT`
- Ambos simultâneos → **arbitragem conservadora**: `HOLD` (sinal ambíguo, evita custo duplo sem direção clara; difere do Donchian que privilegia bearish, porque Bollinger é mean-rev e sinais conflitantes de mean-rev são ruído, não informação).

Sem `EXIT` no modo simétrico (ADR-0012 reverse-on-signal fecha a posição na próxima entrada oposta).

**Arbitragem `HOLD` em sinal duplo — justificativa específica**: em mean-reversion, "cruzou pra dentro de lower AND cruzou pra fora de upper" na mesma barra implica oscilação intra-barra com fechamento em posição indeterminada. Em trend-following (Donchian) o empate significa "ambos breakouts confirmados" — privilegia o último cronologicamente. Em mean-rev não há cronologia intrínseca no sinal — só o preço final importa, e o preço final é ambíguo nesse caso.

### RSI short side — regra exata

Seja `closes = window["close"].iloc[:-1]`:

- `rsi_now` = RSI sobre `closes.iloc[-period-1:]` (como hoje)
- `rsi_prev` = RSI sobre `closes.iloc[-period-2:-1]`

Sinais edge-triggered (cruzamento estrito):

- **Entrada long** (inalterada): `rsi_now < oversold AND rsi_prev >= oversold`
- **Entrada short**: `rsi_now > overbought AND rsi_prev <= overbought` (cruzou pra cima do threshold de overbought)
- Warm-up: `HOLD` enquanto `len(window) < period + 3`

Mapeamento (`long_only=False`):

- `long_entry` apenas → `ENTER_LONG`
- `short_entry` apenas → `ENTER_SHORT`
- Ambos simultâneos → **impossível por construção** (`rsi_now` não pode ser < oversold e > overbought simultaneamente, já que `oversold < 50 < overbought`). Assert defensivo; se acontecer, bug, raise.

### Sinais de saída — não implementados simetricamente

Em ambas as estratégias em modo `long_only=True`, existe `EXIT` explícito ao cruzar a média móvel/rsi=50. Em modo simétrico, **não adicionamos `EXIT` nem "exit simétrico"** (ex: short sairia ao cruzar abaixo da média). Motivação: ADR-0012 `reverse-on-signal` já fecha a posição quando sinal oposto vem — e "sair pra stop" sem reentrada imediata degeneraria em estratégia de 3 estados (long/flat/short) que este engine não gerencia bem.

**Consequência operacional**: em modo simétrico, a estratégia **sempre está em posição** após o primeiro sinal. Flat entre reversões = ineficiência conhecida, tolerada como preço do modelo simples. Idêntico ao Donchian simétrico hoje.

### Validações

`long_only=False` continua sendo opt-in explícito. Construtor aceita com:
- Remover `NotImplementedError` quando `long_only=False`
- Validar que todos os outros parâmetros continuam válidos
- Tipagem de `long_only` continua estrita (rejeita `int`, `None`, etc.)

`name` do strategy não muda (continua `"bollinger"` / `"rsi"`) — é o mesmo algoritmo, só direcionalidade diferente.

### Testes

1. **Unit tests existentes** — sem mudança em long-only. Adicionar módulo com:
   - Entrada short triggered (sintético: close cruza pra cima da banda superior)
   - Short NÃO triggered em long-entry condition
   - Ambos simultâneos → HOLD (Bollinger)
   - RSI: entrada short triggered quando rsi_now > overbought, prev ≤
   - RSI: arbitragem defensiva não-atingível (assert se chegar)
2. **Causalidade** — mutar `window.iloc[-1]` não muda sinal short (herdado, mas re-testar)
3. **Regressão long-only** — todo teste de long-only existente continua verde.

### CLI

Nenhuma mudança de flags — `--long-only` / `--no-long-only` já existem no CLI (ADR-0013 infraestrutura). Basta remover a mensagem atual que bloqueia Bollinger/RSI.

**Verificar**: hoje o CLI da `validate` aceita `--no-long-only` só pra Donchian/ma_crossover? Se sim, estender pra Bollinger/RSI. Ler `cli/app.py` e ajustar.

### Validation pipeline

Walk-forward + Monte Carlo + Cost Stress — sem mudança. Engine já trata short.

### Manifest

**Nenhum combo short side vai pro manifest nesta ADR**. Manifest atual (v2) é long-only. Qualquer promoção short exige Série CE (ADR-0052 pré-registro) + ADR de promoção.

## Alternativas consideradas

### Short side simétrico total (com EXIT simétrico)

Rejeitado. Exigiria stop/exit na mean-reversion reverso (long: EXIT ao cruzar mu; short: EXIT ao cruzar mu). Adicionaria estado flat entre sinais contrários. Engine atual não tem gerência de 3 estados otimizada; risco de corner cases (reversão + exit no mesmo tick). Adiamento para ADR futura se evidência pedir.

### Short apenas com overbought threshold (RSI) e banda superior (Bollinger), sem exigir cruzamento edge-triggered

Rejeitado. Cruzamento edge-triggered é coerente com versão long (ADR-0026 §§"Regra exata"). Remover a condição `prev <= upper` viraria "state-based" em vez de "event-based", inconsistente com o resto.

### Diferente `num_std` / `threshold` para short

Rejeitado nesta ADR. Adicionaria parâmetros (`num_std_short`, `overbought`) que já existe em RSI. Em Bollinger, o mesmo `num_std` aplicado em ambos os lados é a operação simétrica mínima. Se Série CE mostrar assimetria dominante, ADR futura.

### Fee/slippage diferente em short

Rejeitado. Cost model atual é simétrico (ADR-0006). Se descoberta empírica mostrar diferença relevante, ADR futura — mas isso é dado real, não design.

## Consequences

**Positive:**
- Remove bloqueio arquitetural que impedia `trend_htf:short_only` e filtros simétricos de agregarem valor (ADR-0049 §Padrão 7).
- Dobra universo testável (3 ativos × 3 recortes × 2 direções = 18 slots por estratégia). Pré-requisito necessário pra Série CE (ADR-0052).
- Código mínimo e simétrico ao existente. Baixa superfície de bug.

**Negative:**
- Abre o risco de "short mal calibrado em bull extenso" — cripto tem cauda direita gorda, short em overbought pode sangrar. Sério o suficiente pra ADR-0052 ter gate específico.
- Mais superfície no catálogo — `name="bollinger"` com `long_only=False` é nova entidade lógica ainda que mesmo classe. Manifest/runtime precisam serializar essa distinção (`run.json` já serializa `long_only` via ADR-0017, então OK).

**Neutral:**
- `TrendHTFRegimeFilter` fica simétrico em uso — `mode=short_only` vira caso operacional real, não reservado. Documentação do filtro em `system/api.md` continua correta.
- ADR-0012 reverse-on-signal permanece inalterada. Nenhuma mudança de semântica de custo.

## Fora do escopo desta ADR

- Stops explícitos (SL/TP). Ficam pra ADR separada se Série CE mostrar que short sem stop não funciona.
- Sizing dinâmico por direção (ex: `fracao_short=0.05`). ADR futura se necessário.
- Ma_crossover short — já existe via ADR-0012; sem trabalho adicional.
- Dummy strategy — já suporta short; sem trabalho.
- Registro no manifest — esse é trabalho de Série CE + ADR de promoção, não aqui.

## Critério de sucesso

1. `BollingerMeanReversionStrategy(long_only=False)` não lança; retorna sinal correto em condições sintéticas.
2. `RSIMeanReversionStrategy(long_only=False)` idem.
3. Todos os testes unit existentes (long-only) continuam verdes.
4. Novos testes unit cobrem: entry short trigger, arbitragem, regressão long-only, causalidade.
5. `python -m alpha_forge.cli.app validate --strategy bollinger --no-long-only ...` roda end-to-end sem erro.
6. Suite completa `pytest -q` verde.
