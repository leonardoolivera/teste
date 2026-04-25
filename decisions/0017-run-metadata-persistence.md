# 0017 — Metadados de corrida: `run.json` ao lado dos artefatos de validação

**Status:** Accepted
**Date:** 2026-04-17
**Deciders:** Usuário (owner do projeto, em modo autônomo sequencial) + agente.

## Context

A ADR-0016 (`alpha-forge validate`) tornou `run_id` uma string opaca escolhida pelo chamador — sem rastro automático de **como** cada corrida foi produzida. Hoje, um diretório `results/validation/<run_id>/` tem três JSONs de artefatos (ADR-0015) mas nenhum registro de:

- Qual versão do `alpha_forge` rodou a corrida.
- Quando a corrida foi executada.
- Quais flags foram passadas na CLI (`--strategy`, `--n-folds`, `--stress`, etc.).

O `dataset_id` viaja dentro dos payloads e é recuperável; parâmetros da estratégia e do walk-forward **não são** — precisam inferência reversa do comportamento dos folds, o que é frágil e às vezes ambíguo (ex.: `scheme=rolling` vs `expanding` no caso degenerado de `train_fraction=1`).

Dois consumidores futuros já documentados no STATE.md precisarão desse rastro:

1. **ADR de comparação de corridas** (Opção B do Next step anterior): um `compare <run_a> <run_b>` precisa saber se as duas corridas usaram **a mesma versão do código**. Sem versão persistida, a comparação silencia bugs introduzidos entre runs.
2. **`ranking/` futuro** (segurado): ranking multiobjetivo sobre corridas requer saber quais flags foram usadas (estratégia, parâmetros, custos). Hoje, o `cost_stress` persiste `baseline_cost` dentro de si, mas walk-forward e Monte Carlo não persistem a estratégia nem os parâmetros do budget — ranking precisaria inferir.

O Next step anterior do `STATE.md` (pós-ADR-0016) identificou metadados de corrida como **Opção A** — menor superfície, consolida o que existe, não abre módulo novo. É a primeira opção recomendada explicitamente: "menor superfície de todas, completa a ADR-0016 em seu ponto mais honesto (hoje `run_id` é opaco mas sem rastro de como foi produzido)".

A decisão desta ADR é abrir metadados de corrida no **menor tamanho honesto** — um único arquivo novo por `run_id`, envelope versionado igual ao dos três artefatos, gravado pela CLI no início da execução (antes de qualquer backtest rodar), com campos suficientes para auditoria reprodutível e nada além.

## Decision

Adicionar um quarto artefato opcional por `run_id`: `run.json`, gravado em `results/validation/<run_id>/run.json` no mesmo envelope JSON da ADR-0015 (`{"schema_version": "1", "payload": ...}`).

### Schema `RunMetadata` (novo em `validation/schemas.py`)

```python
class RunMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    alpha_forge_version: str = Field(min_length=1)
    timestamp_utc: datetime                              # sempre timezone-aware UTC
    command: str = Field(min_length=1)                   # e.g. "validate"
    run_id: str = Field(min_length=1)
    flags: dict[str, str]                                # todas as flags coagidas a string
```

Decisões explícitas:

1. **`flags: dict[str, str]`** — todas as flags são coagidas a string na gravação. Rejeita-se `dict[str, str | int | float | bool | list[str]]` porque:
   - Union heterogêneo dificulta validação e introduz ambiguidade (`"5"` é `int` ou `str`?).
   - O caso dominante de leitura é humana (auditoria) ou diff textual (comparação de corridas) — ambos operam sobre string.
   - Consumer futuro que precise do valor tipado pode parsear; consumer que só quer diff não paga overhead.
   - `list[str]` da flag `--stress` é serializada como `"[fee+10:10:0, slip+10:0:10]"` — formato inspecionável, não re-executável. Quem quiser re-executar, lê `run.json` manualmente.

2. **`timestamp_utc: datetime` timezone-aware UTC**. `datetime.now(timezone.utc)` na CLI; serialização ISO 8601 pelo pydantic (default). Rejeita-se `datetime` naive (ambiguidade) e string ISO com regex de validação (reinventa o que pydantic já faz).

3. **`alpha_forge_version` lido de `alpha_forge.__version__`** no momento da gravação. Hoje é `"0.0.0"` — está no README e é honesto. Quando o projeto ganhar versões reais (`0.1.0`, etc.), o rastro vira útil imediatamente sem mudança de código.

4. **`command: str`** — hoje só pode ser `"validate"`. Reserva o campo para quando outros subcomandos persistirem metadados (ex.: futuro `compare` que escreva seu próprio `run.json` em diretório próprio — ADR separada).

