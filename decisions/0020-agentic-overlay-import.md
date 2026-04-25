# 0020 — Import seletivo da camada agentic do fork `feature/agentic-pilot-donchian`

**Status:** Accepted
**Date:** 2026-04-17
**Deciders:** autônomo (agente), autorizado pelo usuário em sessão 2026-04-17

## Context

O objetivo declarado do usuário é preparar o projeto para **testar centenas de estratégias em batch**, com pesquisa/implementação/validação/auditoria automatizadas ("quero ter tudo pronto pra quando começar a testar estratégias voce saiam testando centenas 1 por 1 e ranqueando"). O `src/alpha_forge/` está maduro como núcleo de domínio: ADRs 0001–0019 fecham backtest + validation + CLI + persistência + custos (fee + slip + spread). Falta **infra de pesquisa automatizada** — quem decide o que pesquisar, quem traduz hipótese em código, quem valida, quem audita.

O fork `https://github.com/leonardoolivera/teste/tree/feature/agentic-pilot-donchian` tem exatamente essa camada pronta: 5 subagentes (`lead-orchestrator`, `strategy-researcher`, `strategy-implementer`, `backtest-validator`, `risk-auditor`) + 3 hooks determinísticos (`block_live_trading.py`, `session_reminder.py`, `check_gates.py`) + protocolo de 6 artefatos por hipótese (SPEC/IMPLEMENTATION/VALIDATION/BACKTEST/AUDIT/CHECKLIST) + `scripts/validate_artifacts.py` + CI agentic. Clonado em `teste-fork/` para inspeção.

Diff conceitual em 2026-04-17: nosso repo é **ADR-ahead** (0001–0019) vs fork (0001–0012). Rebase/merge não serve — a camada de domínio do fork é **anterior** à nossa. Por outro lado, o `src/alpha_forge/` do fork não tem: ADR-0012 (MA short side), ADR-0013 (Donchian short side), ADR-0014 (cost_stress), ADR-0015 (persistence), ADR-0016 (CLI validate), ADR-0017 (run metadata), ADR-0018 (CLI compare), ADR-0019 (spread). Portanto não queremos o `src/` do fork — queremos **só** a camada agentic, que é ortogonal ao domínio e não tocou `src/alpha_forge/` significativamente.

## Decision

Importar **seletivamente** a camada agentic do fork como **overlay puro**, sem tocar em nenhum contrato de `src/alpha_forge/`, `tests/`, `decisions/0001–0019`, ou `system/*`. Cria-se infra de orquestração paralela à implementação; hooks defensivos ativos (live trading bloqueado, secrets bloqueados, endpoints de produção bloqueados); protocolo por-hipótese **opt-in** (artefatos só ganham força quando uma hipótese está ativa, declarada por `SPEC.md` com front-matter `status: active`).

Itens importados:

1. `.claude/settings.json` — hooks + `permissions.deny` (comandos destrutivos, edição de secrets). Copiado integral.
2. `.claude/agents/{lead-orchestrator,strategy-researcher,strategy-implementer,backtest-validator,risk-auditor}.md` — 5 subagentes, modelos e ferramentas preservados; reading order ajustado para refletir nossas ADRs 0013–0019.
3. `.claude/hooks/block_live_trading.py` — copiado integral. Regras são estruturais (regex) e independem do estado do repo.
4. `.claude/hooks/session_reminder.py` — copiado com pequena adaptação de texto (cita ADR-0020 como origem da camada).
5. `.claude/hooks/check_gates.py` — **adaptado** para modo opt-in: retorna 0 silenciosamente se não há `SPEC.md` em `agentic/active/` OU se `SPEC.md` existe mas contém `status: template`. Só exige os 6 artefatos quando um piloto está marcado `status: active`. Preserva a utilidade original (lembrete anti-esquecimento) sem quebrar a rotina de desenvolvimento de infra (como esta ADR).
6. `scripts/validate_artifacts.py` — **adaptado** ao mesmo modo opt-in do `check_gates.py`. Em repo sem piloto ativo, exit 0 com "nenhum piloto ativo — OK".
7. `agentic/templates/{SPEC,IMPLEMENTATION,VALIDATION,BACKTEST,AUDIT,CHECKLIST}.md` — templates de artefato (do fork, com os placeholders preservados). Copiados para novo diretório `agentic/templates/` para deixar claro que são modelos, não instâncias ativas. Um piloto começa copiando tudo para `agentic/active/<hypothesis_slug>/`.
8. `agentic/README.md` — adaptação do `README_AGENTIC_PILOT.md` do fork, atualizado para refletir nossa realidade (ADRs 0001–0019, não Donchian como piloto inicial; layout `agentic/templates/` + `agentic/active/`).

