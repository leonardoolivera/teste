# 0018 — CLI de comparação de corridas: subcomando `compare`

**Status:** Accepted
**Date:** 2026-04-17
**Deciders:** Usuário (owner do projeto, em modo autônomo sequencial) + agente.

## Context

A ADR-0016 (`alpha-forge validate`) abriu o caminho operacional do pipeline de validação, e a ADR-0017 (`run.json`) fechou o rastro de auditoria por corrida. Hoje, `results/validation/<run_id>/` contém até quatro JSONs versionados (`run.json`, `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`), todos carregáveis via `load_*` da ADR-0015 + ADR-0017.

O próximo passo natural do backlog (Opção A do Next step pós-E.7, "ADR de comparação de corridas — hoje duplamente motivada por E.6 + E.7") é permitir que o operador compare **duas** corridas com um comando. Sem esse subcomando, diffar corridas hoje exige:

- Abrir dois diretórios `results/validation/<run_id>/` no editor.
- Chamar `load_run_metadata`/`load_walk_forward_folds`/etc. em notebook para cada diretório.
- Computar deltas à mão.

A comparação é valor operacional puro: não produz dados novos, só lê artefatos existentes e imprime um diff humano. É precursor natural de `ranking/` (segurado): ranking multiobjetivo **é** comparação generalizada sobre N corridas com composite scoring; `compare` é o caso degenerado com N=2 sem scoring.

Esta ADR fixa a menor fatia honesta do subcomando: dois `run_id` posicionais, leitura via `load_*`, diff textual por seções no stdout, flags de skip simétricas às da `validate`. Saída machine-readable, ranking automático, multi-corrida e stats formais de significância (bootstrap de diferença, testes de hipótese) ficam explicitamente fora.

## Decision

Adicionar um terceiro subcomando à CLI: `alpha-forge compare <run_id_a> <run_id_b>` em `cli/app.py`.

### Contrato do subcomando

```
alpha-forge compare RUN_ID_A RUN_ID_B [--skip-run-metadata]
                                       [--skip-walk-forward]
                                       [--skip-monte-carlo]
                                       [--skip-cost-stress]
                                       [--log-level ...]
```

- `RUN_ID_A` e `RUN_ID_B` são **posicionais obrigatórios** — strings opacas, mesmo contrato opaco da ADR-0016.
- Cada `run_id` é resolvido por `validation_run_dir(run_id)` (ADR-0015).
- Para cada seção (`run_metadata`, `walk_forward`, `monte_carlo`, `cost_stress`), se os dois diretórios **contiverem** o artefato, carrega via `load_*` e imprime diff. Se **só um** contiver, imprime nota "presente em A, ausente em B" (ou vice-versa). Se **nenhum** contiver, pula a seção sem ruído.
- Flags `--skip-*` pulam a seção explicitamente mesmo quando ambos artefatos existem — simetria com `validate` + permite auditoria incremental (ex: só os metadados).
- Stdout é **humano**, formato declarado abaixo. JSON machine-readable é ADR futura.

### Funções puras de diff (privadas, em `cli/app.py`)

Quatro funções puras, uma por artefato, com assinatura `(a: T, b: T) -> list[str]` (lista de linhas de texto já formatadas):

```python
def _diff_run_metadata(a: RunMetadata, b: RunMetadata) -> list[str]: ...
def _diff_walk_forward(a: list[WalkForwardFold], b: list[WalkForwardFold]) -> list[str]: ...
def _diff_monte_carlo(a: MonteCarloSummary, b: MonteCarloSummary) -> list[str]: ...
def _diff_cost_stress(a: CostStressReport, b: CostStressReport) -> list[str]: ...
```

Privadas (sublinhado), **testáveis unitariamente** como funções puras. O subcomando é só orquestração: carregar → diffar → imprimir.

### Formato do output (humano, stdout)

