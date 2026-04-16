# 0009 — First real dataset: BTC/USDT 1h, 180 days, Binance Vision dumps

**Status:** Accepted
**Date:** 2026-04-16
**Deciders:** Usuário (owner do projeto) + agente.

## Context

O laboratório hoje prova contrato de estratégia, causalidade, custos, métricas e pipeline end-to-end **exclusivamente sobre o dataset sintético seminal** (`synthetic_btcusdt_1h_seed42`, 720 barras). Isso foi suficiente para estabilizar o núcleo, mas é um teto: ruído Gaussiano com drift constante não tem regimes, não tem gaps reais, não tem microestrutura, não tem fins de semana, não tem manutenção de exchange. Qualquer conclusão tirada daí é sobre o pipeline, não sobre mercado.

O próximo salto de maturidade é fazer o laboratório encostar em **um pedaço pequeno de mundo real**. Pequeno de propósito: o objetivo desta ADR não é encontrar edge, é **validar `loaders.py`, `DatasetManifest`, `declared_gaps` e o engine sob dado real**. Ainda não é hora de abrir grid, múltiplos timeframes ou integração contínua de download.

**Constraint de primeira classe (explícita pelo usuário):** Alpha Forge é **multi-asset por design**. O manifesto, o loader, o pathing e todos os contratos de domínio precisam refletir isso desde já — **nenhum hardcode de `BTC`, `BTCUSDT` ou qualquer par específico em código compartilhado**. O recorte inicial desta ADR (um único par) é **disciplina operacional** para a primeira rodada de validação real, não uma limitação conceitual do sistema. A infra já entregue (ADR-0005 com `symbol` como campo do manifesto, `data/processed/<symbol>/<timeframe>/<dataset_id>.parquet` como path) foi desenhada multi-asset; esta ADR reafirma e endurece essa decisão.

ADR-0001 manteve `ccxt` como direção macro mas **deferred** para esta fase — integração com exchanges ao vivo traz superfície nova (credenciais, rate limits, versionamento de API) incompatível com o ritmo atual. ADR-0005 já cobriu versionamento, manifesto, imutabilidade e política de gaps; esta ADR **não muda ADR-0005**, apenas seleciona a fonte concreta e o recorte do primeiro dataset real que respeita aquelas regras.

## Decision

### 1. Fonte dos dados

**Binance Vision** — dumps públicos em ZIP disponibilizados em `https://data.binance.vision/`, organizados por `data/spot/monthly/klines/<SYMBOL>/<INTERVAL>/<SYMBOL>-<INTERVAL>-<YYYY-MM>.zip`.

- Cada ZIP contém um CSV com as colunas oficiais da Binance para klines: `open_time, open, high, low, close, volume, close_time, quote_volume, trades, taker_buy_base, taker_buy_quote, ignore`.
- **Não requer autenticação, não requer API key, não requer `ccxt`.** Sem dependência Python nova — `urllib.request` + `zipfile` + `csv` da stdlib bastam. `pyarrow` já existe no projeto para escrever o Parquet final.
- **Rejeitado explicitamente:** `ccxt` nesta fase (mantém deferred de ADR-0001); CSVs obtidos à mão (não reproduzível sem intervenção manual); `cryptodatadownload` ou qualquer fornecedor com histórico de renomes/removes de URL sem versionamento.

Motivação: Binance Vision é a fonte pública com URL estável, origem auditável (bolsa tier-1), e escala natural de "um ZIP por mês" — encaixa perfeitamente com uma janela de 180 dias.

### 2. Recorte inicial (primeira rodada de validação real)

**Este é o primeiro recorte, não uma limitação do sistema.** O sistema é multi-asset (§2-bis). A redução para um único par nesta rodada é para minimizar superfície de variáveis ao validar o ramo "dado real" pela primeira vez.

