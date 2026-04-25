# 0022 — Regime filter minimal contract

**Status:** Accepted
**Date:** 2026-04-18
**Accepted:** 2026-04-17
**Deciders:** Usuário (owner do projeto) + agente.

## Context

Quatro pilotos agentic (H.1, H.2a, H.2b, H.2c) refutaram por `hit_rate < 45%` em BTC/ETH 1h 180d, variando family (Donchian, MA crossover), asset (BTC, ETH) e modo (long-only, symmetric). Em H.2c os walk-forward folds mostram hit_rate dispersando entre 17.78% e 39.02% na mesma estratégia — sinal de forte regime-dependence. `vision/02-scope.md` §"Module: regimes" já declara o módulo como planejado mas deferred; `backtest` declara "integração opcional com `regimes` quando a estratégia quiser usar"; `strategies` explicitamente **não** depende de `regimes` — a estratégia declara filtros e o backtest injeta o regime classification quando aplicável.

`src/alpha_forge/regimes/` hoje tem apenas `README.md` + `__init__.py` vazio. `vision/02-scope.md` lista 8 regimes futuros (tendência alta/baixa, lateral alta/baixa vol, compressão, expansão, pânico, euforia) como alvo eventual, mas explicitamente classifica heurísticas simples (ATR/ADX/vol realizada) como primeira versão e ML como deferred.

Antes de abrir o módulo é preciso fixar: (1) qual é a **interface mínima** entre `regimes` e `backtest`, (2) como garantir que o filtro **não introduz look-ahead** (ADR-0002), (3) como preservar bit-a-bit o comportamento pré-filtro (retrocompat), e (4) qual é o primeiro consumidor que valida o módulo (piloto H.3 com filtro ativo).

Sem esta ADR, o risco é entrar no módulo e descobrir tarde que a interface escolhida acopla `strategies` com `regimes` (violando §"Dependência unidirecional" de `vision/02-scope.md`), ou que o filtro é testável apenas via integração (sem property-based de causalidade como ADR-0010/ADR-0013 já padronizaram).

## Decision

Abrir `src/alpha_forge/regimes/` com **uma interface funcional mínima** e **uma implementação-protótipo** sem introduzir dependência de `strategies` em `regimes`:

**1. Interface pura (`src/alpha_forge/regimes/filter.py`):**

```python
from typing import Protocol
import pandas as pd

class RegimeFilter(Protocol):
    """Filtro causal de regime. Retorna True quando sinais devem ser aceitos."""
    name: str

    def is_active(self, window: pd.DataFrame) -> bool:
        """Decide sobre barra t baseado em window[:-1] (causal, ADR-0002)."""
```

**Contrato exato (igual ao de `Strategy.decide`):**

- `window.iloc[-1]` (barra `t`) é **ignorada** por construção — filtro lê apenas `window.iloc[:-1]`.
- Stateless: `is_active(window) -> bool` é função pura de `window` e parâmetros do filtro.
- Nome (`name: str`) identifica o filtro no `run.json` (ADR-0017).

**2. Integração via composição no engine (`backtest/engine.py`):**

`run_backtest` ganha **parâmetro opcional** `regime_filter: RegimeFilter | None = None`. Quando não-None, o engine consulta `regime_filter.is_active(window)` **antes** de `strategy.decide(window)`; se `False`, o sinal é coercivamente `HOLD` (ou `EXIT` se há posição aberta — preserva invariante de "posição só abre quando regime permite"). Quando `None`, comportamento é **bit-a-bit idêntico** ao pré-ADR.

**Regra de coerção exata:**

```
if regime_filter is not None and not regime_filter.is_active(window):
    if position is flat:
        signal = HOLD
    else:
        signal = EXIT  # fecha posição ao entrar em regime inválido
```

**3. Primeira implementação — `sma_slope_filter`:**

```python
class SMASlopeFilter:
    name = "sma_slope"

    def __init__(self, window: int, min_slope_bps: float) -> None:
        # valida window > 0, min_slope_bps >= 0, ADR-style
        ...

    def is_active(self, window: pd.DataFrame) -> bool:
        # SMA sobre close[:-1] com lookback window;
        # slope = (sma[-1] - sma[-window]) / sma[-window] * 10000 (bps)
        # active if abs(slope) >= min_slope_bps
        ...
```

Racional: mais simples possível que captura intuição "filtrar em mercados laterais" — SMA slope mede tendência direcional; `min_slope_bps=0` desativa filtro (equivalente a `None`). Heurística alinhada com `regimes/README.md` §"heurísticas auditáveis".

**4. CLI `validate` ganha flag opt-in:**

```
--regime-filter sma_slope:window=50:min_slope_bps=10
```

Parser: `name:param=value:param=value` (similar ao padrão `--stress label:fee:slip:spread` de ADR-0019). Default `None` preserva comportamento bit-a-bit de ADR-0016. `run.json` persiste o filtro como string canonicalizada (ADR-0017 §flags).

**5. Property-based obrigatório (mínimo três):**

- `test_regime_filter_neutrality.py`: filtro que sempre retorna `True` produz backtest bit-a-bit idêntico ao sem filtro (ativa código caminho, mas não muda resultado). Garante retrocompat.
- `test_regime_filter_lookahead.py`: filtro não pode consumir `window.iloc[-1]` (mesmo padrão de `test_lookahead_guard.py` de ADR-0002). Framework reusa `VectorizedLookaheadGuard`.
- `test_sma_slope_filter_monotonicity.py`: aumentar `min_slope_bps` nunca pode aumentar `trade_count` (mais restritivo ⇒ menos entradas). Property dominada similar a ADR-0010.

**6. Persistência — sem bump de `schema_version`:**