5. **`run_id` está no metadata E no nome do diretório** — redundância deliberada. Facilita auditoria em lote (grep por `run_id` no conteúdo dos arquivos); custo é ~40 bytes por arquivo.

### Persistência — novo par em `validation/persistence.py`

```python
_RUN_METADATA_FILENAME = "run.json"

def save_run_metadata(*, metadata: RunMetadata, directory: Path) -> Path:
    """Grava `metadata` em `directory/run.json`. Sobrescreve se existir."""

def load_run_metadata(*, directory: Path) -> RunMetadata:
    """Carrega `directory/run.json`. Levanta FileNotFoundError / ValidationError
    com as mesmas regras de envelope da ADR-0015."""
```

Mesma mecânica dos outros seis `save_*`/`load_*`: envelope `{"schema_version": "1", "payload": ...}`, sobrescrita permitida, `schema_version` string, `FileNotFoundError` se ausente, `ValidationError` se envelope/payload inválido. Quatro artefatos agora são todos **independentes** entre si.

### Integração com `alpha-forge validate` (ADR-0016)

A CLI `validate` grava `run.json` **antes** de rodar walk-forward — assim, mesmo se a corrida abortar por `ValidationError` no meio do pipeline, o rastro sobrevive ("tentamos rodar X com flags Y e quebrou"). Ordem:

1. Parse de flags + validação de `--stress`.
2. Constrói `RunMetadata` capturando: versão do pacote + timestamp UTC atual + `command="validate"` + `run_id` do argumento + `dict(flags)` derivado do `argparse.Namespace` coagido a string.
3. Chama `save_run_metadata(metadata=..., directory=validation_run_dir(run_id))`.
4. Roda walk-forward → MC → cost_stress normalmente (fluxo ADR-0016 inalterado).

Summary no stdout ganha uma linha adicional:

```
run_metadata     : alpha_forge=0.0.0, ts=2026-04-17T14:23:05Z → results/validation/<run_id>/run.json
```

### O que esta ADR NÃO faz

- **Não persiste `alpha-forge run-demo`.** `run-demo` é didático/sanidade; não tem `run_id` nem diretório de saída. Quando tiver, vira ADR separada.
- **Não persiste host info** (hostname, OS, Python version, CPU). Dados de host vazam info não-essencial e em alguns contextos (CI, notebooks compartilhados) viram ruído. Quando houver caso de uso, ADR própria.
- **Não persiste env vars nem caminhos absolutos.** Mesma razão — ruído e potencial vazamento de paths privados.
- **Não permite o chamador anexar metadados arbitrários** (ex.: `--meta experiment=alpha --meta branch=feature/x`). Campo genérico `extra: dict[str, str]` foi explicitamente rejeitado — introduz semântica livre sem consumidor e deixa schema frouxo. Se um caso surgir, ADR própria com campos tipados.
- **Não tenta reconstruir a corrida a partir do `run.json`.** O arquivo é auditoria, não reexecução. "Rode de novo" é responsabilidade do usuário lendo as flags e montando a linha de comando.
- **Não assina criptograficamente o `run.json`.** Integridade via hash/sha é overkill pro caso de uso hoje; se surgir necessidade (auditoria adversarial, shared storage), ADR separada.

## Consequences

**Positivas:**

- Primeira forma de rastro declarativo da corrida: "quem rodou, quando, com que código, com que flags".
- Desbloqueia comparação de corridas (Opção B) e `ranking/` (Opção D) sem acoplamento: ambos leem `run.json` via `load_run_metadata`.
- Envelope idêntico ao da ADR-0015 → round-trip bit-a-bit grátis (`==` de pydantic frozen).
- Persiste **antes** do pipeline rodar: corridas que abortam no meio ainda deixam rastro auditável.
- Superfície mínima: 1 schema novo, 2 funções de persistência novas, ~5 linhas de integração na CLI, testes focados.

**Negativas aceitas:**

- **`flags: dict[str, str]`** perde tipagem original. Consumer que precisa de `int(--n-folds)` parseia o string; é custo real mas pequeno comparado com a complexidade de union heterogêneo.
- **Timestamp UTC atual quebra reprodutibilidade bit-a-bit** entre duas corridas com mesmas flags — dois `run.json` gravados em instantes diferentes terão `timestamp_utc` diferentes. Isso é *desejado*: o campo existe justamente para desambiguar corridas idênticas em flags. Quem quiser round-trip bit-a-bit em testes injeta timestamp via helper (ver guardrails).
- **Sobrescrita silenciosa** de `run.json` pré-existente (consistente com ADR-0015). Aceitável: re-executar o mesmo `run_id` é caso dominante; "proteger" com confirmação quebra CI.
- **`alpha_forge.__version__="0.0.0"` hoje** — honesto, e o rastro fica melhor automaticamente quando a versão avançar. Não vale adiar ADR esperando versões reais.
- **CLI ganha 1 chamada I/O adicional no início** (`save_run_metadata`). Custo: ~1ms. Não relevante.