- **Ativo:** `BTCUSDT` (spot). Mesmo par do sintético seminal — permite comparação lado a lado na mesma CLI.
- **Timeframe:** `1h`. Mesmo timeframe do sintético seminal. 1h é o mais natural para o primeiro contato real: volume por barra é alto o suficiente para mitigar ruído de microestrutura e a série é pequena o suficiente para inspeção no olho.
- **Janela:** **180 dias civis consecutivos terminando em 2025-12-31 23:00 UTC** (inclusivo). Intervalo exato: **2025-07-05 00:00 UTC → 2025-12-31 23:00 UTC**. Total nominal: `180 × 24 = 4.320` barras.
  - Motivação da data final: 2025-12-31 é o último instante possível dentro de ano civil fechado anterior à data atual (2026-04-16), evita reprocessar dados que ainda possam sofrer reclassificação, e casa com o particionamento mensal da Binance Vision (6 meses fechados: 2025-07, …, 2025-12).
  - 180 dias é o ponto médio proposto: pequeno o suficiente para ser auditável no olho, grande o suficiente para cobrir mais de um regime (cripto troca de regime em escala de semanas).
- **Timezone canônico:** **UTC**. Todos os timestamps do Parquet final têm `tzinfo=UTC`. Timestamps da Binance vêm em ms desde epoch; conversão `pd.to_datetime(..., unit="ms", utc=True)` fixa unidade e timezone.

### 2-bis. Suporte estrutural a múltiplos ativos — requisito de primeira classe

A ADR fixa, como invariante do repositório (não apenas "boa prática"):

1. **Nenhum hardcode de símbolo em código compartilhado.** Nenhum `if symbol == "BTCUSDT"`, nenhum default implícito para `BTC*` em `src/alpha_forge/**`. O único lugar onde um símbolo específico aparece é:
   - Em scripts de bootstrap/ingestão, como parâmetro de linha de comando.
   - Em entradas concretas do manifesto `data/datasets.yaml`.
   - Em testes que referenciam um dataset-id específico já registrado.
   - Em docs (`system/*.md`, `STATE.md`) descrevendo recortes já carregados.
   CLI e API pública recebem `dataset_id` ou `symbol`; defaults do demo são configuração da CLI, não do domínio.
2. **Manifesto preparado para N entradas coexistentes.** `data/datasets.yaml` já tem uma chave `datasets: [...]` que é lista. O loader já faz lookup por `dataset_id` (`find_manifest_entry`). Esta ADR reafirma: qualquer script de ingestão faz **upsert não destrutivo** (preserva as outras entradas), e qualquer script que aceita múltiplos símbolos em paralelo grava uma entrada por `(symbol, timeframe, janela)`.
3. **Pathing derivado de `symbol` e `timeframe`.** O helper `processed_dataset_path(symbol, timeframe, dataset_id)` (em `io/paths.py`) já é a API oficial. Nenhum código novo monta path de Parquet por concatenação ad-hoc.
4. **Script de ingestão da Binance Vision (§6) aceita `--symbol` e `--interval` arbitrários desde o dia 1.** Rodar para `ETHUSDT` ou `SOLUSDT` deve ser questão de trocar o valor da flag, não de editar o script. Adicionalmente, o script aceita **`--symbol` repetido** (ou `--symbols BTCUSDT,ETHUSDT,SOLUSDT`) para ingerir um lote em um único run — cada símbolo gera uma entrada independente no manifesto com seu próprio `dataset_id`. Implementação em lote é obrigação, não follow-up.
5. **Contratos do engine permanecem por-dataset.** `run_backtest` aceita um `prices: DataFrame` e um `dataset_id` — não existe "backtest multi-asset" nesta ADR. Comparação entre ativos acontece fora do engine, chamando `run_backtest` por ativo e comparando resultados. Portfolio-level / netting permanecem `deferred` (ADR-0001, ADR-0004).

**Testes que protegem multi-asset desde já:**
- Teste unitário em `test_paths.py` (criar se não existir): `processed_dataset_path("ETHUSDT", "1h", "foo")` gera path correto; `processed_dataset_path("SOLUSDT", "4h", "bar")` também. Nenhum BTC embutido.
- Teste unitário em `test_data_loader.py` (estender): popular manifesto temporário com **dois datasets distintos** (símbolos diferentes), carregar os dois por `dataset_id`, ver que não há colisão.

