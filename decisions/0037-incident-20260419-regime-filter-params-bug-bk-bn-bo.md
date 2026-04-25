# 0037 — Incidente 2026-04-19: regime filter params errados em BK/BN/BO (24 pilotos invalidados) + paper-mock detectou via cross-check

**Status:** Accepted (registro de incidente + auditoria)
**Date:** 2026-04-19
**Deciders:** Agente AF (auto-detecção via paper-mock cross-check). Espelha como auditoria pública para o usuário e @botbinance.
**Scope:** Validação offline. **Manifest v2 aprovado NÃO afetado** (bot executa params corretos). Afetadas: ADRs 0032, 0033, 0035 (sweeps de sensibilidade) + classificação 3D consolidada.

## Context

O paper-mock cross-check (ADR-0036) detectou divergência real no primeiro confronto AF↔bot com eventos JSONL: bot emitiu `SIGNAL_CREATED` para ETHUSDT em `2026-04-19T08:00:32Z` que o engine AF canonical (com params usados pelos sweeps BK/BN/BO) **não emitiu**.

**Investigação imediata:**

Para ETH 2026-04-19 08:00 UTC:
- Engine entry condition (`window=30, num_std=1.5`): `close[t-1]=2314.27 < lower=2321.31` ✅ (condição de ENTER satisfeita).
- Regime gate, **params usados em BK/BN/BO + paper-mock loader (ERRADO)**: `bollinger_width(window=20, num_std=2.0)` → `bw_bps=216.65 < 250` → regime INATIVO → AF não emite.
- Regime gate, **params do manifest v2 aprovado (CORRETO)**: `bollinger_width(window=30, num_std=1.5)` → `bw_bps=339.02 >= 250` → regime ATIVO → bot emite ✅.

O bot está correto. Os scripts AF estavam errados.

## Root cause

Os 3 scripts de sweep e o loader paper-mock hardcoded usaram os defaults de `BollingerWidthFilter` da Série AK/AZ original (window=20, num_std=2 — params canônicos da família Bollinger no AF), em vez dos params específicos que o manifest aprovado v2 declara em `engine.params.regime_filter`:

```json
"regime_filter": {
  "type": "bollinger_width",
  "window": 30,
  "num_std": 1.5,
  "min_width_bps": 250
}
```

ADR-0028/0029 explicitamente especificam `bollinger_width:window=30:num_std=1.5:min_width_bps=250`. O bot (BotBinance) leu o manifest e usou os params corretos. Eu, ao construir os sweeps, copiei o pattern do CLI das séries AK/AZ originais sem re-ler o manifest aprovado.

**Arquivos afetados:**
- `tools/run_bk_sweep.py:51` — `--regime-filter bollinger_width:min_width_bps=250:num_std=2:window=20`
- `tools/run_bn_sweep.py:45` — idem
- `tools/run_bo_sweep.py:44` — `--regime-filter bollinger_width:min_width_bps={bw}:num_std=2:window=20`
- `tools/paper_mock_cross_check.py` — `REGIME_PARAMS = dict(window=20, num_std=2.0, min_width_bps=250.0)` (já corrigido para 30/1.5)

## Impacto

### 1. Manifest v2 aprovado: NÃO afetado.

O manifest é fonte de verdade. Bot executa o que está lá. Live continua válido.

### 2. ADRs 0032, 0033, 0035 (Séries BK, BN, BO): metodologicamente inválidos.

24 pilotos sweepados validaram **um manifest hipotético (engine 30/1.5 + regime 20/2)** que não existe em produção. Os números (PASS/FAIL counts, classificações fragile/robust por eixo) **não podem** ser usados pra inferir robustez do manifest aprovado.

**Implicação prática:**
- A classificação 3D (fragile_3d, semi_robust_window, etc.) não vale.
- O `weakest_wins` rule (ADR-0034) está construído sobre classes erradas.
- O `rollout_priority_live` no manifest v2 (campo `class`) reflete classificação errada — mas é puramente informacional para o bot, não muda execução.
- A sugestão "elevar 2ª onda BTC 14d → 21d" foi feita baseada em "BTC frágil 3/3 eixos" → conclusão pode ou não sobreviver à re-execução. Por enquanto **mantém** (argumento de conservadorismo independe do número exato).

### 3. Paper-mock cross-check: foi a ferramenta que pegou o bug.

Validação cruzada: exatamente o caso de uso que o ADR-0036 declarou ("detecta divergências silenciosas para cenários não cobertos por unit tests"). Aqui o cenário não-coberto era um bug **do meu lado**, não do bot. Auto-validação do conceito de paper-mock.

**Cross-check pós-fix:**
| Symbol | AF regime-active signals | Bot signals | Divergências |
|---|---:|---:|---:|
| SOLUSDT | 2 | 2 | 0 |
| ETHUSDT | 1 | 1 | 0 |

Ambos CLEAN. Engine canonical AF e runtime bot agora concordam 100% nos signals históricos pós-ativação.

## Decisões

### 1. Corrigir scripts (imediato)

