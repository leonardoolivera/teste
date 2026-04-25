# 0043 — Arquitetura: TrendHTFRegimeFilter (higher-timeframe bias)

**Status:** Accepted — arquitetura; implementação segue
**Date:** 2026-04-19
**Deciders:** Usuário + agente.

## Context

Séries CA (Donchian SOL 1h) e CB (RSI 1h) foram arquivadas (ADRs 0040, 0042). Ambas testaram estratégias LTF pure sem contexto de trend maior. Hipótese emergente do usuário: **executar estratégia LTF apenas no lado permitido por um bias HTF** (4h ou daily) pode filtrar contra-tendência que matou Donchian/RSI.

Tem base teórica consistente:
- Dow theory: tendência primária domina secundária
- Turtles (Dennis/Eckhardt): só opera long em bull trend confirmado
- Triple screen (Elder): weekly/daily/intraday alinhados

Arquitetura nova, não estratégia nova. Reaproveita engine AF inteiro via `RegimeFilter` Protocol (ADR-0022) + `CompositeFilter` (ADR-0023).

## Decision

Adicionar `TrendHTFRegimeFilter` em `src/alpha_forge/regimes/filter.py`, seguindo o Protocol de ADR-0022.

### Regra exata

**Entrada**: `window: pd.DataFrame` (OHLCV no timeframe LTF, ex: 1h).

**Parâmetros do filtro**:
- `htf: str` — timeframe alvo do resample (`"4h"`, `"1d"`, `"1w"`). Restrito a esse conjunto inicial; outros valores rejeitados.
- `sma_window: int` — janela da SMA no HTF (ex: 50 candles 4h = ~8 dias).
- `mode: Literal["long_only", "short_only", "both_sides"]` — política:
  - `"long_only"`: filtro ativo se `close_htf[-1] > sma_htf[-1]` (preço acima da média HTF)
  - `"short_only"`: ativo se `close_htf[-1] < sma_htf[-1]`
  - `"both_sides"`: ativo se qualquer um dos dois (sanity — permite validar sem filtro)

**Processamento**:
1. Ignora `window.iloc[-1]` (causal por construção, ADR-0002).
2. Resample `causal = window.iloc[:-1]` para `htf` via `agg={"open":"first", "high":"max", "low":"min", "close":"last", "volume":"sum"}` em `resample(htf, label="right", closed="right")`.
3. Se `len(resampled) < sma_window + 1`: warm-up, retorna `False`.
4. **Crítico — causalidade HTF**: descartar último candle HTF resampled se ele ainda não fechou no contexto de `t`. Implementação: resample produz bucket HTF contendo o último close LTF; se esse bucket não está completo (ex: 1h barra com timestamp 14:00 pertence ao bucket 4h 12:00-16:00 ainda aberto), descartar. Alternativa mais simples e conservadora: **sempre** descartar último candle HTF do resample via `resampled.iloc[:-1]`, garantindo que só candles fechados contribuam. Adotamos esta. Custa 1 candle HTF de atraso (ex: 4h de defasagem em bias daily), aceitável.
5. Calcular `sma_htf = resampled_closed["close"].rolling(sma_window).mean()`.
6. Se `mode == "long_only"`: retornar `close_htf[-1] > sma_htf[-1]`.
7. Se `mode == "short_only"`: retornar `close_htf[-1] < sma_htf[-1]`.
8. Se `mode == "both_sides"`: retornar `True` se qualquer um.

**Nota crítica de uso com LTF long_only**: o filtro em `mode="long_only"` faz sentido com estratégia LTF long-only (ex: RSI 30/70 long-only). O filtro em `mode="short_only"` só faz sentido em estratégia que suporta short — hoje todas são long-only (Bollinger, RSI, Donchian). Portanto `"short_only"` está na API mas sem uso imediato — reservado para quando short side for implementado. Documentar isso no filter.

### Contrato de parâmetros (parte da decisão)

- `htf`: `str`, valores permitidos `{"4h", "1d", "1w"}`. Rejeitar outros com `ValueError`. Pandas suporta mais (`"2h"`, `"12h"`, etc) mas restringimos o conjunto inicial por disciplina (ADR-0027 style).
- `sma_window`: `int` puro (rejeita bool), `> 0`.
- `mode`: `str`, `{"long_only", "short_only", "both_sides"}`. Rejeitar outros.

### CLI

Novo parser argument para `--regime-filter trend_htf:htf=4h:sma_window=50:mode=long_only`. Segue o padrão existente de colon-separated key=value.

`name = "trend_htf"` no filtro — aparece em `run.json` e summaries.

### Composição com filtros existentes

Usuário pode compor via `CompositeFilter` (ADR-0023) — ex: `trend_htf` (bias) AND `atr_regime` (volatilidade mínima). Sintaxe CLI ainda não tem literal pra composição; composição só via código hoje. **Fora de escopo desta ADR**: adicionar sintaxe CLI pra compor filtros. Se Série CC precisar, abrir ADR separado.

### Causalidade — propriedade testada