### 2-ter. Próximo lote planejado (sinalização, não compromisso desta ADR)

Depois que esta ADR estiver entregue e as frentes intermediárias (ADR-0010 property-based de custo; ADR-0011 segunda estratégia — Donchian breakout) rodarem, o próximo lote de datasets reais é:

- `BTCUSDT` 1h — já incluído nesta ADR.
- `ETHUSDT` 1h — mesma janela, mesma política de gaps.
- `SOLUSDT` 1h — mesma janela, mesma política de gaps.

Esse lote vira **ADR própria** quando chegar a hora (provável ADR-0012). A listagem aqui serve apenas para:
- Justificar que a infra multi-asset desta ADR não é over-engineering — é pré-requisito imediato.
- Tornar explícito para o leitor futuro que o projeto **não** é BTC-only nem mentalmente nem estruturalmente.

Nenhum código, manifesto ou teste desta ADR-0009 depende do lote ETH/SOL estar pronto. Se o projeto pivotar e outros pares fizerem mais sentido (BNB, XRP, algum par alt-USDT), o lote muda sem custo: nada depende estruturalmente de ETH ou SOL.

### 3. Convenção de `dataset_id` para dados reais

Slug estável (ADR-0005 §1) seguindo o padrão:

```
<symbol_lower>_<timeframe>_<start_yyyymmdd>_<end_yyyymmdd>_<source_slug>
```

Para este primeiro dataset:

```
btcusdt_1h_20250705_20251231_binance_spot
```

A extensão do arquivo Parquet é o mesmo slug: `data/processed/BTCUSDT/1h/btcusdt_1h_20250705_20251231_binance_spot.parquet`. `symbol` na path preserva a convenção do diretório (maiúsculas), mas `dataset_id` é lowercase para consistência com slugs.

**Regra de imutabilidade (reafirma ADR-0005 §3):** se o mesmo recorte precisar ser rebaixado (correção de bug de transformação, por exemplo), o novo dataset recebe `dataset_id` diferente — o sufixo ganha um discriminador (ex.: `..._binance_spot_v2`). Nunca reescrever o Parquet antigo.

### 4. Política de gaps reais — aceitar, mas **declarar um a um**

A opção (b) discutida com o usuário. Reafirma ADR-0005 §4 com uma regra concreta de preenchimento:

- O script de download detecta **automaticamente** qualquer salto de timestamp maior que `1h` entre barras consecutivas dentro da janela pedida.
- Cada gap detectado vira uma entrada em `declared_gaps` do manifesto, com:
  - `start` — timestamp da primeira barra faltante (inclusivo).
  - `end` — timestamp da última barra faltante (inclusivo).
  - `reason` — **precisa ser preenchida manualmente antes do commit**. Não aceitar `""` nem `"unknown"`. Valores aceitáveis são factuais: `"exchange maintenance"`, `"binance halt"`, `"missing from vendor dump"`. Sem razão factual → bloqueia commit do dataset.
- O script **nunca interpola**, **nunca forward-fills**, **nunca inventa barras**. Parquet contém exatamente as barras que a Binance publicou.
- Se o dataset final tiver **zero gaps**, `declared_gaps: []` — coerente com ADR-0005.

**Teto tolerado nesta ADR:** até **3 gaps** ou **48 horas faltantes cumulativas** (o que for atingido primeiro). Ultrapassou → a janela é **rejeitada** e escolhemos outra. Um dataset que declarou 30 gaps é um dataset impróprio como "primeiro contato com o real"; nesse caso o valor está no próximo dataset, não no esforço de declarar 30 razões.

### 5. Critério de aceitação do dataset no manifesto

Antes de commit do `data/datasets.yaml` com a entrada nova:

1. **Integridade do Parquet:** arquivo legível por `pd.read_parquet(engine="pyarrow")` sem warning; colunas exatamente `open, high, low, close, volume` (`open_time` vira o index, nome `timestamp`); `DatetimeIndex` UTC-aware; sem `NaN` nas 5 colunas.
2. **Invariantes de barra (ADR-0005 via `OHLCVBar`):** para toda barra, `high ≥ max(open, close)`, `low ≤ min(open, close)`, `high ≥ low`, `volume ≥ 0`, `open/high/low/close > 0`.
3. **Manifesto consistente com o arquivo:** `sha256` calculado sobre o Parquet bate; `row_count` bate com `len(df)`; `start_ts` e `end_ts` batem com `df.index[0]`/`df.index[-1]`; `declared_gaps` cobrem **todo** salto > 1h e só eles.
4. **Loader aceita o dataset sem exceção:** `load_dataset("btcusdt_1h_20250705_20251231_binance_spot")` retorna DataFrame sem `DatasetIntegrityError`. Isso é o critério final — se o loader recusar, o dataset não entra no manifesto.
5. **Teto de gaps respeitado:** `len(declared_gaps) ≤ 3` e soma total das durações ≤ 48h.

O dataset sintético seminal **permanece** no manifesto. Este não substitui aquele — coexistem. A CLI continua rodando sobre `--dataset-id synthetic_btcusdt_1h_seed42` por default (mantém reproducibilidade do demo sem exigir rede); o novo dataset é acionado via `--dataset-id btcusdt_1h_20250705_20251231_binance_spot`.

### 6. Script de ingestão

Novo arquivo: `scripts/ingest_binance_vision.py`. Parametrizado por `--symbol` (repetível ou em lista separada por vírgula), `--interval`, `--start`, `--end`, `--source-slug` (para o `dataset_id`). **Uso manual sob demanda**, não parte da CI. O script, para **cada símbolo pedido**:

1. Monta a lista de ZIPs mensais necessários para cobrir a janela pedida.
2. Baixa cada ZIP para `data/raw/binance_vision/<symbol>/<interval>/` (cacheado — se o arquivo já existe com sha256 esperado, pula o download). `data/raw/` já está no `.gitignore`.
3. Lê cada CSV, concatena em ordem, filtra para a janela exata (descarta barras antes de `start` e depois de `end`).
4. Converte `open_time` (ms UTC) para `DatetimeIndex` tz-aware; mantém colunas OHLCV; descarta as demais (`quote_volume`, `trades`, `taker_buy_*`, `ignore` não entram no Parquet nesta fase — ADR futura pode revisitar se uma estratégia precisar).
5. Detecta gaps > `interval`; emite relatório para stdout listando cada gap com start/end/duração; **exige razão factual por gap** via flag `--gap-reason "SYMBOL:start_iso=reason;..."` (prefixada por símbolo para permitir runs em lote). Sem razão → erro e o dataset do símbolo em questão **não é gravado**.
6. Valida invariantes de `OHLCVBar` via passagem pelo pydantic antes de escrever o Parquet (sample ou completo).
7. Escreve o Parquet com `snappy` em `data/processed/<SYMBOL>/<interval>/<dataset_id>.parquet` via `processed_dataset_path(...)`. **Nenhum path hardcoded**.
8. Calcula sha256, monta `DatasetManifest`, faz **upsert não destrutivo** em `data/datasets.yaml` (chave é `dataset_id`) — preserva demais entradas, inclusive as de outros símbolos processados no mesmo run.
9. Imprime sumário final **por símbolo**: `dataset_id`, bytes Parquet, `row_count`, janela efetiva, número de gaps declarados, sha256.
10. Se algum símbolo no lote falhar (gap sem razão, janela rejeitada pelo teto, invariante de barra violada), esse símbolo é **pulado com erro explícito** e o script continua com os demais. Exit code ≠ 0 se **qualquer** símbolo falhou — assim a CI/usuário percebe. Símbolos que passaram ficam gravados.

Idempotente: rerun produz o mesmo sha256 por símbolo se a Binance não tiver alterado os ZIPs mensais subjacentes (não deveria — dumps mensais fechados são arquivos históricos estáveis).

**Run canônico desta ADR** (um único símbolo, primeira rodada):