`RunMetadata.flags` (ADR-0017) já aceita strings arbitrárias. Campo `regime_filter` passa como string ou ausente. JSONs persistidos pré-ADR-0022 carregam sem modificação. `CostStressReport`, `WalkForwardReport`, `MonteCarloTradesReport` **não** mudam — filtro afeta apenas a produção de sinais, não o schema de relatórios.

**7. `compare` (ADR-0018) é retrocompatível:**

`_diff_run_metadata` já mostra flags divergentes — se `run_a` tem `regime_filter=None` e `run_b` tem `regime_filter=sma_slope:...`, a diferença aparece naturalmente na seção `flags diff`. Nenhuma mudança em `_diff_*` requerida.

## Consequences

- **Positive:** primeira causa-raiz candidata dos 4 pilotos refutados — filtro permite testar diretamente "regime é o fator dominante" via piloto H.3 (Donchian 20/10 BTC 180d **com** `sma_slope_filter`). Interface unidirecional preservada: `strategies` continua ignorando `regimes`. Property-based de neutralidade garante retrocompat bit-a-bit: todos os 4 pilotos anteriores re-executáveis com `regime_filter=None` produzem os mesmos JSONs. ADR-0015/0017 (persistência, metadata) não mudam — filtro é dado via flag CLI, não novo artefato. Opt-in: overhead zero quando não usado. Abre caminho para adicionar mais filtros (`atr_regime`, `adx_regime`) no mesmo contrato sem nova ADR — só nova implementação + nova linha de parser.

- **Negative:** `run_backtest` ganha um parâmetro opcional, expandindo a assinatura pública. Property-based de neutralidade exige um dataset fixture estável (provavelmente o mesmo `btcusdt_1h_20250705_20251231_binance_spot` já usado em pilotos), fixando mais uma dependência entre `tests/` e `data/registry`. Parser de flag `--regime-filter name:k=v:k=v` é o 3º parser de flag estruturada em CLI (junto de `--stress` e `--dataset-id`); se um 4º aparecer, talvez valha extrair um helper genérico. O engine agora tem duas formas de emitir `EXIT` (sinal de estratégia ou coerção por regime-filter); `engine.py` precisa distinguir as duas em logs/rejections para auditoria.

- **Neutral:** Esta ADR **não** implementa os 8 regimes de `vision/02-scope.md` — só abre o módulo com UM filtro simples. Os outros 7 regimes ficam deferred até haver consumidor concreto. `ml-based` classifier permanece em `deferred` como declarado em `regimes/README.md`. Integração com `ranking/` (ADR-0011 §"Depends on") é preservada para o futuro — filtro é um eixo que ranking pode varrer (similar a `cost_stress`).

## Alternatives considered

- **Acoplar `Strategy.decide` com regime** (ex: `Strategy.decide(window, regime: Regime)`) — rejeitado: viola `vision/02-scope.md` §"strategies não depende de regimes". Quebra bit-a-bit todos os 289 testes (`Strategy.decide` pública). Força ADR de breaking change no contrato de estratégia.
- **Implementar 8 regimes agora** (trend-up, trend-down, lateral-low-vol, etc.) — rejeitado: escopo balão. Sem primeiro consumidor validado, risco é construir 8 classificadores e descobrir depois que a interface está errada. ADR mínima primeiro + iterar.
- **ML classifier como primeira implementação** — rejeitado: `regimes/README.md` explicitamente lista ML como deferred. Heurística auditável (SMA slope) valida a interface antes de qualquer modelo.
- **Filter via pipeline em `validation/` em vez de `backtest/`** — rejeitado: filtro precisa ser causal por barra, o que é natural dentro do loop de `run_backtest`. Em `validation/` só poderia filtrar post-hoc, o que não simula comportamento real do trader. Além disso, `vision/02-scope.md` §"backtest" já declara "integração opcional com regimes" no backtest, não em validation.
- **Regime como feature em `RiskBudget`** (ADR-0004) — rejeitado: risk é governança de exposição (sizing, leverage); regime é sobre quando emitir sinal. Mesclar viola separação declarada em §"risk não é mesclado em backtest". Regime filter antes do sinal é conceptualmente anterior ao sizing.
- **Default `regime_filter=None` vs default `NullFilter`** — rejeitado o segundo: forçaria 289 testes a ajustar construção do engine ou importar `NullFilter`. `None` preserva bit-a-bit a assinatura atual com comportamento idêntico.

## Follow-ups

Cada item é pending work em STATE.md:

- Implementar `src/alpha_forge/regimes/filter.py` com `RegimeFilter` Protocol + `SMASlopeFilter` concreto.
- Integrar `regime_filter: RegimeFilter | None = None` em `run_backtest` (engine.py) com coerção HOLD/EXIT.
- Adicionar flag `--regime-filter name:k=v:k=v` em `cli/app.py` (subcomando `validate`; opcionalmente `run-demo`).
- Escrever 3 property-based: neutrality, lookahead, monotonicity. Todos devem passar junto com os 289 existentes (total esperado: 292).
- Abrir piloto **H.3 (`donchian-20-10-btc-180d-regime-sma`)** — mesmo SPEC de H.1 mas com `--regime-filter sma_slope:window=50:min_slope_bps=10`. Testa diretamente a hipótese "regime é a causa raiz". Critério de refutação idêntico (hit_rate ≥ 45%); resultado esperado: `hit_rate` significativamente maior que H.1's 25.45%.
- Atualizar `system/api.md` com o contrato `RegimeFilter`.
- Atualizar `system/flows.md` com novo fluxo "regime filter coerce signal".
- ADRs futuras a considerar após H.3 rodar: ADR-0023 para segundo filtro (ATR-based? ADX-based?) se H.3 validar a direção.
