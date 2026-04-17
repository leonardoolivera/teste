# IMPLEMENTATION.md — Donchian breakout

> Produzido pelo `strategy-implementer` a partir de [SPEC.md](./SPEC.md) + [ADR-0011](./decisions/0011-donchian-breakout-strategy.md).
> Suíte pós-entrega: **86 passed, 1 skipped** (20 testes Donchian novos; partia de 66 passed).

---

## Arquivos alterados

| Arquivo | Tipo | Resumo |
|---|---|---|
| [src/alpha_forge/strategies/families/donchian/__init__.py](./src/alpha_forge/strategies/families/donchian/__init__.py) | novo | exporta `DonchianBreakoutStrategy`. |
| [src/alpha_forge/strategies/families/donchian/strategy.py](./src/alpha_forge/strategies/families/donchian/strategy.py) | novo | implementação; `decide(window) -> Signal` puro, stateless, long-only, causal por construção. |
| [src/alpha_forge/cli/app.py](./src/alpha_forge/cli/app.py) | modificado | `--strategy donchian`, `--entry-window`, `--exit-window`; `_build_strategy` ganha ramo Donchian; label de parâmetros estendido. |
| [tests/unit/test_donchian_breakout.py](./tests/unit/test_donchian_breakout.py) | novo | 17 testes: validação, warm-up, entrada, saída, arbitragem EXIT>ENTER, ignora `window.iloc[-1]`, long-only, stateless. |
| [tests/property/test_donchian_causal.py](./tests/property/test_donchian_causal.py) | novo | hypothesis: mutar OHLC de barra futura não altera sinal em `t`. `entry=5, exit=3`, 80 exemplos. |
| [scripts/validate_pilot.py](./scripts/validate_pilot.py) | novo | grid de sensibilidade fees × slippage; gera artefato JSON em `results/validation/`. |
| [scripts/validate_artifacts.py](./scripts/validate_artifacts.py) | novo | checa presença/coerência dos artefatos agentic. |
| [.github/workflows/agentic.yml](./.github/workflows/agentic.yml) | novo | CI não-bloqueante: valida artefatos + smoke backtest + grid de sensibilidade sobre sintético. |

## Mapeamento SPEC → código

| Seção do SPEC | Implementação |
|---|---|
| Hipótese | Não é código; é texto de SPEC + AUDIT. |
| Mercado / Timeframe | Dataset carregado via `load_dataset(dataset_id)`; estratégia é agnóstica a símbolo/timeframe. |
| Entradas — `high[t-1] > max(...)` | [strategy.py:56-62](./src/alpha_forge/strategies/families/donchian/strategy.py#L56-L62): `entry_window_max = highs.iloc[-entry_window-2 : -2].max()`; compara com `high_tm1`. |
| Saídas — `low[t-1] < min(...)` | [strategy.py:56-62](./src/alpha_forge/strategies/families/donchian/strategy.py#L56-L62): `exit_window_min = lows.iloc[-exit_window-2 : -2].min()`; compara com `low_tm1`. |
| Ordem EXIT antes ENTER | [strategy.py:64-68](./src/alpha_forge/strategies/families/donchian/strategy.py#L64-L68): `if low_tm1 < ... : EXIT` avaliado antes. |
| Warm-up | [strategy.py:49-52](./src/alpha_forge/strategies/families/donchian/strategy.py#L49-L52): `if len(window) < max(entry, exit) + 2 : HOLD`. |
| Ignora `window.iloc[-1]` | Slicing `iloc[-N-2 : -2]` + uso de `iloc[-2]` (barra `t-1`); nunca acessa `iloc[-1]`. Testado em `TestIgnoraBarraCorrente`. |
| Validação `__init__` | [strategy.py:26-44](./src/alpha_forge/strategies/families/donchian/strategy.py#L26-L44): `TypeError` para não-int (inclui bool), `ValueError` para ≤ 0. |
| Long-only | Universo emitido: `ENTER_LONG`, `EXIT`, `HOLD`. Testado em `TestLongOnly`. |
| Stateless | Nenhuma instance-var além de `entry_window`/`exit_window` imutáveis. Testado em `TestStateless`. |
| Sizing / fees / slippage / alavancagem | Orquestrados pela CLI via `RiskBudget` + `CostModel` existentes (ADR-0004, ADR-0006). Sem mudança no engine. |

## Decisões técnicas (não ditadas pelo SPEC)

1. **Slice `iloc[-entry_window-2 : -2]`** foi preferido a `iloc[-entry_window-1 : -1]` porque:
   - `high[t-1]` é `iloc[-2]` (engine chama estratégia com `prices[:t+1]`, então `iloc[-1]` é `t` e `iloc[-2]` é `t-1`).
   - A janela de `N` barras **anteriores a `t-1`** é `iloc[-2-N : -2]`.
   - Isso exclui explicitamente a barra `t-1` do próprio cálculo do máximo — consistente com ADR-0011 §"Regra exata": "janela de comparação exclui a barra `t-1`".
2. **`float(...)` nas leituras** para garantir tipo escalar Python (não `numpy.float64`), evitando surpresas em comparações. Mesmo padrão do MA crossover.
3. **Single-pass**: não calculo rolling max/min para toda a janela; faço só para a janela relevante a `t`. Justificativa: `decide()` é chamado por barra pelo engine; rolling global seria trabalho repetido.
4. **Imports absolutos** (`from alpha_forge.backtest.schemas import Signal`) seguindo o padrão do projeto; nunca relativos.

## Gaps (explícitos — não escondidos)

1. **Property-based de monotonicidade de custo para Donchian ainda não foi escrito.** ADR-0010 cobre MA crossover; replicar para Donchian é mecânico e foi marcado como follow-up explícito na ADR-0011 §"Fica explicitamente fora". Não é bloqueador do piloto, mas sim do "piloto é equivalente a MA em rigor de propriedades".
2. **Caracterização multi-asset** (ETHUSDT, SOLUSDT) está no roadmap (STATE.md); não foi feita aqui porque exigiria ingestão de dois datasets a mais. Neutralidade a símbolo foi testada estruturalmente, não empiricamente com Donchian.
3. **Integration test dedicado** ao Donchian não foi adicionado — ADR-0011 explicitamente rejeitou como redundante; o property-based + unit + smoke CLI cobrem o contrato.
4. **`system/domain.md`, `system/api.md`, `system/flows.md` não foram atualizados** nesta entrega porque o overlay agentic introduziu uma decisão nova: manter `system/` espelhando o código (protocolo AGENTS.md) **é** trabalho a ser feito em commit separado, para não misturar "overlay agentic" com "atualização da realidade por implementação". Aponto explicitamente como blocker em CHECKLIST.md.
5. **Short side** — por design não entra; ADR própria quando fizer sentido.

## Como rodar

```bash
# smoke — sintético
python -c "from alpha_forge.cli.app import run; raise SystemExit(run(['run-demo', '--strategy', 'donchian', '--entry-window', '20', '--exit-window', '10']))"

# sobre dataset real (requer ingestão prévia)
python -c "from alpha_forge.cli.app import run; raise SystemExit(run(['run-demo', '--strategy', 'donchian', '--dataset-id', 'btcusdt_1h_20250705_20251231_binance_spot', '--entry-window', '20', '--exit-window', '10']))"

# suíte
python -m pytest -q

# sensibilidade (BACKTEST.md é gerado a partir do output)
python scripts/validate_pilot.py --strategy donchian \
    --dataset-id btcusdt_1h_20250705_20251231_binance_spot \
    --entry-window 20 --exit-window 10

# valida artefatos agentic
python scripts/validate_artifacts.py
```
