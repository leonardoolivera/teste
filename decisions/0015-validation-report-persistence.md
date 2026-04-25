# 0015 — Persistência de relatórios de validação

**Status:** Accepted
**Date:** 2026-04-17
**Deciders:** Usuário (owner do projeto, em modo autônomo sequencial) + agente.

## Context

`validation/` expõe hoje três contratos (ADR-0003 + ADR-0014): `walk_forward`, `monte_carlo_trades`, `cost_stress`. Todos são funções puras sem I/O, devolvem objetos pydantic `frozen` em memória.

Duas ADRs abriram pontos explícitos sobre persistência e deliberadamente **não** a entregaram:

- ADR-0003 §"Alternatives considered" rejeitou `results/validation/` no mesmo ciclo por falta de consumidor (`ranking/` ainda não existe) — "formato do arquivo hoje seria chute; amanhã seria dívida".
- ADR-0014 §"Follow-ups" deixou explícito: persistência de `CostStressReport` fica para ADR futura quando `ranking/` precisar consumir.

O Next step anterior do `STATE.md` (pós-ADR-0014) identificou **persistência de relatórios** como o próximo passo mecânico-mas-arquitetural de menor superfície — precursor leve de `ranking/`. Desbloqueia dois consumos futuros sem desenhá-los já: (a) `ranking/` lê relatórios persistidos para agregar entre estratégias; (b) notebooks / relatórios compartilháveis podem anexar artefatos sem rodar backtest de novo.

A decisão desta ADR é abrir persistência no **menor tamanho honesto** — o suficiente para round-trip bit-a-bit dos três artefatos que já existem, com contrato versionado, e deixar extensões (compactação, streaming, migração entre versões, identidade por hash) para ADRs próprias quando cada uma tiver caso de uso.

## Decision

Abrir `validation/persistence.py` dentro do módulo `validation/` já existente. **Não** criar módulo de persistência genérico na raiz: o único consumidor de persistência hoje é `validation/`; promover a módulo raiz sem segundo irmão é desenhar abstração sem evidência.

Escopo mínimo desta ADR:

1. **Formato: JSON (uma linha por arquivo, pretty-print opcional).**
   - Relatórios de validação são objetos **pequenos e aninhados**, não tabelas colunares. Parquet/Arrow resolveriam o problema errado (eficiência colunar) introduzindo um problema novo (schema alinhado entre artefatos heterogêneos).
   - JSON nativo: legível em inspeção manual; round-trip bit-a-bit via pydantic `model_dump_json()` / `model_validate_json()`; `datetime` serializado como ISO 8601 (default do pydantic); `float` com precisão IEEE 754 (strict — round-trip preserva).
   - Encoding fixo: UTF-8 sem BOM.

2. **Layout de diretório.**
   - Raiz: `results/validation/<run_id>/`.
   - `run_id` é uma string opaca passada pelo chamador — convenção sugerida (não imposta) é `f"{dataset_id}__{strategy_slug}__{timestamp_utc}"`, mas a ADR **não** fixa essa convenção; o chamador é responsável por unicidade dentro do diretório. Se o diretório já existir com artefatos, as funções `save_*` **sobrescrevem** (sem confirmação) — round-trip em testes + CI é o caso de uso dominante; "protegê-lo" com `exist_ok=False` gera fricção sem ganho. Quem quiser idempotência por hash implementa em camada acima.
   - Três nomes de arquivo fixos dentro do diretório:
     - `walk_forward.json` — lista de `WalkForwardFold`.
     - `monte_carlo.json` — um `MonteCarloSummary`.
     - `cost_stress.json` — um `CostStressReport`.
   - Cada artefato é opcional: uma corrida que não rodou Monte Carlo não precisa ter `monte_carlo.json`. `load_*` levanta `FileNotFoundError` se o artefato pedido não existir.

3. **Envelope com `schema_version`.**
   - Todo JSON persistido começa com um envelope de dois campos:
     ```json
     {
       "schema_version": "1",
       "payload": { ... o objeto pydantic serializado ... }
     }
     ```
   - `schema_version` é **string** (`"1"`, `"2"`, etc.) — não `int`, não semver. String força escolha explícita de identificador; números convidam aritmética indevida.
   - Versão atual fixa: `"1"` para os três artefatos.
   - `load_*` valida `schema_version == "1"`; diferente → `ValidationError` com mensagem explícita indicando qual artefato, o valor lido e o esperado. **Não** tenta migração. Migração entre versões é ADR separada.
   - Chave `payload` contém o dump pydantic exato do objeto — sem transformação. Garantir round-trip bit-a-bit.