```
python scripts/ingest_binance_vision.py \
    --symbol BTCUSDT \
    --interval 1h \
    --start 2025-07-05 \
    --end 2025-12-31 \
    --source-slug binance_spot \
    --gap-reason "BTCUSDT:2025-08-14T12:00:00Z=binance scheduled maintenance"   # exemplo; razões reais preenchidas após primeiro run listar os gaps
```

**Run em lote (quando o próximo ADR habilitar):**

```
python scripts/ingest_binance_vision.py \
    --symbols BTCUSDT,ETHUSDT,SOLUSDT \
    --interval 1h \
    --start 2025-07-05 \
    --end 2025-12-31 \
    --source-slug binance_spot \
    --gap-reason "..."
```

A segunda forma já funciona nesta ADR; só não é exercitada aqui por disciplina.

## Consequences

- **Positive:** primeiro dataset real disponível para qualquer backtest; Binance Vision é fonte estável e não exige credenciais; `declared_gaps` finalmente encontra casos reais (permite testar o ramo "gap declarado → loader aceita"); CLI ganha um segundo `dataset-id` útil sem nenhuma mudança no engine; sintético permanece como default de demo (reproducibilidade offline); invariante "nenhum hardcode de símbolo" passa a ter testes que o protegem, o que era implícito e agora é explícito.
- **Negative:** introduz dependência de rede no script de ingestão (aceita, não é CI); ritual manual de "declarar razão de cada gap" custa tempo no primeiro run; se a Binance algum dia reorganizar as URLs do Vision, o script quebra (aceita: é utilitário local, não infra crítica); ~4.320 barras OHLCV em 1h cabem em < 500 kB Parquet — custo de storage desprezível, custo de download trivial; suportar lote multi-símbolo já no primeiro script gasta alguns minutos a mais de design, mas evita retrabalho imediato no próximo ADR.
- **Neutral:** escolha de janela 2025-07-05 → 2025-12-31 é arbitrária dentro da família "180 dias de ano civil fechado"; outra janela da mesma família serviria igualmente, mas qualquer mudança posterior exige novo `dataset_id` (imutabilidade); sinalização do próximo lote (BTC+ETH+SOL) é orientação, não compromisso — qualquer pivot fica livre.

## Alternatives considered

- **`ccxt` agora, puxando de qualquer exchange suportada** — rejeitado: ADR-0001 já marcou `deferred`; traz dependência + API instável + questão de credenciais por exchange; ganho marginal enquanto o laboratório tem 1 dataset.
- **CSV baixado à mão via browser** — rejeitado pelo usuário e pelo agente: não é reproduzível sem intervenção humana; qualquer colaborador precisaria repetir o ritual; sha256 protege conteúdo, mas não protege a origem.
- **`cryptodatadownload` ou vendor análogo** — rejeitado: URLs menos estáveis; origem a um passo de distância da bolsa (re-empacotamento); Binance Vision é "oficial direto da fonte".
- **Janela de 90 dias** — rejeitado pelo usuário: 2.160 barras é denso para inspeção mas pobre de regime; 180 dias compra regime sem abrir a conta de complexidade.
- **Janela de 1 ano civil (365 dias, ~8.760 barras)** — rejeitado pelo usuário: auditável ainda, mas "primeiro contato" pede menos superfície; ano inteiro vira ADR futura.
- **Aceitar gaps sem declarar razão (opção (a) com bar alto)** — rejeitado: viola ADR-0005 §4 no espírito; "unknown" como razão é a porta de entrada para dataset poluído.
- **Rejeitar qualquer janela com gap (opção (a) rígida)** — rejeitado: Binance teve ≥ 1 janela de manutenção documentada no intervalo proposto; rejeitar seria fugir do problema que a infra de gaps existe justamente para resolver.
- **ETH/USDT ou outro par** — rejeitado: BTC é a base natural de comparação com o sintético; outros pares entram em ADR futura quando houver razão (diversificação, correlação entre ativos).
- **Timeframe 1d ou 4h** — rejeitado: 1d dá ~180 barras (muito pouco); 4h dá ~1.080 (razoável, mas perde granularidade útil para testes de causalidade e custos); 1h casa com o sintético existente.
- **Guardar colunas extras (`quote_volume`, `trades`, `taker_buy_*`)** — rejeitado nesta fase: nenhuma estratégia atual consome essas colunas; incluí-las sem razão infla o Parquet e cria expectativa. Revisitar em ADR futura se surgir demanda (ex.: estratégia que use volume de takers).
- **Binance Vision direto no script principal do engine** — rejeitado: engine não fala rede nem fala ZIP; responsabilidade do script de ingestão. Separação coerente com ADR-0005 §5 ("`data/` é o único autorizado a ler `datasets.yaml`").
- **Script de ingestão single-symbol agora, multi-symbol em ADR futura** — rejeitado: o retrabalho é pequeno (dois loops em vez de um) e o risco de cristalizar hardcode de BTC no script é alto. Multi-símbolo do dia 1, exercitar em lote só depois.
- **Ingerir BTC + ETH + SOL já nesta ADR** — rejeitado: essa é a constraint de disciplina operacional ("pequeno de propósito"). Primeira rodada valida o ramo real com a **menor superfície possível** (um símbolo); o próximo lote é ADR própria, com orçamento próprio de atenção para declarar gaps de três pares.

