# VALIDATION.md — Donchian breakout

> Produzido pelo `backtest-validator` após [IMPLEMENTATION.md](./IMPLEMENTATION.md).
> Piloto: `backtest_only`. Nenhuma ordem real foi enviada. LIVE_TRADING = False.

---

## Testes executados

**Comando:** `python -m pytest -q` (repo raiz).

**Output (resumido):**
```
86 passed, 1 skipped, 8 warnings in 19.16s
```

O skip (1) é estrutural do `hypothesis` em `tests/property/test_lookahead_guard.py::test_guard_aceita_sinal_causal` — by design (quando o gerador não produz sinais ativos suficientes, pula). As 8 warnings são `RuntimeWarning: invalid value encountered in divide` do numpy durante `assert_causal` para janelas com série constante — benigno, já documentado em commits anteriores.

**Detalhamento Donchian:**

| Arquivo | Testes | Status |
|---|---|---|
| [tests/unit/test_donchian_breakout.py](./tests/unit/test_donchian_breakout.py) | 17 | **17 passed** |
| [tests/property/test_donchian_causal.py](./tests/property/test_donchian_causal.py) | 1 (hypothesis, 80 exemplos) | **passed** |

**Repetibilidade:** a suíte de property-based foi executada 3× consecutivas; sem flakiness. Tempo médio 3.5s por execução da suíte Donchian isolada.

**Suite Donchian isolada:**
```
python -m pytest tests/unit/test_donchian_breakout.py tests/property/test_donchian_causal.py -q
20 passed in 3.47s
```

## Conformidade ao SPEC

| Seção do SPEC | Evidência |
|---|---|
| **Hipótese (falsificabilidade)** | Não é código; texto de SPEC + teste de falsificação barato documentado. `scripts/validate_pilot.py` é o instrumento de falsificação. |
| **Mercado** | Estratégia é agnóstica a símbolo — testado estruturalmente em `test_paths_multi_asset.py` (herda). Caracterização empírica: BTCUSDT (spot 1h). |
| **Timeframe** | Warm-up respeita `max(entry, exit) + 2` — testado em `TestWarmUp` (2 casos). |
| **Entradas — `>` estrito** | `TestEntradaBreakoutAlta::test_breakout_alta_estrita_gera_enter_long` + `test_empate_exato_nao_e_entrada`. |
| **Saídas — `<` estrito** | `TestSaidaBreakoutBaixa::test_breakout_baixa_estrita_gera_exit` + `test_empate_exato_na_baixa_nao_e_saida`. |
| **Ordem EXIT antes ENTER** | `TestArbitragemReversao::test_exit_vence_enter_long_em_reversao_simultanea`. |
| **Warm-up HOLD** | `TestWarmUp::test_warmup_hold_enquanto_menor_que_max_mais_dois`, `test_warmup_usa_max_dos_dois_windows`. |
| **Validação cedo `__init__`** | `TestValidacaoParametros` — 8 casos: zero/negativo/float/bool para ambos; entry=exit permitido; entry<exit permitido. |
| **Ignora `window.iloc[-1]`** | `TestIgnoraBarraCorrente::test_mutar_ohlc_em_t_nao_muda_sinal` — mutação simultânea de OHLC de `iloc[-1]` (valores extremos: high=999, low=0.001, close=999) não altera sinal. |
| **Long-only** | `TestLongOnly::test_universo_de_saida_apenas_enter_long_exit_hold` — 200 barras sintéticas; sinal ∈ {ENTER_LONG, EXIT, HOLD} em todos os steps. |
| **Stateless** | `TestStateless` — 2 casos: duas instâncias produzem o mesmo sinal; chamadas anteriores não alteram chamada final. |
| **Causalidade (ADR-0002)** | Property-based `test_sinal_em_t_independe_do_futuro_ohlc_completo` com 80 exemplos. Mutação em OHLC completo de barra futura; sinal em `t` inalterado. |
| **Sizing fixed fractional** | Engine existente usa `fixed_fractional_position_sizing` (testado em `test_risk_sizing.py`); Donchian não toca sizing. |
| **Fees / Slippage (aplicação)** | Engine existente aplica `CostModel` (testado em `test_cost_model.py`, `test_backtest_metrics.py`). Donchian herda. |
| **Condições inválidas — gap** | `load_dataset` rejeita; testado em `test_data_loader.py`. |
| **Condições inválidas — sizing** | Engine rejeita com `Rejection`; testado em `test_engine_reject_invalid_sizing.py`. |