4. **Contrato funcional.**
   - `validation/persistence.py::save_walk_forward_folds(*, folds: list[WalkForwardFold], directory: Path) -> Path` — grava `directory/walk_forward.json`; cria `directory` se não existir; devolve o `Path` gravado.
   - `validation/persistence.py::save_monte_carlo_summary(*, summary: MonteCarloSummary, directory: Path) -> Path` — grava `directory/monte_carlo.json`.
   - `validation/persistence.py::save_cost_stress_report(*, report: CostStressReport, directory: Path) -> Path` — grava `directory/cost_stress.json`.
   - `validation/persistence.py::load_walk_forward_folds(*, directory: Path) -> list[WalkForwardFold]`.
   - `validation/persistence.py::load_monte_carlo_summary(*, directory: Path) -> MonteCarloSummary`.
   - `validation/persistence.py::load_cost_stress_report(*, directory: Path) -> CostStressReport`.
   - Funções puras do ponto de vista do chamador (sem estado global; I/O é efeito colateral, mas não atravessa processos). Namespace exposto em `validation/__init__.py`.

5. **Validações.**
   - `save_*`: `directory` existe ou é criado (`mkdir(parents=True, exist_ok=True)`); `list[]` vazio para `save_walk_forward_folds` é **permitido** (casos reais podem ter zero folds válidos após filtragem) — grava array JSON vazio com envelope versionado. Para consistência: `load_walk_forward_folds` devolve `[]` nesse caso.
   - `load_*`: `FileNotFoundError` se o arquivo não existir; `ValidationError` se (a) JSON malformado; (b) envelope ausente dos campos `schema_version`/`payload`; (c) `schema_version != "1"`; (d) `payload` viola schema pydantic. Mensagem cita o arquivo para facilitar diagnóstico.

6. **Separação clara de responsabilidades.**
   - `persistence.py` só sabe **gravar e ler**. Não agrega, não sumariza, não renderiza tabela, não gera `run_id`, não detecta duplicatas. Essas responsabilidades são de camadas acima (`ranking/`, relatórios de notebook, CLI) e ficam deferred.
   - `io/paths.py` ganha **uma** função nova: `validation_run_dir(run_id: str) -> Path` resolvendo `results_dir() / "validation" / run_id`. Consistência com o resto de `io/paths.py` (resolução canônica centralizada).

7. **Integração com os contratos existentes — zero mudança.**
   - `walk_forward`, `monte_carlo_trades`, `cost_stress` **não** mudam nem um caractere. Continuam puras em memória. `persistence.py` é camada passiva que **consome** os objetos devolvidos.
   - Os três schemas (`WalkForwardFold`, `MonteCarloSummary`, `CostStressReport`) não ganham campos. Envelope de versionamento vive **só** na serialização; objetos em memória continuam limpos.
   - Nenhum campo novo em `BacktestResult`, `BacktestMetrics`, `CostModel`.

8. **Testes obrigatórios como critério de "entregue".**
   - Unit: `tests/unit/test_validation_persistence.py` — três classes, uma por artefato, cobrindo:
     - Round-trip bit-a-bit (`save` + `load` em `tmp_path`, objeto carregado é `==` ao original via pydantic `__eq__`; para `BacktestResult` aninhado, comparação estrutural pydantic).
     - Caminho devolvido corresponde a `directory / <nome_fixo>.json`.
     - `directory` inexistente é criado.
     - `schema_version` no JSON gravado é `"1"` (inspeção direta do texto).
     - `load_*` sobre `schema_version = "2"` adulterado no arquivo → `ValidationError` com mensagem explícita.
     - `load_*` sobre JSON malformado → `ValidationError`.
     - `load_*` sobre arquivo inexistente → `FileNotFoundError`.
     - Para walk-forward: `save` + `load` de lista vazia é round-trip válido.
   - Integration: `tests/integration/test_validation_persistence_pipeline.py` — end-to-end: rodar `walk_forward` + `monte_carlo_trades` + `cost_stress` sobre MA 20/50 no sintético seminal; persistir os três em `tmp_path / "run_abc"`; carregar de volta; verificar que `final_equity`, `trade_count` e percentis são preservados bit-a-bit.

## Consequences