## Follow-ups

- Implementar `scripts/ingest_binance_vision.py` conforme §6, **multi-symbol desde o dia 1** (aceita `--symbol` repetível ou `--symbols` CSV). Parar na primeira execução se algum gap ficar sem razão factual.
- Executar o script uma vez com `--symbol BTCUSDT --interval 1h --start 2025-07-05 --end 2025-12-31 --source-slug binance_spot`. Registrar em follow-up do STATE o relatório de gaps detectados e a razão factual atribuída a cada um.
- Escrever `tests/unit/test_ingest_binance_vision.py` cobrindo funções puras do script, **sem rede**: montagem de URLs mensais **para símbolo genérico** (testar ao menos dois símbolos distintos — nenhum BTC hardcoded no teste da função); filtro para janela exata; detecção de gap entre barras consecutivas; roteamento multi-símbolo em lote (um run com dois símbolos produz duas entradas de manifesto independentes, nenhuma colisão).
- Escrever `tests/unit/test_paths_multi_asset.py` (criar) — `processed_dataset_path("ETHUSDT", "1h", "x")` e `processed_dataset_path("SOLUSDT", "4h", "y")` produzem paths distintos e corretos; nenhum valor BTC embutido.
- Estender `tests/unit/test_data_loader.py` com caso multi-asset: manifesto temporário com dois datasets de símbolos diferentes, `load_dataset` por `dataset_id` funciona para cada um independentemente, não há colisão de path.
- Escrever teste de integração `tests/integration/test_first_real_dataset.py` que **depende** do dataset real estar presente (skip se ausente), e exercita: `load_dataset(...)` retorna DataFrame coerente; `run_backtest` com `MovingAverageCrossoverStrategy(20, 50)` roda sobre ele sem exceção; métricas finitas; posição aberta ao fim é permitida.
- Atualizar `system/domain.md` com o novo dataset (entrada análoga à do sintético seminal) e reforçar a linha "multi-asset por design"; `system/api.md` com o novo script (sintaxe multi-símbolo explícita); `system/flows.md` com o fluxo "ingestão de dataset real — Binance Vision".
- Atualizar `data/datasets.yaml` com a nova entrada (o próprio script faz o upsert não destrutivo).
- Atualizar `STATE.md` no fim: mover para "last delivered" e listar a próxima frente (ADR-0010 — property-based de custo — já no forno pela decisão do usuário); registrar que multi-asset está estruturalmente cravado mesmo com um único par carregado.
- **Não** tocar no engine, nos schemas, no `CostModel`, nas métricas, nem nas estratégias. Esta ADR não muda código compartilhado — só adiciona um script utilitário (multi-símbolo), um dataset concreto (um símbolo) e seus testes.
- **Auditoria anti-hardcode** antes do commit final da implementação: `rg -n "BTC(USDT)?" src/` não deve retornar nenhum match fora de comentários explicativos. Qualquer ocorrência remanescente em `src/` é bloqueador.
