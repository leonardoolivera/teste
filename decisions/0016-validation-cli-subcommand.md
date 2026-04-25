# 0016 — CLI de validação: subcomando `validate`

**Status:** Accepted
**Date:** 2026-04-17
**Deciders:** Usuário (owner do projeto, em modo autônomo sequencial) + agente.

## Context

`validation/` expõe hoje quatro contratos funcionais (`walk_forward`, `monte_carlo_trades`, `cost_stress`) e seis funções de persistência (`save_*`/`load_*` × 3 artefatos, ADR-0015). A CLI `alpha-forge` tem apenas um subcomando: `run-demo` — carrega dataset, roda um único `run_backtest`, imprime summary. Não existe ponta-a-ponta **operacional** para rodar pipeline de validação completo e persistir os artefatos; o único consumidor hoje é `tests/integration/test_validation_persistence_pipeline.py`, que constrói o pipeline manualmente dentro do teste.

O Next step anterior do `STATE.md` (pós-ADR-0015) identificou três candidatos de escopo controlado. O critério declarado pelo usuário — "pequenas entregas completas sobre grandes entregas parciais" — aponta para o candidato de **menor superfície**: CLI de validação.

Três razões para abrir CLI agora, antes de `ranking/`:

1. **Consolida o que existe.** Walk-forward + MC + cost_stress + persistência estão entregues mas não têm caminho operacional fora de testes. Abrir CLI expõe o produto real — um script que roda pipeline + grava artefatos — sem adicionar lógica de domínio nova.
2. **Produz identidade canônica de corrida.** `run_id` até hoje é string opaca passada pelo chamador (ADR-0015 §"Layout"). A CLI fixa uma convenção operacional: `run_id` é argumento explícito do usuário, sem timestamping implícito — determinismo é pré-requisito para testar a CLI sem mock de clock.
3. **Desbloqueia `ranking/` por composição, não por abstração.** Quando `ranking/` chegar, seu primeiro input natural é um diretório `results/validation/<run_id>/` já gravado por CLI — ranking lê artefatos persistidos, não importa como vieram. Sem CLI, ranking teria que conviver com "execute este Python script ad-hoc primeiro"; com CLI, ranking documenta "rode `alpha-forge validate ...` e aponte o ranking para o run_id".

A decisão desta ADR é abrir o subcomando `validate` no **menor tamanho honesto** — o suficiente para rodar pipeline completo com as mesmas flags já estabelecidas para `run-demo`, persistir os três artefatos via ADR-0015, e imprimir um summary de uma página. Nenhuma descoberta de `run_id` por timestamp, nenhum comparador de corridas, nenhum consumidor de persistência (ranking) — cada um vira ADR própria.

## Decision

Adicionar o subcomando `alpha-forge validate` na CLI existente (`cli/app.py`). **Não** criar módulo CLI separado: o único consumidor de CLI hoje é `cli/app.py`; um segundo irmão (`cli/validate.py`) só se justifica se o subcomando crescer além do limite mínimo, o que não acontece nesta fatia.

### Contrato do subcomando

```
alpha-forge validate --run-id <str>
                     --dataset-id <str>
                     [--capital, --fracao, --alavancagem]
                     [--taker-fee-bps, --slippage-bps-per-notional]
                     [--strategy {ma_crossover,dummy,donchian}]
                     [--short-window, --long-window, --long-only/--no-long-only]
                     [--entry-window, --exit-window]
                     [--n-folds N] [--scheme {rolling,expanding}]
                     [--train-fraction F] [--min-test-bars N]
                     [--mc-resamples N] [--mc-seed N]
                     [--stress label:fee_delta_bps:slip_delta_bps]...
                     [--skip-monte-carlo] [--skip-cost-stress]
                     [--log-level {silent,info,debug}]
```

Regras:

1. **`--run-id` é obrigatório, string opaca.** Nenhum timestamping implícito. Se o diretório `results/validation/<run_id>/` já existir com artefatos, a CLI **sobrescreve** (consistente com ADR-0015 §"sobrescrita permitida").

2. **Walk-forward roda sempre.** É o único contrato não-opcional — é o pivô do pipeline, os outros dois consomem suas saídas (MC) ou seu padrão (cost_stress). Flags de walk-forward têm defaults calibrados (`n_folds=5`, `scheme=rolling`, `train_fraction=0.5`, `min_test_bars=50` — mesmos defaults do integration test ADR-0015).