```
run_a            : <run_id_a> (<directory_a>)
run_b            : <run_id_b> (<directory_b>)

--- run_metadata ---
alpha_forge_version : a=0.0.0  b=0.0.0  (igual)
timestamp_utc       : a=2026-04-17T10:00:00+00:00  b=2026-04-17T11:30:00+00:00  (Δ=1h30m)
command             : a=validate  b=validate  (igual)
flags diff:
  n_folds           : a=5  b=10
  mc_seed           : a=42  b=123
  (restantes iguais: 12 flags)

--- walk_forward ---
n_folds          : a=5  b=10  (Δ=+5)
total_trades     : a=12  b=27  (Δ=+15)
total_test_bars  : a=360  b=720  (Δ=+360)
sum_final_equity : a=10234.50  b=10567.89  (Δ=+333.39)

--- monte_carlo ---
n_resamples      : a=1000  b=500
seed             : a=42  b=123
median_final     : a=10100.00  b=10234.50  (Δ=+134.50)
p5_final         : a=9800.00  b=9650.00  (Δ=-150.00)
p95_final        : a=10500.00  b=10800.00  (Δ=+300.00)
original_final   : a=10234.50  b=10567.89  (Δ=+333.39)

--- cost_stress ---
dataset_id       : a=synthetic_...  b=synthetic_...  (igual)
baseline_final   : a=10234.50  b=10567.89  (Δ=+333.39)
scenarios:
  fee+10         : a=10100.00  b=10400.00  (Δ=+300.00)
  slip+10        : presente em A, ausente em B
  big_stress     : ausente em A, presente em B
```

Cada seção é independente: pular uma (via `--skip-*` ou artefato ausente) imprime linha única `<section>: pulado (<motivo>)`.

### Códigos de saída

- `0` em sucesso (independente do conteúdo do diff — corridas iguais não são erro).
- `1` se algum `run_id` não existir (`FileNotFoundError` em `run.json`, que é sempre gravado pela ADR-0017 — sua ausência é sinal de `run_id` inválido ou não-produzido-por-validate), ou se qualquer `load_*` levantar `ValidationError` (artefato corrompido).
- `2` em erro de flags (argparse).

## Consequences

- **Positive:**
  - Operador ganha um caminho operacional visível para auditar duas corridas — casa de uso comum (rodei com `seed=42`, depois com `seed=123`, o que mudou?).
  - Três consumidores futuros desbloqueados parcialmente: (a) `ranking/` (segurado) pode reusar `_diff_*` para gerar tabelas N×N; (b) ADR futura de `compare --json` é extensão trivial (`_diff_*` já devolve lista de linhas estruturáveis); (c) testes de regressão podem diffar uma corrida canônica contra baseline.
  - As funções `_diff_*` são puras — testáveis sem tocar filesystem.
  - Tráfego de I/O é agnóstico a conteúdo: `compare` não precisa saber o que há dentro dos artefatos além dos schemas declarados. Se ADR futura adicionar campo a `RunMetadata`, basta estender `_diff_run_metadata`.
  - `run.json` agora tem segundo consumidor real (primeiro foi auditoria humana). Valida empiricamente a decisão da ADR-0017 §"Consequences" de que metadados sobreviverem abort é útil.

- **Negative:**
  - Terceiro subcomando na CLI aumenta a superfície pública. Mitigação: zero código de domínio novo; `_cmd_compare` é pura orquestração, como `_cmd_validate`.
  - Output humano não é machine-readable. Mitigação declarada: quem precisar de JSON abre ADR nova; mesmo padrão da ADR-0016 §"Alternatives" (stdout humano, artefatos JSON são contrato).
  - Diff semântico de `flags` é por chave (igualdade exata de string). Se duas corridas usam `--stress fee+10:10:0` e `--stress=fee+10:10:0` (um com `=`, outro sem), argparse normaliza os dois para o mesmo `repr` de lista — não há ambiguidade real; basta documentar que igualdade é sobre o `repr` final coagido pela ADR-0017.
  - `compare` **não** detecta que duas corridas podem ter sido produzidas por versões diferentes do `alpha_forge` até o stdout exibir. Mitigação: a primeira linha da seção `run_metadata` é sempre `alpha_forge_version`, e o operador vê imediatamente.

- **Neutral:**
  - Funções `_diff_*` são privadas (sublinhado) mas documentadas na API como seams de testes — mesmo padrão da `_now_utc` da ADR-0017.
  - Fila de trabalho futura natural: ADR de ranking multiobjetivo (N corridas + composite scoring); ADR de `compare --json` (machine output); ADR de `compare --baseline <run_id>` (N-1 corridas contra referência canônica).

## Alternatives considered