- `tools/paper_mock_cross_check.py`: `REGIME_PARAMS` → `dict(window=30, num_std=1.5, min_width_bps=250.0)`. **Feito.**
- `tools/run_bk_sweep.py:51`, `run_bn_sweep.py:45`, `run_bo_sweep.py:44`: trocar `num_std=2:window=20` → `num_std=1.5:window=30`. **Pendente.**

### 2. Re-rodar BK/BN/BO com params corretos

24 pilotos. Mesmo grid, mesmos gates, mesmos seeds (42). Output em `results/validation/{bk,bn,bo}-rerun-*`. Tempo estimado: ~30-45min de wall time se sequencial.

### 3. Suspender uso das classificações 3D antigas

Até a re-execução, o manifest v2 mantém os campos `robustness.*_sensitivity` e `cross_axis_3d`, mas com **flag de invalidez** anotada. Não usar pra decisão de wave/sizing.

### 4. ADR-0034 (weakest-wins) continua válido como REGRA

A regra `live class = min over (offline classes for that symbol+engine)` independe dos números — é uma regra de agregação. Os **inputs** mudam após re-execução, mas o output (mesma estrutura) será re-derivável.

### 5. Reportar publicamente ao @botbinance

Mea culpa explícita. O bot fez tudo certo. Eu publiquei 3 ADRs (0032/0033/0035) com números errados. O bot **não acionou** essas ADRs em decisão de execução (manifest é fonte de verdade), então não há dano realizado — mas há ruído epistêmico que precisa ser limpo.

### 6. Critério de paper-mock NÃO é alterado

Os critérios (a)/(b)/(c) do ADR-0036 continuam:
- (a) ≥10 trades clean → encerra.
- (b) Divergência **real** (fill, exit, sizing, decisão genuína) → para tudo.
- (c) 7d sem amostra suficiente → encerra.

Este incidente não é "divergência real do runtime" — é "bug do AF auto-detectado". Conta como auditoria interna, não como gatilho do critério (b).

## Consequences

**Prós:**
- Bug epistêmico detectado **antes** de qualquer decisão de live ser tomada com base nele. Mecanismo paper-mock provou seu valor no primeiro uso real.
- Mea culpa pública via ADR mantém integridade do registro.
- O bot ganha confiança adicional: AF é auto-corretivo + transparente.

**Contras:**
- Re-execução de 24 pilotos é trabalho. ~45min de compute + tempo de re-escrever ADRs 0032/0033/0035 ou emitir errata.
- Potencialmente as classes mudam → algumas conclusões editoriais ("BTC frágil em 3 eixos", "ETH 2025-H1 robust em num_std", etc.) podem mudar. Boa notícia: a re-execução é determinística, não há especulação.
- Demonstrou que copiei pattern de CLI sem checar manifest. Adiciona um item ao protocolo: **toda invocação de sweep que toca params do manifest tem que ler o manifest antes de hardcodear**.

**Riscos residuais:**
- Se a re-execução der classes muito diferentes das antigas, a narrativa "manifest v2 é frágil em todos os eixos" pode mudar significativamente. Pode ficar **mais ou menos** robusto. Não dá pra prever sem rodar.
- Pode haver outros bugs de copy-paste latentes em scripts AF que não foram detectados ainda. Sugere passar os scripts de sweep por uma checagem cross-vs-manifest no protocolo de gate.

## Follow-ups

- [x] Paper-mock loader corrigido (`REGIME_PARAMS` → 30/1.5).
- [ ] Re-rodar BK/BN/BO com params corretos. Output: `exports/diag/bk_rerun_summary.json`, `bn_rerun_summary.json`, `bo_rerun_summary.json`.
- [ ] Re-emitir ADRs 0032/0033/0035 OU adicionar errata em cada apontando para este ADR-0037.
- [ ] Atualizar `exports/approved/bollinger_width_regime_20260418_v2.json` com flag `robustness.invalidated_by="ADR-0037"` até re-derivação.
- [ ] Reportar @botbinance via bridge com root cause + plano de correção.
- [ ] Adicionar checagem ao protocolo: "antes de qualquer sweep que toca regime_filter, ler `engine.params.regime_filter` do manifest correspondente — não copiar pattern de séries anteriores".
- [ ] Considerar se cross-check deveria ler params direto do manifest JSON em vez de hardcoded constants. Reduz superfície de erro.

## Artefatos

- Bridge log: `c:/Users/leo-a/agents_bridge/conversa.md` — entrada 2026-04-19 ~10:50 UTC (eventos JSONL chegaram + cross-check disparado).
- Eventos bot: `c:/Users/leo-a/agents_bridge/paper_mock_feed/{ETHUSDT,SOLUSDT}_events.jsonl`.
- Manifest aprovado: `exports/approved/bollinger_width_regime_20260418_v2.json` — `engine.params.regime_filter = {window: 30, num_std: 1.5, min_width_bps: 250}`.
- Scripts afetados: `tools/run_bk_sweep.py`, `run_bn_sweep.py`, `run_bo_sweep.py`, `paper_mock_cross_check.py`.
- ADRs invalidados: 0032, 0033, 0035 (números, não a regra weakest-wins do 0034).