**Conformidade: completa.** Todas as cláusulas do SPEC que virariam código têm teste correspondente.

## Falhas conhecidas

### Que passam mas têm fragilidade documentada

- **Property-based `test_donchian_causal` tem `max_examples=80`**, não 200+. Suficiente para sanidade, insuficiente para cobrir completamente o espaço de OHLC. Justificativa: tempo de execução do CI.
- **`TestLongOnly` usa amostra aleatória seeded (random.Random(123))**; não é hypothesis completo. Cobre o caminho feliz; não cobre geração adversarial de OHLC patológico.
- **Warm-up não testa todas as fronteiras `max(entry, exit) + 2`** — testa apenas dois pares `(5,3)` e `(3,10)`. É suficiente para sanidade; hypothesis cobriria mais.

### Que falhariam se tentássemos (e por isso não tentamos ainda)

- **Monotonicidade de custo property-based** (ADR-0010 aplicada a Donchian) **não foi escrita**. Não é falha de execução — é gap explícito do escopo, reconhecido em IMPLEMENTATION.md §Gaps item 1. Será necessário antes de promover.
- **Sensibilidade de parâmetros `(entry, exit)`** não foi varrida. Grid search é responsabilidade de `validation/` (deferred). Hoje, SPEC usa defaults Turtle 20/10 e não prova que são ótimos.
- **Multi-asset** não foi caracterizado empiricamente com Donchian. A estratégia é neutral a símbolo por construção, mas não foi rodada em ETHUSDT/SOLUSDT.

## Resultados de execução (CLI)

### Sintético (sanidade)
```
$ run-demo --strategy donchian --entry-window 20 --exit-window 10
dataset          : synthetic_btcusdt_1h_seed42
strategy         : donchian entry=20 exit=10
barras           : 720
fills            : 28    rejections: 0
equity inicial   : 10000.00    equity final: 9627.50
total_pnl        : -372.50 (-3.73%)
trade_count      : 14     hit_rate: 42.86%    max_drawdown: 4.77%
```

### Dataset real (caracterização)
```
$ run-demo --strategy donchian --dataset-id btcusdt_1h_20250705_20251231_binance_spot --entry-window 20 --exit-window 10
dataset          : btcusdt_1h_20250705_20251231_binance_spot
strategy         : donchian entry=20 exit=10
barras           : 4320
fills            : 220   rejections: 0
equity inicial   : 10000.00    equity final: 9089.79
total_pnl        : -910.21 (-9.10%)
trade_count      : 110    hit_rate: 25.45%    max_drawdown: 10.49%
```

**Leitura honesta:** Donchian 20/10 long-only perdeu dinheiro em ambos os datasets. 110 trades × hit rate de 25% em BTCUSDT sugere que a janela foi mais um recorte de range/oscilação do que de tendência persistente. Isto **não invalida** a hipótese da SPEC — invalida **este recorte**, que é exatamente para o que a hipótese existe.

## Lookahead bias

- **Property-based passa** em 80 exemplos com OHLC completo (não só um campo) — **estrutura da estratégia é causal**.
- **Engine chama `assert_causal` obrigatoriamente** ao final de `run_backtest` — ADR-0002, testado em `test_lookahead_guard.py`.
- **Estratégia ignora `window.iloc[-1]`** por construção: slicing `iloc[-N-2 : -2]` + `iloc[-2]`, nunca `iloc[-1]`. Testado em `TestIgnoraBarraCorrente`.

**Veredito de lookahead:** ausente na implementação testada.