- **Positive:** `validation/` ganha lado passivo (persistência) sem tocar lado ativo (funções). `ranking/` pode ser aberto em ADR futura consumindo artefatos persistidos em vez de exigir re-execução. Notebooks e relatórios podem anexar JSONs compartilháveis. `schema_version` explícito desde o dia 1 evita dívida de migração silenciosa. Round-trip bit-a-bit testado dá segurança de que o formato é estável.
- **Negative:** JSON não é ideal para volumes grandes — `BacktestResult` com muitos trades ou `equity_curve` extensa pode gerar arquivos de alguns MB. Hoje é aceitável (datasets reais de 4320 barras × MA 20/50 geram ~200 trades; estimativa conservadora < 1 MB por artefato); se virar problema, ADR futura introduz `save_trades_only=True` ou compressão gzip. Persistir `BacktestResult` inteiro por fold significa que `walk_forward.json` pode crescer linearmente em `n_folds × trades_por_fold` — linearidade esperada, não patológica.
- **Neutral:** `validation/persistence.py` é o **segundo** irmão de `validation/` (primeiro foi walk-forward, segundo foi monte_carlo, terceiro foi cost_stress, quarto agora é persistence). Quando o quinto irmão entrar, vale revisar se o namespace está virando "tudo que é validação"; hoje ainda é coeso. A escolha "sobrescrever sem perguntar" é contrato — se um dia virar suscetível a perda acidental de dados, ADR futura introduz `exist_ok=False` ou lock.

## Alternatives considered

- **Formato Parquet/Arrow.** — Rejeitado: otimiza o caso errado (tabela colunar homogênea); força schema alinhado entre artefatos que são heterogêneos. Rescrita do pipeline depois de entrar em Parquet seria cara; JSON é barato de trocar se houver evidência de necessidade.
- **Um único arquivo `report.json` agregando tudo.** — Rejeitado: os três artefatos são produzidos por funções diferentes em momentos diferentes; um relatório parcial (só walk-forward, sem MC) ficaria com estrutura incompleta no arquivo único. Arquivos separados modelam essa parcialidade naturalmente.
- **Incluir `run_id` dentro do JSON como campo.** — Rejeitado: `run_id` já é o nome do diretório; duplicar no payload convida divergência (quem é a verdade — o diretório ou o campo?). O chamador que quiser registrar contexto adicional (`strategy`, `dataset_id`, `timestamp`) faz isso em uma ADR futura de metadados, não aqui.
- **`schema_version` como `int` (1, 2, 3).** — Rejeitado: convida comparação aritmética (`schema_version >= 2`); `string` força switch/match explícito.
- **Compressão automática (gzip).** — Rejeitado nesta ADR: tamanho atual é compatível com leitura humana direta; gzip adiciona um passo e mascara erros de codificação. Se crescer, ADR futura adiciona `save_*_gzipped` como variante.
- **Migração entre versões de schema.** — Rejeitado: hoje só existe versão 1. Migração sem caso concreto vira código morto. Quando surgir versão 2, ADR nova define a trajetória.
- **Identidade por hash (conteúdo-como-nome).** — Rejeitado: interessante para deduplicação em cache, mas acopla nome de arquivo a serialização; mudar uma regra de formatação invalida nomes anteriores. Deixar o chamador decidir `run_id` é mais simples.
- **Levantar em sobrescrita (`exist_ok=False`).** — Rejeitado: CI e testes gravam no mesmo diretório repetidamente; `exist_ok=False` criaria ritual de limpeza. Sobrescrita é o comportamento esperado.
- **Abrir `ranking/` junto.** — Rejeitado (regra AGENTS.md §4): núcleo mínimo primeiro. Persistência isolada é auto-contida e desbloqueia; `ranking/` é a próxima ADR que consumirá, não esta.
- **Expor CLI `alpha-forge validate --save ...`.** — Rejeitado (mesma regra da ADR-0003 e ADR-0014): CLI para `validation/` vira follow-up de `ranking/`. Funções chamáveis via Python + testáveis bastam.
- **Persistir `BacktestResult` **sem** `equity_curve` e `fills` por default (só `metrics` e `trades`).** — Rejeitado: truncagem silenciosa quebra round-trip bit-a-bit e contraria o próprio objetivo de reprodutibilidade. Se o tamanho virar problema concreto, ADR futura introduz variante `save_trades_only=True` como **opção explícita**, não default.

## Follow-ups

- Implementar `src/alpha_forge/validation/persistence.py` (6 funções + envelope interno) no mesmo ciclo desta ADR.
- Atualizar `src/alpha_forge/validation/__init__.py` reexportando as 6 funções.
- Adicionar `validation_run_dir(run_id)` em `src/alpha_forge/io/paths.py`.
- Escrever `tests/unit/test_validation_persistence.py` e `tests/integration/test_validation_persistence_pipeline.py`.
- Atualizar `system/domain.md`, `system/api.md`, `system/flows.md`, `decisions/README.md`, `STATE.md`.
- **Não abrir**: compressão gzip (ADR futura se crescer); migração entre versões (ADR quando surgir v2); identidade por hash (ADR separada); CLI (follow-up de `ranking/`); metadados de contexto (`strategy`, `timestamp`) no envelope (ADR separada se `ranking/` precisar); `save_trades_only=True` (ADR futura se tamanho virar problema); abrir `ranking/` consumidor (ADR separada).