## Alternatives considered

1. **Persistir metadados dentro de cada um dos três envelopes existentes** (`walk_forward.json`, `monte_carlo.json`, `cost_stress.json`). Rejeitado: triplica a informação, viola a independência dos artefatos (ADR-0015), e acopla walk-forward ao fato de ter vindo de CLI (um notebook chamando `save_walk_forward_folds` diretamente teria que inventar metadados falsos).

2. **Campo `extra: dict[str, str]` livre no schema.** Rejeitado: semântica livre sem consumer concreto; deixar schema rígido força ADR quando um caso real surgir.

3. **Persistir objetos tipados (`RiskBudget`, `CostModel`, parâmetros da estratégia)** em vez de `dict[str, str]`. Rejeitado por esta ADR: seria duplicação parcial (o `cost_stress.json` já guarda `CostModel` no baseline; walk-forward já guarda `dataset_id` em cada fold). A coerção a string é o formato mais neutro para diff + auditoria. Quando `ranking/` precisar de objetos tipados, ADR dedicada os expõe via load reverso ou via persistência paralela.

4. **Hash SHA256 do conteúdo dos três artefatos dentro do `run.json`.** Rejeitado: não há caso de uso (adversarial? shared storage com risco de corrupção silenciosa?). Pode ser folow-up quando houver.

5. **`timestamp_utc` como string ISO 8601 no schema.** Rejeitado: pydantic já faz round-trip bit-a-bit de `datetime` timezone-aware via `model_dump(mode="json")` → string ISO + `model_validate` ← string ISO. Usar `str` no schema perde validação de formato.

6. **`RunMetadata.flags` como `tuple[tuple[str, str], ...]`** (ordenado). Rejeitado: ganho marginal (ordem das flags é ordem de declaração no argparse, não afeta semântica), custo em ergonomia de leitura (dict é mais legível).

7. **Gravar `run.json` no **fim** do pipeline, não no início.** Rejeitado: corridas que abortam no meio perdem rastro. O uso dominante de auditoria é "algo quebrou, o que foi que tentei rodar?".

8. **Gravar `run.json` em diretório separado (`results/runs/<run_id>/`).** Rejeitado: separa fisicamente metadados dos artefatos, forçando dois paths por `run_id`. ADR-0015 já fixou `results/validation/<run_id>/` como raiz da corrida; metadados moram junto.

9. **Expor subcomando novo `alpha-forge inspect <run_id>`** que imprime `run.json` formatado. Rejeitado nesta ADR: `cat results/validation/<run_id>/run.json | jq` é suficiente hoje. Quando houver mais campos ou comparação side-by-side, ADR própria.

## Guardrails desta ADR

1. ADR escrita e aprovada **antes** do código.
2. `RunMetadata` é pydantic frozen + `extra="forbid"`, mesmo rigor dos outros schemas de `validation/`.
3. `save_run_metadata` / `load_run_metadata` reusam `_write_envelope` / `_read_envelope` de `persistence.py` — zero duplicação de lógica de envelope/versionamento.
4. Round-trip bit-a-bit é testado em unit com `timestamp_utc` fixo (construído manualmente no teste, não via `datetime.now`).
5. Integração CLI é testada: `validate` grava `run.json` antes dos outros artefatos; teste usa `monkeypatch` de `datetime` ou injeta `timestamp_utc` via helper para determinismo.
6. Nenhum dos contratos existentes é modificado (`walk_forward`, `monte_carlo_trades`, `cost_stress`, os seis `save_*`/`load_*` da ADR-0015, nem o subcomando `validate` em seu fluxo de pipeline).
7. `system/domain.md`, `system/api.md`, `system/flows.md`, `decisions/README.md`, `STATE.md` atualizados.
8. Suíte verde.
9. Gate anti-hardcode `rg -n 'BTC|ETH|SOL' src/` = 0 matches.

## Follow-ups

Esta ADR **não** abre:

- `alpha-forge compare <run_a> <run_b>` — desbloqueado por esta ADR, mas é Opção B do backlog.
- Persistência de metadados para `run-demo`.
- Host info no metadata.
- `extra: dict[str, str]` para anotações livres.
- Assinatura/hash do `run.json`.
- Subcomando `inspect`.
- Reexecução a partir do `run.json`.

Cada um vira ADR quando houver consumidor concreto.
