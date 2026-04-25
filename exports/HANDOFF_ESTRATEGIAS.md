# HANDOFF — Estratégias validadas (stack canônico 13 combos)

**Data:** 2026-04-21
**Versão:** 1.0
**Fonte:** `exports/approved/*.json` (6 manifests ativos)
**Runtime contract:** `faithful` (ADR-0030, 5 invariantes)

Este documento consolida **todas as estratégias OOS-validadas** e dá passo-a-passo de implementação. É o single source of truth para implementar o bot. Se o bot diverge daqui, o bot está errado — não a estratégia.

---

## Índice

1. [Invariantes universais (obrigatórias em toda estratégia)](#1-invariantes-universais)
2. [Estratégia 1 — Bollinger SHORT + filter width 300](#2-estratégia-1--bollinger-short--filter-width-300)
3. [Estratégia 2 — Bollinger LONG + filter width 250](#3-estratégia-2--bollinger-long--filter-width-250)
4. [Estratégia 3 — RSI LONG + filter width 300 (ETH only)](#4-estratégia-3--rsi-long--filter-width-300-eth-only)
5. [Estratégia 4 — RSI SHORT puro (sem filter)](#5-estratégia-4--rsi-short-puro-sem-filter)
6. [Estratégia 5 — RSI 25/75 SHORT + filter trend_htf 4h (SOL only)](#6-estratégia-5--rsi-2575-short--filter-trend_htf-4h-sol-only)
7. [Estratégia 6 — RSI SHORT + filter width 300 (BTC only)](#7-estratégia-6--rsi-short--filter-width-300-btc-only)
8. [Checklist de fidelidade do bot](#8-checklist-de-fidelidade-do-bot)

---

## 1. Invariantes universais

**Toda** estratégia no stack obedece o contract `faithful` (ADR-0030). Qualquer desvio aqui invalida a validação OOS.

### 1.1 Invariantes de execução

| # | Invariante | Regra exata |
|---|---|---|
| 1 | `entry_fill` | **market_at_open_next_bar**: sinal em barra `t` executa no open da barra `t+1`. Não existe entrada mid-bar. |
| 2 | `exit_fill` | **market_at_open_next_bar**: saída também no open da barra seguinte. |
| 3 | `sizing` | **fixed_notional_literal**: tamanho fixo em moeda quote (USDT). Default $2000 por trade. |
| 4 | `stop_loss` | **disabled**: nunca usar stop-loss. Exit é 100% pelo sinal do engine. |
| 5 | `signal_arbitration` | **exit_wins_on_tie**: se EXIT e ENTER disparam na mesma barra, EXIT vence. |

### 1.2 Causalidade (ADR-0002)

**CRÍTICO.** Em qualquer bar `t`, o engine deve ler apenas closes até `t-1` inclusive. Isto é, **ignora `window.iloc[-1]`**. O valor open/close do bar `t` só existe para execução, nunca para decisão.

Pseudocódigo universal:
```python
def decide(window):
    closes = window["close"].iloc[:-1]  # ignora bar t
    # computar indicadores sobre closes
    # gerar sinal usando closes.iloc[-1] (= close[t-1]) e closes.iloc[-2] (= close[t-2])
```

### 1.3 Cost model validado

Todos os combos passaram stress com fees elevados:

| Parâmetro | Baseline | Stress |
|---|---|---|
| `taker_fee_bps` | 5.0 | 15.0 (fee+10) |
| `slippage_bps_per_notional` | 2.0 | 2.0 |
| `spread_bps` | 0.0 | 10.0 (spread+10) |
| `cost_stress_ratio_min` | — | ≥ 0.95 (todos combos) |

Binance spot taker atual ≈ 10 bps (0.1%). Está **dentro** do stress envelope — edge sobrevive. Se a Binance subir fees acima de ~15 bps, re-validar.

### 1.4 Sizing explicitamente proibido

Nunca usar em **nenhuma** estratégia do stack:
- `snowball` (size cresce com equity)
- `kelly_like`
- `martingale`

Motivo: ADR-0064. BotBinance tentou snowball em ETH BB long 2025-H1 → PnL de +19% → +0.78%, MDD subiu de 17% para 23%. Mean-reversion + sizing escalado em streaks é estruturalmente destrutivo.

### 1.5 Reverse-on-signal

Em estratégias bidirecionais (`long_only=false`), se o engine emite ENTER_SHORT enquanto a posição está LONG (ou vice-versa), o bot deve:
1. Fechar a posição atual no open do bar seguinte (paga custo)
2. Abrir a posição oposta no mesmo open (paga custo novamente)

ADR-0012: reverse incorre **double cost**. O filter (quando presente) serve de gate anti-whipsaw.

---

## 2. Estratégia 1 — Bollinger SHORT + filter width 300

- **Manifest:** `exports/approved/bollinger_short_width_20260419.json` (v3, active)
- **Live desde:** 2026-04-19
- **Approval ADR:** `decisions/0058-manifest-v3-bollinger-short-width-promotion.md`

### 2.1 Engine

```
family: bollinger
params:
  window: 20
  num_std: 1.5
  long_only: false
regime_filter:
  type: bollinger_width
  window: 30
  num_std: 1.5
  min_width_bps: 300
```

### 2.2 Sinais

Seja `closes = window["close"].iloc[:-1]` (ignora bar t).

**Indicadores:**
- `ma_now = closes.rolling(20).mean().iloc[-1]`
- `sigma_now = closes.rolling(20).std().iloc[-1]` (desvio populacional, `ddof=0` se replicar exatamente — mas a biblioteca usa pandas default; verifique consistência)
- `upper_now = ma_now + 1.5 * sigma_now`
- `lower_now = ma_now - 1.5 * sigma_now`
- `ma_prev`, `sigma_prev`, `upper_prev`, `lower_prev` = mesmos cálculos em `closes.iloc[:-1]` (shift de 1)

**Regime gate (obrigatório):**
```
width_bps = 2 * num_std * sigma_now / ma_now * 10000
gate_passa = width_bps >= 300
```
Se `gate_passa == False`, retorna HOLD. **Sem exceção.** Sinais de entry só são avaliados se o gate passa.

**Entry short** (ADR-0051):
```
c_tm1 = closes.iloc[-1]   # close[t-1]
c_tm2 = closes.iloc[-2]   # close[t-2]
enter_short = c_tm1 > upper_now AND c_tm2 <= upper_prev
```
Cruza estritamente acima da banda superior, vindo de dentro ou da borda.

**Entry long** (ADR-0026):
```
enter_long = c_tm1 < lower_now AND c_tm2 >= lower_prev
```

**Exit (ambas direções):**
```
# long exit: fecha quando cruza a média vindo de baixo
exit_long = c_tm1 >= ma_now AND c_tm2 < ma_prev

# short exit: fecha quando cruza a média vindo de cima
exit_short = c_tm1 <= ma_now AND c_tm2 > ma_prev
```

**Ordem de avaliação (ADR-0011):** EXIT antes de ENTER. Se ambos disparam no mesmo bar → EXIT vence.

### 2.3 Combos aprovados

| Symbol | Window | Regime | Trades OOS | Sharpe | MDD% | PnL% |
|---|---|---|---:|---:|---:|---:|
| SOLUSDT 1h | 2024-H2 (2024-07-05..12-31) | bull_com_chop | 102 | 1.380 | 6.33 | +6.64 |
| BTCUSDT 1h | 2025-H1 (2025-01-05..07-04) | chop | 37 | 1.243 | 2.17 | +2.96 |
| ETHUSDT 1h | 2025-H1 | chop | 85 | 2.395 | 8.33 | +12.16 |
| SOLUSDT 1h | 2025-H1 | chop | 109 | 2.713 | 4.92 | +17.47 |

### 2.4 Escopo (não extrapolar)

Edge é **regime-específico** (3 dos 4 combos em regime chop). **Não rodar** este combo em:
- BTC/ETH/SOL 2024-H2 bull puro (Sharpe ≤ 0.77 ou negativo)
- 2025-H2 (CG.7/8/9 todos FAIL)

### 2.5 Passo-a-passo implementação

1. Conectar ao Binance, subscrever klines 1h para símbolos aprovados (SOL/BTC/ETH USDT).
2. Manter buffer rolling de ≥35 closes por símbolo (precisa de 30 para sigma_30 + 3 folga + 1 bar atual).
3. A cada close de bar 1h completo:
   a. Anexar close ao buffer.
   b. Chamar `decide(buffer)` — respeitando causalidade (item 1.2).
   c. Verificar gate width ≥ 300 bps. Se não, HOLD.
   d. Calcular sinal (ENTER/EXIT/HOLD).
4. No **open** do próximo bar 1h:
   a. Se EXIT, enviar market order fechando posição.
   b. Se ENTER com gate OK, enviar market order $2000 quote (ou capital_frac * equity convertido, mas default literal = $2000).
5. Logar cada sinal + fill com timestamp. Comparar periodicamente com o backtest faithful.

---

## 3. Estratégia 2 — Bollinger LONG + filter width 250

- **Manifest:** `exports/approved/bollinger_width_regime_20260418_v2.json` (v2, active)
- **Live desde:** 2026-04-18
- **Approval ADR:** `decisions/0029-eth-2025h1-deploy-approval.md`

### 3.1 Engine

```
family: bollinger
params:
  window: 30              # diferente de Estratégia 1
  num_std: 1.5
  long_only: true         # apenas long
regime_filter:
  type: bollinger_width
  window: 30
  num_std: 1.5
  min_width_bps: 250      # diferente de Estratégia 1 (300)
```

### 3.2 Sinais

Idêntico à Estratégia 1 com **3 diferenças**:
1. `window=30` em vez de 20 para as bandas.
2. `min_width_bps=250` em vez de 300.
3. `long_only=true`: apenas entry_long e exit_long (ignorar sinal short totalmente).

### 3.3 Combos aprovados

| Symbol | Window | Trades OOS | Sharpe | MDD% | PnL% | Rollout priority |
|---|---|---:|---:|---:|---:|---|
| ETHUSDT 1h | 2024-H1 | 38 | 1.834 | 1.82 | +4.68 | wave 1 (fragile_3d) |
| ETHUSDT 1h | 2025-H1 | 36 | 1.210 | 4.37 | +3.71 | wave 1 (fragile_3d_total) |
| BTCUSDT 1h | 2024-H2 | 30 | 1.559 | 1.90 | +2.24 | **wave 2** deferred, $1000 notional |
| SOLUSDT 1h | 2024-H2 | 69 | 2.401 | 3.37 | +8.01 | wave 1 (semi_robust_2d) **melhor combo** |

**BTC 2024-H2 está em wave 2 deferred.** Trigger para ativar: 21 dias corridos sem MANIFEST_EXIT-abaixo-do-entry em ETH+SOL **E** DD combinado < 5%. Sizing ao ativar: $1000 (metade do padrão).

### 3.4 Escopo

**Fragile cross-eixo.** Manifests de robustness (ADR-0038) mostram:
- SOL 2024-H2: único semi_robust_2d (confiar mais).
- Outros 3: fragile_3d (qualquer variação de params pode derrubar).

**Não extrapolar** sem nova ADR:
- BTC 2025-H1/H2 (trades < 30)
- ETH 2024-H2 (Sh=0.72), 2025-H2 (Sh=0.42)
- SOL 2024-H1/2025-H1/2025-H2 (todos Sh < 1.0)

### 3.5 Passo-a-passo implementação

Idêntico à Estratégia 1 §2.5, trocando:
- Buffer mínimo ≥ 45 closes (window=30 + folga).
- Gate em `width_bps >= 250`.
- Apenas lado LONG (ignorar enter_short/exit_short completamente).

---

## 4. Estratégia 3 — RSI LONG + filter width 300 (ETH only)

- **Manifest:** `exports/approved/rsi_long_width_eth_2024h2_20260420.json` (v7, active)
- **Live desde:** 2026-04-20
- **Approval ADR:** `decisions/0092-series-cw-closeout-eth-2024h2-promotes-v7.md`

### 4.1 Engine

```
family: rsi
params:
  period: 14
  oversold: 30
  overbought: 70
  long_only: true
regime_filter:
  type: bollinger_width
  window: 30
  num_std: 1.5
  min_width_bps: 300
```

### 4.2 Sinais

Seja `closes = window["close"].iloc[:-1]`.

**RSI Wilder's (ADR-0027):**
```
deltas = closes.diff()
gains  = deltas.clip(lower=0)
losses = -deltas.clip(upper=0)
# usar Wilder's smoothing (EMA com alpha=1/14):
avg_gain = gains.ewm(alpha=1/14, adjust=False).mean()
avg_loss = losses.ewm(alpha=1/14, adjust=False).mean()
rs = avg_gain / avg_loss
rsi = 100 - 100 / (1 + rs)
rsi_now  = rsi.iloc[-1]
rsi_prev = rsi.iloc[-2]
```

**Regime gate (obrigatório):**
```
# computar bollinger_width com window=30, num_std=1.5
ma    = closes.rolling(30).mean().iloc[-1]
sigma = closes.rolling(30).std().iloc[-1]
width_bps = 2 * 1.5 * sigma / ma * 10000
gate_passa = width_bps >= 300
```
Se gate não passa, HOLD.

**Entry long:**
```
enter_long = rsi_now < 30 AND rsi_prev >= 30   # cruza pra baixo
```

**Exit long:**
```
exit_long = rsi_now >= 50 AND rsi_prev < 50    # volta para zona neutra
```

**Não usar short** (long_only=true).

### 4.3 Combo aprovado (único)

| Symbol | Window | Trades OOS | Sharpe | MDD% | PnL% |
|---|---|---:|---:|---:|---:|
| ETHUSDT 1h | 2024-H2 (2024-07-05..12-31) | 30 | 1.774 | 3.21 | +3.09 |

**Combo mais sensível do stack.** Trade count exato no floor (30). Watch list alta prioridade em paper. Combo é long + regime bull-to-chop, único RSI long aprovado.

### 4.4 Escopo

**Estritamente ETH 2024-H2.** Cross-asset/window todos refutados:
- BTC 2024-H2: trades=17 (abaixo do floor)
- SOL 2024-H2: Sh=-0.29 FAIL
- BTC/ETH/SOL 2025-H1: todos FAIL
- BTC/ETH/SOL 2025-H2: todos FAIL

Cross-window: ETH 2024-H1 Sh=0.574 (contextual PASS regime-matched).

**Não extrapolar.**

### 4.5 Passo-a-passo implementação

1. Subscrever BTC/ETH/SOL ou só ETHUSDT 1h (o combo só é ETH).
2. Buffer ≥ 45 closes.
3. A cada close 1h:
   a. Computar width_bps, RSI(14).
   b. Se width_bps < 300: HOLD.
   c. Se entry_long: armar ENTER_LONG para próximo open.
   d. Se exit_long e posição aberta: armar EXIT.
4. Execução no open do bar seguinte.

---

## 5. Estratégia 4 — RSI SHORT puro (sem filter)

- **Manifest:** `exports/approved/rsi_short_pure_2025h2_20260420b.json` (v8.1, active)
- **Live desde:** 2026-04-20
- **Approval ADR:** `decisions/0106-series-czd-closeout-link-window-specific-rollback-v8.md`

### 5.1 Engine

```
family: rsi
params:
  period: 14
  oversold: 30
  overbought: 70
  long_only: false
regime_filter: null        # SEM FILTER
```

**Importante:** Este é o único combo do stack que é **sem filter**. O manifest determinou empiricamente (ADR-0068 Padrão 12) que em 2025-H2 misto o filter width **reduz edge** em SOL (Sh 2.30 sem → 1.92 com) e é neutro em BTC. Portanto, não aplicar filter.

### 5.2 Sinais

Mesma lógica de RSI da §4.2, **sem o gate de width**.

**Entry long:** `rsi_now < 30 AND rsi_prev >= 30`
**Entry short:** `rsi_now > 70 AND rsi_prev <= 70`
**Exit long:** `rsi_now >= 50 AND rsi_prev < 50`
**Exit short:** `rsi_now <= 50 AND rsi_prev > 50`

**Ordem:** EXIT antes de ENTER.

### 5.3 Combos aprovados

| Symbol | Window | Trades OOS | Sharpe | MDD% | PnL% |
|---|---|---:|---:|---:|---:|
| BTCUSDT 1h | 2025-H2 (2025-07-05..12-31) | 92 | 1.640 | 4.97 | +5.13 |
| SOLUSDT 1h | 2025-H2 | 86 | 2.300 | 5.14 | +13.81 |

**Correlação cross-combo (returns bar-a-bar):** 0.584 (ADR-0110). Diversificação útil mas **no limite** (threshold 0.6). Se rodar ambos simultaneamente, monitorar drawdown conjunto.

Seed stability: 3/3 PASS em seeds {42, 1337, 2024} para ambos combos.

### 5.4 Escopo

**Escopado a regime 2025-H2 misto.** Não extrapolar:
- ETH 2025-H2: Sh=0.81 com filter (sem filter não testado mas fora de escopo).
- BTC/SOL 2025-H1 chop: sem filter FAIL (Sh 0.23 e 0.61). Para 2025-H1 usar Estratégia 5 ou 6.
- LINK 2025-H2: originalmente aprovado (v8), **revertido** em v8.1 porque cross-window falhou (2025-H1 Sh=0.51, 2024-H2 Sh=-1.34). **Não rodar LINK.**
- DOT/AVAX 2025-H2: FAIL naked (Sh 0.50 e -0.05).

### 5.5 Passo-a-passo implementação

1. Subscrever BTCUSDT e SOLUSDT klines 1h.
2. Buffer ≥ 20 closes (RSI warm-up).
3. A cada close 1h, computar RSI(14) e gerar sinal sem gate.
4. Execução no open do bar seguinte.
5. **Se rodar ambos**, monitorar correlação realtime — pausar um dos dois se drawdown conjunto > 8%.

---

## 6. Estratégia 5 — RSI 25/75 SHORT + filter trend_htf 4h (SOL only)

- **Manifest:** `exports/approved/rsi_short_trendhtf_2025h1_sol_20260420.json` (v6.1, active)
- **Live desde:** 2026-04-20
- **Approval ADR:** `decisions/0140-manifest-v61-rsi-trendhtf-sol-2575-promote.md`

### 6.1 Engine

```
family: rsi
params:
  period: 14
  oversold: 25              # <- 25, não 30 (upgrade v6.1)
  overbought: 75            # <- 75, não 70
  long_only: false
regime_filter:
  type: trend_htf
  htf: "4h"                 # higher timeframe
  sma_window: 50
  mode: "short_only"        # filter só habilita entries SHORT
```

### 6.2 Sinais

**RSI com bounds 25/75:**
```
entry_short = rsi_now > 75 AND rsi_prev <= 75
exit_short  = rsi_now <= 50 AND rsi_prev > 50
# long entries também existem mas são todas cortadas pelo filter (mode=short_only)
```

**Regime gate trend_htf 4h:**

Manter buffer paralelo de closes 4h. A cada sinal em 1h:
```
# HTF check: usar closes de barras 4h anteriores (ignora barra 4h atual se incompleta)
closes_4h = buffer_4h["close"].iloc[:-1]  # causal
sma_4h = closes_4h.rolling(50).mean().iloc[-1]
htf_bearish = closes_4h.iloc[-1] < sma_4h
gate_passa = htf_bearish   # mode=short_only: só permite entry se trend 4h bearish
```
Se `gate_passa == False` e sinal é ENTER_SHORT, **descartar** (HOLD). Entries LONG são bloqueadas independentemente (mode=short_only).

Exits NÃO são filtrados pelo gate — se já está short, exit dispara normalmente.

### 6.3 Combo aprovado (único)

| Symbol | Window | Trades OOS | Sharpe | MDD% | PnL% |
|---|---|---:|---:|---:|---:|
| SOLUSDT 1h | 2025-H1 | 32 | 2.00 | 4.75 | +9.80 |

Cross-window reforço:
- SOL 2025-H2: Sh=3.36 (CZ11.6)
- SOL 2024-H1: Sh=1.99 (CZ12.2)
- SOL 2024-H2 bull: Sh=-0.19 (filter contém dano — não destrutivo)

Padrão 40 cross-era confirmado: 3/3 regime-compatível PASS.

### 6.4 Escopo

**Estritamente SOL 2025-H1 chop.** Cross-asset BTC/ETH não testado ainda. Bull 2024-H2 SOL FAIL Sh=-1.02 com filter (Padrão 14: trend_htf contém mas não cria edge).

### 6.5 Passo-a-passo implementação

1. Subscrever **SOLUSDT 1h E 4h** (precisa das duas timeframes).
2. Buffer 1h ≥ 20 closes; buffer 4h ≥ 55 closes (50 para SMA + folga).
3. A cada close 1h:
   a. Computar RSI(14) sobre buffer 1h.
   b. Computar SMA(50) sobre buffer 4h **causal** (ignorando bar 4h em curso).
   c. Verificar `close_4h_last_completed < sma_4h` — se falso, bloquear ENTER_SHORT.
   d. ENTER_LONG **sempre** bloqueado (mode=short_only).
   e. EXIT_SHORT passa livre (sem filter).
4. Execução no open do bar 1h seguinte.

**Atenção sincronização TF:** a cada bar 1h, verificar qual o último bar 4h **fechado**. Ex: no close do bar 1h das 09:00, o último bar 4h fechado é o das 08:00-12:00? Não — é o que fechou às 08:00 (cobriu 04:00-08:00). Apenas barras 4h **inteiramente fechadas** entram no buffer causal.

---

## 7. Estratégia 6 — RSI SHORT + filter width 300 (BTC only)

- **Manifest:** `exports/approved/rsi_short_width_2025h1_20260419.json` (v3, active)
- **Live desde:** 2026-04-19
- **Approval ADR:** `decisions/0068-manifest-v4-audit-closeout-split-v4a-v4b.md`

### 7.1 Engine

```
family: rsi
params:
  period: 14
  oversold: 30              # 30/70 (não 25/75 como Estratégia 5)
  overbought: 70
  long_only: false
regime_filter:
  type: bollinger_width
  window: 30
  num_std: 1.5
  min_width_bps: 300
```

### 7.2 Sinais

RSI 30/70 idêntico à §5.2.
Filter width idêntico à §2.2 (gate width_bps ≥ 300).

Se gate não passa, HOLD em todas direções.

### 7.3 Combo aprovado (único)

| Symbol | Window | Trades OOS | Sharpe | MDD% | PnL% |
|---|---|---:|---:|---:|---:|
| BTCUSDT 1h | 2025-H1 | 37 | 1.688 | 1.67 | +4.07 |

Cross-window: BTC 2024-H1 Sh=1.340 (CZE.3 regime-matched, ADR-0109). **Strict cross-window.**

### 7.4 Escopo

**Estritamente BTC 2025-H1 chop.** SOL 2025-H1 migrou para Estratégia 5 (RSI 25/75 + trend_htf). Não rodar:
- BTC/ETH 2025-H2 (manifest v4b rsi puro cobre)
- ETH 2025-H1 FAIL Sh=0.50
- 2024-H2 bull puro todos FAIL

### 7.5 Passo-a-passo implementação

1. Subscrever BTCUSDT 1h.
2. Buffer ≥ 45 closes.
3. A cada close 1h:
   a. Computar RSI(14) e width_bps.
   b. Se `width_bps < 300` → HOLD.
   c. Caso contrário, gerar sinais short (entry/exit) + long.
4. Execução no open do bar seguinte.

---

## 8. Checklist de fidelidade do bot

Este checklist é a única forma confiável de saber se o bot está implementando o stack corretamente. **Rodar após qualquer mudança no bot.**

### 8.1 Inspeção estática (code review)

- [ ] Decisão usa apenas `closes.iloc[:-1]` (ignora bar em curso).
- [ ] `entry_fill = market @ open[t+1]` para toda estratégia.
- [ ] `exit_fill = market @ open[t+1]` para toda estratégia.
- [ ] `sizing = fixed_notional_literal` (não snowball/kelly).
- [ ] Stop-loss **desabilitado**.
- [ ] `signal_arbitration = exit_wins_on_tie` (EXIT antes de ENTER).
- [ ] RSI usa Wilder's smoothing (EMA alpha=1/14), não SMA.
- [ ] Bollinger sigma: verificar se usa `ddof=0` ou `ddof=1` — validação AF usa pandas default (`ddof=1`). Divergência aqui invalida combos BB.
- [ ] Regime filter `bollinger_width`: fórmula `2*num_std*sigma/ma*10000`.
- [ ] `reverse_on_signal` implementado corretamente (fecha + abre, paga 2 custos).

### 8.2 Cross-check empírico (shadow mode)

Rodar bot em **paper** por 7-14 dias com log detalhado por bar:
- timestamp, symbol, indicador_values, sinal_emitted, fill_executed.

Comparar com backtest faithful no mesmo dataset 1h mais recente. **Divergências aceitáveis:**
- Fills com ≤ 1 bar de delay (depende da ligação ao exchange).
- PnL dentro de ±0.5% do backtest idêntico período.

**Divergências não aceitáveis:**
- Sinais diferentes (≥ 1 discrepância por semana).
- Fills no bar errado.
- PnL > 2% de divergência em 14 dias → bot tem bug estrutural.

### 8.3 Diff esperado live vs backtest

Fatores que causam divergência pequena (≤ 0.5% / 14 dias) e são aceitáveis:
- Fees reais vs fees simulados (se divergem do baseline 5 bps).
- Slippage real > slippage simulado (mas stress envelope cobriu até 10 bps extra).
- Parciais de execução (se o bot não fecha tudo numa ordem só).

Fatores que **invalidam** a comparação:
- Bar em curso sendo usado na decisão.
- Entry/exit no bar errado (mid-bar vs next-open).
- Sizing variável sem ser autorizado.

---

## 9. Apêndice — Índice de runs e rastreabilidade

Cada combo tem `source_run_id` que aponta para `results/validation/<id>/` com:
- `run.json` (metadata + flags completos)
- `walk_forward.json` (folds + trades + equity curves)
- `monte_carlo.json` (1000 resamples)
- `cost_stress.json` (fee+10, spread+10)

Re-rodar qualquer combo (smoke test):
```bash
# exemplo BB short SOL 2025-H1 (combo CG.6)
python -m alpha_forge.cli.app validate \
  --run-id smoke-cg6 \
  --dataset-id solusdt_1h_20250105_20250704_binance_spot \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --sizing-mode fixed_notional \
  --taker-fee-bps 5 --slippage-bps-per-notional 2 --spread-bps 0 \
  --strategy bollinger --no-long-only \
  --bollinger-window 20 --bollinger-num-std 1.5 \
  --regime-filter bollinger_width:window=30:num_std=1.5:min_width_bps=300 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 1000 --mc-seed 42
```

---

## 10. Resumo operacional

**Total: 13 combos em 6 manifests ativos. Todos faithful, todos OOS validated com walk-forward 4-5 folds + MC 1000 + cost_stress.**

| # | Estratégia | Combos | Assets cobertos |
|---|---|---:|---|
| 1 | Bollinger SHORT + width 300 | 4 | SOL 2024-H2, BTC/ETH/SOL 2025-H1 |
| 2 | Bollinger LONG + width 250 | 4 | ETH 2024-H1/2025-H1, BTC/SOL 2024-H2 |
| 3 | RSI LONG + width 300 (ETH only) | 1 | ETH 2024-H2 |
| 4 | RSI SHORT puro (sem filter) | 2 | BTC/SOL 2025-H2 |
| 5 | RSI 25/75 SHORT + trend_htf 4h | 1 | SOL 2025-H1 |
| 6 | RSI SHORT + width 300 (BTC only) | 1 | BTC 2025-H1 |

**Recomendação de rollout inicial:** começar apenas pela **Estratégia 2 (BB long + width 250)** com o combo SOL 2024-H2, que é o único `semi_robust_2d` e o de maior confiança cross-eixo. Adicionar os demais por wave conforme paper-trade acumula ≥ 21 dias corridos limpos.

**Objetivo final:** todos os 13 combos ativos, $2000 notional cada (exceto BTC BB long 2024-H2 = $1000). Notional total stack completo ≈ $25000 quote.