Itens **não** importados:

- ADRs 0001–0012 do fork — **nós já temos versões próprias** (e o fork não tem 0012 da forma que temos, que fixa short side; há divergência de conteúdo que seria mesclagem perigosa).
- `SPEC.md`/`IMPLEMENTATION.md`/`VALIDATION.md`/`BACKTEST.md`/`AUDIT.md`/`CHECKLIST.md` **na raiz** — fork tinha hipótese Donchian ativa; nós não temos hipótese ativa. Templates ficam em `agentic/templates/`, instâncias vão em `agentic/active/<slug>/` quando houver piloto.
- `src/alpha_forge/strategies/families/donchian/` do fork — já temos Donchian próprio (ADR-0011 + ADR-0013 com short side), que é superset do fork. Divergência de conteúdo rejeitada.
- `tests/` do fork — são casados com `src/` do fork; nosso `tests/` já cobre nosso superset.
- `scripts/validate_pilot.py` do fork — duplica funcionalidade já coberta por `alpha-forge validate` (ADR-0016) + `cost_stress` (ADR-0014) + `walk_forward` (ADR-0003). Não há ganho estrutural; seria dívida técnica por sobreposição.
- `configs/{strategies,experiments,regimes,risk}` — subdiretórios vazios no fork, sem consumidor hoje. Adiado para ADR-0022 (se/quando abrir configs declarativas como infraestrutura real).
- `.github/workflows/agentic.yml` — depende de `validate_artifacts.py` passar em CI e do repo estar configurado pra GitHub Actions. Adiado para ADR-0021 (CI agentic) como fatia independente.
- `ASSUMPTIONS.md` raiz — fork tem; nós não temos; suposições tomadas ficam dentro de ADRs próprias (cada ADR já tem §Alternatives/§Consequences). Adicionar um único `ASSUMPTIONS.md` central seria dispersar fonte de verdade.

## Consequences

- **Positive:**
  - Agente tem **5 personas especializadas** disponíveis (`lead-orchestrator` + 4 especialistas) com contratos explícitos de reading order, protocolo de trabalho, regras duras e formato de saída. Pré-requisito pra escalar pesquisa de estratégias — um orquestrador pode rodar N hipóteses em paralelo delegando aos 4 especialistas.
  - **Defesa em profundidade contra live trading**: 3 camadas (hook PreToolUse, `permissions.deny` do settings.json, políticas de CLAUDE.md). Mesmo se uma falhar, as outras cobrem.
  - **Rastro pós-compactação**: `session_reminder.py` reinjeta regras duras em `SessionStart`, sobrevive compactação de contexto.
  - **Protocolo por-hipótese descrito**: SPEC→IMPLEMENTATION→VALIDATION→BACKTEST→AUDIT é um fluxo formal reprodutível, não invenção por sessão.
  - **Sem poluir raiz**: artefatos de hipótese vivem em `agentic/active/<slug>/`, não na raiz. Raiz fica limpa até alguém abrir um piloto.
  - **Templates em `agentic/templates/`**: quem abre piloto copia o template, adapta, e coloca em `agentic/active/<slug>/`. Zero ambiguidade entre "modelo" e "hipótese ativa".
- **Negative:**
  - `.claude/` é infra específica de Claude Code; não ajuda usuários de outros agentes ou CI fora de Claude. Aceito — fork já assumiu esse custo, não reabrimos a decisão.
  - 5 subagentes + 3 hooks = 9 arquivos novos de configuração. Para quem nunca viu a camada agentic, é curva de aprendizado. Mitigado pelo `agentic/README.md` adaptado.
  - Hook `check_gates.py` adaptado tem lógica de "opt-in" que é mais sutil que o do fork. Risco: dev esquecer de marcar `status: active` e ficar sem gate. Aceito — é melhor opt-in silencioso do que falso-positivo ruidoso em cada sessão de infra.
  - Reading orders dos subagentes mencionam ADRs 0013–0019 — se uma ADR for superseded no futuro, subagentes precisam ser atualizados também. Aceito — o custo é 5 arquivos de texto.