3. **Monte Carlo é opcional via `--skip-monte-carlo`.** Default: roda. Quando roda, agrega trades de **todos os folds** (mesmo padrão do integration test ADR-0015: `all_trades = sum(f.result.trades for f in folds)`), monta um `BacktestResult` agregado com `dataset_id` original, e chama `monte_carlo_trades(seed=--mc-seed, n_resamples=--mc-resamples)`. Se `all_trades` for vazio, MC é silenciosamente pulado com mensagem no stderr — não é erro (pode acontecer em janela curta com estratégia conservadora); o `monte_carlo.json` simplesmente não é gravado.

4. **Cost stress é opcional via `--skip-cost-stress` ou via lista `--stress` vazia.** Flag `--stress` é repetível e aceita strings `label:fee_delta_bps:slip_delta_bps` (três partes separadas por `:`). Exemplo: `--stress fee+10:10:0 --stress slip+10:0:10`. Parsing é estrito: menos de três partes, nomes duplicados, valores não-float, ou valores negativos levantam erro da CLI antes de rodar qualquer backtest. Labels da linha de comando são os labels das `CostPerturbation`; ordem é preservada no `CostStressReport.scenarios`. Se a lista `--stress` estiver vazia (default) ou `--skip-cost-stress` for passado, cost_stress é pulado e `cost_stress.json` não é gravado.

5. **Summary no stdout.** Uma linha por artefato persistido: caminho canônico, tamanho, contagem de registros (folds, resamples, scenarios). Summary é **legível humano**, não machine-parseable — o contrato machine-parseable é o JSON persistido.

6. **Código de saída.** `0` em caminho feliz. `2` se flags inválidas (argparse default). `1` se um erro de domínio levantou `ValidationError` ou `DatasetIntegrityError` (erro operacional, não bug): CLI imprime a mensagem curta no stderr e sai com 1. Exceções inesperadas sobem (stacktrace — é bug, queremos ver).

### O que o subcomando `validate` NÃO faz

- **Não gera `run_id` automaticamente.** Determinismo é pré-requisito para testar a CLI.
- **Não aceita múltiplas estratégias por corrida.** Cada corrida = uma estratégia. Grid de estratégias é trabalho de `ranking/` (segurado).
- **Não aceita múltiplos datasets por corrida.** Mesmo motivo.
- **Não compara corridas.** Comparação vira subcomando `compare` ou vira input de `ranking/` — ADR própria quando necessário.
- **Não tenta descobrir `run_id` pré-existentes.** Nenhum `alpha-forge validate --list` ou `--show <run_id>`. Inspeção de artefatos é `cat results/validation/<run_id>/*.json` com qualquer ferramenta JSON.
- **Não expõe tuning de parâmetros.** Walk-forward não tuna; continua como ADR-0003 §"não entra neste núcleo mínimo".
- **Não escreve log de execução em `results/validation/<run_id>/`.** Stdout é suficiente para auditoria manual; persistir log vira ADR quando houver consumidor automatizado.

## Consequences

**Positivas:**

- Primeiro caminho operacional ponta-a-ponta para `validation/` fora de testes.
- `run_id` canonizado como string opaca controlada pelo usuário — mesmo contrato da ADR-0015, agora exposto na CLI.
- Três artefatos persistidos com uma invocação; cada um **independente** (mesmo contrato da ADR-0015 §"artefatos são independentes").
- Reaproveita 100% da infraestrutura de flags do `run-demo` — nova superfície de código é mínima.
- Desbloqueia `ranking/` por composição: qualquer rankder futuro consome um diretório `results/validation/<run_id>/`, não precisa saber como foi gerado.

**Negativas aceitas:**

- **Parsing manual de `--stress`** adiciona ~15 linhas de código + testes próprios. Formato `label:fee:slip` é ergonômico mas exige validação. Alternativa rejeitada: aceitar JSON inline (mais flexível mas ilegível em linha de comando).
- **Sobrescrita silenciosa** de artefatos pré-existentes pode mascarar erro de `run_id` copiado. Aceitável: o caso dominante é re-executar o mesmo pipeline com parâmetros revisados; "proteger" com confirmação interativa quebra CI.
- **Summary não é machine-parseable.** Consumidores automatizados devem ler os JSONs persistidos, não o stdout. É intencional — stdout é para humano; JSON é o contrato.
- **CLI não ganha subcomando `run-demo-validate` ou similar.** Reaproveitar o mecanismo de "run-demo + validate" em um comando só foi rejeitado: `run-demo` tem objetivo didático/sanidade; `validate` tem objetivo de produção. Misturar os dois confunde.

## Alternatives considered