- **Output JSON machine-readable nesta fatia (`--json`)** — rejeitado porque viola o padrão explícito da ADR-0016 §"Alternatives" ("stdout é humano, JSON persistido é o contrato"). O consumidor de ranking vai ler os `load_*` diretamente; não precisa do stdout.
- **Exit code 1 quando corridas divergem em algum campo** — rejeitado porque o valor do subcomando **é** mostrar divergência. Falhar em divergência transforma `compare` em "assert iguais", caso de uso diferente e mais restrito. Se alguém quiser isso, abre ADR de `--strict` ou `assert`.
- **Implementar ranking como passo seguinte direto em vez de compare** — rejeitado porque viola o critério do usuário de pequenas entregas completas. Ranking abre módulo `ranking/` (segurado); compare é uma função de cada lado. ADR-0015/0016/0017 já entregaram os inputs; compare é o consumidor de N=2; ranking é o consumidor de N≥2 — endereçar o degenerado primeiro mantém a cadência.
- **Diff recursivo estrutural (ex: deepdiff) em vez de funções por artefato** — rejeitado porque cada artefato tem contexto semântico diferente: `walk_forward` é lista de folds (interessa agregados), `monte_carlo` tem percentis fixos, `cost_stress` tem labels de cenários como chaves naturais. Um diff estrutural genérico imprimiria ruído (ex: `fills[0].timestamp` de cada fold).
- **Subcomando aceita N ≥ 2 corridas em vez de exatamente duas** — rejeitado porque N≥3 é uma variante de ranking (precisa decidir baseline, formato de tabela larga). Compare é explicitamente N=2 para manter output claro (`a` vs `b` é fácil de ler; `a vs b vs c vs d` vira tabela).
- **Comparar artefatos por hash de arquivo** — rejeitado porque é o contrário do útil: o operador quer saber **onde** as corridas divergem, não se elas divergem.
- **Flags `--run-id-a` / `--run-id-b` em vez de posicionais** — rejeitado porque `compare` é simétrico: `a` e `b` são intercambiáveis na semântica (operador pode ler o diff em qualquer ordem). Posicional curto é a forma idiomática para dois argumentos simétricos; `--run-id-*` adicionaria sete caracteres redundantes por chamada.
- **Imprimir diff unified (estilo `diff -u`) do JSON bruto** — rejeitado porque JSONs dos artefatos contêm blobs grandes (fills, equity curve) cuja diferença linha-a-linha é ruído. O valor está em agregados (total_trades, percentis), não em barras individuais.
- **Usar bibliotecas externas (tabulate, rich) para formato** — rejeitado porque o padrão da ADR-0016 §"stdout humano" é `print` com alinhamento fixo por `:` e espaços. Introduzir dependência só para `compare` viola o guardrail de minimalismo de dependências do ADR-0001.

## Follow-ups

Cada item vira entrada em `STATE.md` como pending; a ADR não os executa.

- Implementar `_cmd_compare` em `cli/app.py` + quatro `_diff_*` privadas.
- Adicionar testes unit das funções `_diff_*` (funções puras sobre pydantic — sem tmp_path).
- Adicionar teste integration que grava duas corridas sintéticas em `tmp_path` via `cli_app.run(["validate", ...])` e chama `cli_app.run(["compare", ...])`.
- Atualizar `system/domain.md`, `system/api.md`, `system/flows.md`, `decisions/README.md`, `STATE.md`.
- Guardrails: `run-demo` e `validate` **não** tocados; suíte continua verde sem um único ajuste; gate anti-hardcode preservado.

### Guardrails declarados para a implementação

1. ADR escrita e aprovada **antes** do código (satisfeito por esta ADR).
2. Terceiro subcomando **não** modifica `run-demo` nem `validate` — reuso via os helpers `_add_shared_log_level_flag` já existentes.
3. Nenhum código de domínio novo — `_cmd_compare` é orquestração pura de `load_*` + `_diff_*` + `print`.
4. Funções `_diff_*` são funções puras sobre schemas pydantic — testadas sem tocar filesystem.
5. Teste integration usa `cli_app.run(["validate", ...])` para produzir corridas reais (mesmo padrão da ADR-0016); `validation_run_dir` é monkeypatched para `tmp_path`.
6. `system/domain.md`, `system/api.md`, `system/flows.md`, `decisions/README.md`, `STATE.md` atualizados.
7. Suíte verde com zero regressões; gate anti-hardcode `rg -n 'BTC|ETH|SOL' src/` = 0 matches.
8. Códigos de saída 0/1/2 conforme declarado acima; `FileNotFoundError` em `run.json` (ausente pela ADR-0017) é tratado como exit 1 com mensagem clara em stderr.
9. Zero mudança em `validation/schemas.py`, `validation/persistence.py`, `validation/walk_forward.py`, `validation/monte_carlo.py`, `validation/cost_stress.py` — compare é pura camada de CLI.