- **Neutral:**
  - `src/alpha_forge/` não é tocado nesta ADR. Suíte de testes continua exatamente como `289 passed, 1 skipped` de E.9.
  - Import preserva a estrutura original do fork (mesmos nomes de arquivo, mesmos roles) — consumidores familiarizados com o fork reconhecem imediatamente.

## Alternatives considered

- **Import integral do fork (incluindo `src/`)** — rejeitado. Fork é ADR-atrás; mesclar seu `src/` perderia ADRs 0012–0019. Não é merge mecânico, é conflito semântico.
- **Rebase do fork sobre nossa main** — rejeitado. Mesmo motivo: ADRs divergentes no mesmo namespace (0011 e 0012 têm conteúdos diferentes nas duas linhas). Merge três-vias seria um pesadelo.
- **Não importar nada, escrever camada agentic do zero** — rejeitado. Fork tem 5 subagentes bem escritos + 3 hooks testados; reinventar é desperdício. O custo de adaptar é uma fração do custo de desenhar.
- **Import só dos subagentes, sem hooks** — rejeitado. Hooks são a defesa em profundidade anti-live-trading; são o guardrail estrutural que o fork pensou pra esta camada. Sem hooks, os subagentes perdem metade do valor.
- **Import só dos hooks, sem subagentes** — rejeitado. O protocolo SPEC/IMPL/VAL/BT/AUDIT **é** o trabalho do orquestrador + especialistas; importar só os hooks deixaria um protocolo sem executores.
- **Manter os artefatos de protocolo na raiz (como no fork)** — rejeitado. Fork tinha hipótese Donchian ativa; nós não temos. Poluir raiz com 6 arquivos de template que ninguém consulta cria confusão entre "modelo" e "hipótese ativa". `agentic/templates/` + `agentic/active/` separa as duas noções estruturalmente.
- **Copiar `check_gates.py` idêntico, sem o modo opt-in** — rejeitado. Forçaria criar SPEC/IMPL/VAL/BT/AUDIT na raiz logo agora, com placeholders, só pro hook calar. Dívida técnica imediata por zero ganho.
- **Importar `scripts/validate_pilot.py`** — rejeitado. Sobrepõe `alpha-forge validate` + `cost_stress` + `walk_forward`. Não há ganho estrutural.
- **Importar `.github/workflows/agentic.yml` nesta ADR** — rejeitado. Depende de `validate_artifacts` estável e de configuração de GH Actions que hoje não temos. Adiado para ADR-0021 como fatia independente.
- **Importar `configs/` vazio** — rejeitado. Diretórios vazios sem consumidor criam confusão ("isto é pra ser usado como?"). Adiado para ADR-0022 quando houver consumidor real (provável: ranking multi-estratégia lê configs/strategies para grid).

## Follow-ups

Cada item vira pendência em `STATE.md`.

- **ADR-0021 (CI agentic)**: importar `.github/workflows/agentic.yml` depois que `validate_artifacts.py` estiver estável em ≥1 piloto real. Fatia independente.
- **ADR-0022 (configs declarativas)**: abrir `configs/{strategies,experiments,regimes,risk}` quando ranking multi-estratégia (outra ADR candidata) precisar de grid paramétrico.
- **ADR-0023 (primeiro piloto agentic)**: quando o usuário quiser exercitar o protocolo completo ponta-a-ponta, escolher uma hipótese (ex: retest de Donchian 20/10 long-only em BTC/ETH/SOL com walk-forward full + MC + cost_stress + spread), abrir `agentic/active/<slug>/` copiando templates, e rodar `lead-orchestrator`. ADR documenta a escolha da hipótese e o critério de promoção do piloto.
- **Atualizar subagentes quando ADR nova for aceita**: reading orders de `lead-orchestrator`, `strategy-researcher`, `strategy-implementer`, `backtest-validator`, `risk-auditor` mencionam ADRs específicas. Ao aceitar ADR nova (ex: ranking), atualizar as listas.