1. **Gerar `run_id` automaticamente por timestamp ou hash dos inputs.** Rejeitado: quebra testabilidade (precisaria mock de clock ou de hash), e o chamador já tem a informação que faria o `run_id` significativo (nome do experimento, iteração do grid). Deixar explícito é mais honesto.

2. **Aceitar `--stress-file <path.json>` em vez de `--stress label:fee:slip` repetível.** Rejeitado para este ciclo: arquivo JSON separado introduz nova convenção de formato (que precisaria ADR própria) para economizar poucos caracteres em linha de comando. Lista repetível é o padrão Unix (`-I` do `xargs`, `-D` do `gcc`). Quando o número de perturbações crescer, abre-se uma ADR de "stress plan file" — não agora.

3. **Permitir múltiplas estratégias por chamada (grid).** Rejeitado: primeiro consumidor de grid é `ranking/`, que é segurado. Adicionar grid na CLI sem ranking significa "imprime várias tabelas, sem comparação" — deselegante e adiantado.

4. **Rodar walk-forward e persistir, depois rodar MC e persistir, depois cost_stress e persistir — em três subcomandos separados** (`validate-walk`, `validate-mc`, `validate-stress`). Rejeitado: triplica superfície de flags (cada um precisaria `--dataset-id`, `--strategy`, `--capital`, etc.), e o caso dominante é rodar os três juntos. Subcomandos separados só fazem sentido se os três puderem ser consumidos independentemente com contratos muito diferentes — não é o caso.

5. **Passar perturbações como `--fee-deltas 10,20,30 --slip-deltas 0,0,0 --stress-labels fee+10,fee+20,fee+30`.** Rejeitado: três listas paralelas por índice são mais frágeis que uma lista de triplas (`label:fee:slip`). Padrão Unix é evitar acoplamento posicional entre listas.

6. **Emitir machine-readable summary em stdout (JSON Lines).** Rejeitado: stdout é para humano, JSON persistido é o contrato. Duplicar o contrato em dois lugares dobra a superfície de versionamento.

7. **Escrever um `run.json` com metadados da corrida** (flags passadas, timestamp, versão do `alpha_forge`). Rejeitado nesta ADR: útil para auditoria, mas é **quarta** forma de persistência — merece ADR própria (`ADR de metadados de corrida`) quando houver consumidor. Hoje, o `dataset_id` já viaja dentro dos payloads; parâmetros da estratégia podem ser recuperados rodando de novo; timestamp está no filesystem (`mtime`).

8. **Gerar `run_id` determinístico pela hash dos parâmetros + dataset.** Rejeitado: cria dependência forte entre "identidade da corrida" e "parâmetros da corrida", o que impede re-executar um `run_id` com parâmetros revisados (case dominante: descobri bug no `seed`, rodo de novo com mesmo nome). Deixar `run_id` como string opaca é mais maleável.

9. **Criar módulo `cli/validate.py` separado.** Rejeitado: um único subcomando extra não justifica arquivo novo. Quando `cli/app.py` passar de ~500 linhas ou quando houver 3+ subcomandos, reavaliar.

## Guardrails desta ADR

1. ADR escrita e aprovada **antes** do código.
2. Subcomando novo **não** modifica `run-demo` — testes existentes (CLI + `test_engine_observability.py`) continuam verdes sem ajuste.
3. Nenhum código de domínio novo em `validation/` — CLI é lado passivo que orquestra o que já existe.
4. Parsing de `--stress` tem testes unit dedicados (formato válido, formatos inválidos, labels duplicados, valores negativos).
5. Subcomando tem teste integration end-to-end: chama `run(["validate", ...])` com `--run-id` apontando para `tmp_path`; assert que os três artefatos foram gravados; carrega com `load_*` e verifica round-trip estrutural.
6. `system/domain.md`, `system/api.md`, `system/flows.md`, `decisions/README.md`, `STATE.md` atualizados.
7. Suíte verde.
8. Gate anti-hardcode `rg -n 'BTC|ETH|SOL' src/` = 0 matches.

## Follow-ups

Esta ADR **não** abre:

- Descoberta de corridas (`alpha-forge validate --list`).
- Comparação de corridas (`alpha-forge compare <run_a> <run_b>`).
- Metadados de corrida (`run.json` com flags + timestamp + versão).
- `--stress-file` (JSON externo).
- Grid de estratégias ou datasets em uma chamada.
- Tuning de parâmetros por fold (ADR própria com gate anti-overfitting).

Cada um vira ADR quando houver consumidor concreto. A decisão desta ADR é apenas: **o pipeline completo de validação é invocável via CLI em uma chamada, e persiste seus artefatos via ADR-0015**.