`tests/property/test_trend_htf_causal.py`: gerar OHLCV sintético de tamanho N, avaliar `is_active(window)`. Mutar `window.iloc[-1]` (close, high, low, volume) — resultado de `is_active` deve ser idêntico. Mutar qualquer barra **depois** de `-1` (inexistente no protocol, mas testar prepending barras futuras hipotéticas não muda resultado). Teste passa sem flakiness em ≥ 100 exemplos Hypothesis.

Adicional: teste específico **alinhamento HTF**. Dataset LTF sintético com padrão conhecido, resample 4h, verificar que bucket da hora 12:00 LTF pertence ao candle 4h 08:00-12:00 (fechado) OR 12:00-16:00 (aberto, descartado) dependendo de `label="right"` convention. Nunca incluir candle HTF aberto no `is_active`.

### Unit tests

`tests/unit/test_trend_htf_filter.py`:
- `TestValidacaoParametros`: `htf` inválido, `sma_window <= 0`, `sma_window` não-int, `mode` inválido.
- `TestWarmUp`: window pequena (< sma_window HTF candles equivalentes) → retorna `False`.
- `TestLongOnlyAtivo`: synthetic trend up; close > sma → `True`.
- `TestLongOnlyInativo`: trend down; close < sma → `False`.
- `TestBothSides`: qualquer condição ativa.
- `TestIgnoreLastBar`: mutar `window.iloc[-1]` não muda `is_active`.
- `TestResampleAlignment`: verificar que resample respeita boundaries (hora 16:00 LTF pertence a 16:00-20:00 HTF 4h, etc).

### Stateless + reprodutível

Sem cache, sem state — `is_active(window)` é função pura. Mesma window → mesmo resultado, sempre.

## Consequences

**Positive:**
- Primeiro filter que lê contexto de tempo maior. Abre eixo arquitetural novo sem mudar Strategy API.
- Reaproveita engine + validation pipeline inteiro — zero mudança em `engine/`, `validation/`, `strategies/`.
- Base teórica sólida (Dow/Turtles/Elder) — não é "feature" especulativa.
- Testável: property-based de causalidade cobre o risco de lookahead do resample HTF.

**Negative:**
- CLI ganha 1 filter novo (4º no total: sma_slope, atr_regime, bollinger_width, trend_htf). Colon-syntax fica mais rica — documentação no `--help` cresce.
- Resample pandas adiciona custo computacional: ~5-10ms extra por barra LTF no pior caso. Aceitável no pipeline atual (segundos por backtest 1h 180d).
- Descartar último candle HTF adiciona 1 candle HTF de defasagem (conservador — pode atrasar entry). Trade-off consciente vs risco de lookahead.

**Neutral:**
- `mode="short_only"` fica reservado até short side implementado. Documentado mas sem teste integrado (só unit).
- `htf` restrito a `{4h, 1d, 1w}` inicialmente; expandir no futuro se necessário (não breaking).

## Alternatives considered

- **SMA 200 no LTF 1h**: rejeitado. 200 barras 1h ≈ 8 dias, mas alinhamento arbitrário (término em qualquer minuto). Não é equivalente a bias HTF — barras HTF têm boundaries fixas (4h fecha 00/04/08/...). Diferença importa pra reprodutibilidade e interpretabilidade.
- **EMA slope**: rejeitado. EMA tem seed; SMA é transparente (mesmo argumento ADR-0027 §Wilder). Abrir ADR separada se quisermos EMA.
- **Slope-based trend** (diferença SMA atual - SMA N atrás): já existe em `SMASlopeFilter`. Trend-HTF é **nível-based** (close vs SMA), não slope. Ambos são válidos mas capturam coisas diferentes — slope captura força da tendência; close vs SMA captura posição. Para bias direcional, close vs SMA é mais simples e direto.
- **Usar um "regime classifier" ML**: rejeitado. Vision §Non-goals proíbe framework AutoML; trend_htf é 4 linhas de lógica, não classificador.

## Fica explicitamente fora desta ADR

1. **Sintaxe CLI pra composição de filtros** (ex: `--regime-filter "trend_htf:...+atr_regime:..."`). Se Série CC precisar, abrir ADR separado.
2. **`TrendHTFSlopeFilter`** (slope HTF em vez de level HTF). Família próxima, mas ADR separada.
3. **Stops dinâmicos baseados em HTF** (ex: stop na SMA HTF). Stops estão fora do núcleo AF.
4. **Short side ativo** — `mode="short_only"` está na API mas sem teste integrado até strategies short-only existirem.

## Critério de sucesso

ADR-0043 concluída quando:

1. `TrendHTFRegimeFilter` existe em `src/alpha_forge/regimes/filter.py`.
2. Unit tests verdes (8 classes acima).
3. Property-based test verde (causalidade + resample alignment).
4. CLI aceita `--regime-filter trend_htf:htf=4h:sma_window=50:mode=long_only`.
5. `run.json` registra filter config (ADR-0017).
6. Pipeline `validate` roda end-to-end com filter novo sobre dataset existente (smoke test, ex: Bollinger 30/1.5 + trend_htf 4h SMA 50 long_only em SOL 2024-H2).
7. `system/api.md` atualizado (lista de filtros).

Explicitamente fora do critério:
- Série CC (usa o filter). Série vai após criterion de sucesso satisfeito.
- Alvo numérico de performance.
