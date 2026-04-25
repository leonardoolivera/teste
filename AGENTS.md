# AGENTS.md

**You are an AI agent working on this project. Read this file first. Every time.**

This file defines the protocol you must follow. It is not documentation about the project — it is instructions for you.

---

## 1. Reading order (mandatory, in this sequence)

Before you write or edit any code, read these files in order:

1. **`AGENTS.md`** — this file (you are here)
2. **`STATE.md`** — what is done, what is pending, what the next step is. This is the only document that reflects *now*.
3. **`vision/01-product.md`** — what this project is supposed to be and for whom
4. **`vision/02-scope.md`** — what is in, what is out
5. **`vision/03-architecture.md`** — stack and technical decisions
6. **`system/domain.md`** — only if the project has code already; describes entities and business rules that currently exist
7. **`decisions/`** — skim index, read ADRs relevant to your task

Do not skip. Do not reorder. Do not assume.

---

## 2. The three-layer model (non-negotiable)

This project separates documentation into three layers. Each answers a different question:

| Layer | Folder | Question it answers | How often it changes |
|---|---|---|---|
| **Target** | `vision/` | What do we want to be? | Rarely (per quarter) |
| **System** | `system/` | What currently exists? | When code changes |
| **State** | `STATE.md` | Where are we right now? | Every session |

**You must respect the boundary.** Never describe existing code in `vision/`. Never describe aspirations in `system/`. Never leave intermediate work out of `STATE.md`.

If you find a document violating its layer, fix it as part of your current task.

---

## 3. The interview protocol (critical)

If the user starts this project from an empty or partial state, **do not start coding**. Your first job is to make sure the three layers are filled in enough to work.

**Check in this order:**

1. Does `vision/01-product.md` answer: *what is this, for whom, what problem does it solve, what is success?* → If not, interview the user.
2. Does `vision/02-scope.md` answer: *what modules exist, what is explicitly out of scope?* → If not, interview.
3. Does `vision/03-architecture.md` answer: *language, framework, database, deployment target, non-functional constraints?* → If not, interview.
4. Is there a first ADR in `decisions/` recording the key technical bets? → If not, propose and write one after the interview.

**How to interview** (rules):

- Ask **one question at a time**. Wait for the answer before the next.
- Ask **concrete, scoped questions**, not open-ended ones. Bad: "how do you want the API?". Good: "REST with JSON or GraphQL?".
- Offer **2–4 options** with a short tradeoff for each when the user seems unsure. The user picks; you don't decide for them.
- After each answer, **write it into the corresponding vision/ file immediately** — do not batch. If the user changes their mind, edit the file.
- When all vision/ files are filled and the user confirms, **propose a first ADR** summarizing the decisions. Only then start scaffolding.
- If the user says "you decide", make a choice, state it explicitly, and write it down as a reversible default. Flag it so they can override later.

**Signs the interview is not done:**
- `vision/` files still contain `{{PLACEHOLDER}}` markers
- You are about to write code but cannot name the first three entities of the domain
- The user hasn't explicitly confirmed the stack

---

## 4. Writing rules

**Before any code change:**
- Confirm the task aligns with `STATE.md`'s next step, or update `STATE.md` to reflect the new direction
- If it touches architecture, write an ADR in `decisions/` first

**After any code change:**
- Update `system/` files that describe the area you touched (domain, api, flows)
- Update `STATE.md`: mark what's done, list what remains, set the next step
- Never leave stale documentation. Stale docs are worse than no docs.

**Commit discipline:**
- One commit per logical unit
- Commit message answers *why*, not *what*
- Never commit without updating `STATE.md` in the same commit when work progresses

---

## 5. When in doubt

- **Doubt about scope** → read `vision/02-scope.md`. If ambiguous, ask the user.
- **Doubt about a technical choice** → read `decisions/` index. If no ADR covers it, propose one.
- **Doubt about what "done" means** → read `STATE.md`'s acceptance criteria for the current step.
- **Doubt about whether to ask or decide** → ask. The cost of interrupting the user is small. The cost of building the wrong thing is large.

---

## 6. Hard rules

- **Do not invent information.** If `vision/` doesn't answer a question, ask the user — do not guess.
- **Do not edit `decisions/` ADRs.** They are immutable. Supersede them with a new ADR that references the old one.
- **Do not ship code without tests** unless the user explicitly waives it for this task.
- **Do not skip the reading order** because the task seems small. Small tasks corrupt state when the agent skipped context.

---

## 7. For Claude Code specifically

`CLAUDE.md` at the repo root points here. This file is the source of truth. Keep them in sync.

---

## 8. Export contract — handoff to BotBinance runtime

Alpha Forge is a **research lab**. It does not execute. When a strategy is approved here, it is handed off to **BotBinance** (sibling project at `c:\Users\leo-a\Downloads\Nova pasta (3)\botbinance\`) for paper/live execution.

The handoff is **code-free**: BotBinance never imports Alpha Forge Python. The only contract is a JSON manifest.

### Manifest location
`exports/approved/<strategy_name>_<YYYYMMDD>.json`

### Approval gate (all required before exporting)
1. **Walk-forward validated** — out-of-sample Sharpe ≥ 1.0, MDD ≤ 20%, PnL > 0 on OOS.
2. **Lookahead guard passed** — `backtest/lookahead_guard.py` clean on every feature.
3. **Realistic cost** — fees + slippage ≥ 0.20% round-trip applied.
4. **Trade count** ≥ 30 on OOS.
5. **ADR written** in `decisions/` recording the approval and rationale.

### Manifest schema (v3+, canonical)

The canonical schema is `exports/approved/manifest.schema.json` (JSON Schema Draft 2020-12), introduced by **ADR-0031**. Every manifest emitted from this lab must validate against it via `alpha_forge.exports.validate_manifest` before being written. v1 and v2 manifests (ADR-0028, ADR-0029) are legacy and explicitly out of scope.

Required top-level fields in v3:
- `manifest_version` (`"v3"` or higher)
- `strategy_name`, `alpha_forge_commit` (40-char sha), `approved_at` (ISO 8601 UTC)
- `approval_adr` (path starting with `decisions/`)
- `engine` (`family` + `params`)
- `approved_combos` (array; each combo has `symbol`, `timeframe`, `validation_window`, `window_tag`, and all OOS stats — no defaults)
- `validation` (with `cost_stress_ratio_min ≥ 0.95`, `seed_monte_carlo`, etc.)
- `execution_hints` (with `position_sizing: "fixed_notional_per_trade"` fixed and `notional_per_trade_quote_ccy`)
- **`runtime_contract: "faithful"`** (ADR-0030; only accepted value in v3)
- **`runtime_invariants`** object with five fixed literals (ADR-0030):
  - `entry_fill: "market_at_open_next_bar"`
  - `exit_fill: "market_at_open_next_bar"`
  - `sizing: "fixed_notional_literal"`
  - `stop_loss: "disabled"`
  - `signal_arbitration: "exit_wins_on_tie"`
- `expansion_policy` (`rule` + `excluded_combos`)

Optional in v3: `supersedes`, `prior_approval_adr`, `disallow_sizing_modes` (enum `["snowball", "kelly_like", "martingale"]`), `disallow_sizing_reason`.

`additionalProperties: false` at the top level — unknown fields are rejected.

### Runtime-faithful contract (ADR-0030)

Any runtime consuming an approved manifest (BotBinance or otherwise) must honor four invariants; reinterpreting any of them invalidates the approval:
1. **Entry fill:** `market @ open[t+1]` after ENTER signal at `t`. Never limit at trigger, never extra delay.
2. **Exit fill:** `market @ open[t+1]` after EXIT signal at `t`. Never stop-loss, never take-profit, never limit.
3. **Sizing:** literal `execution_hints.notional_per_trade_quote_ccy`. Risk-%, kelly, volatility-based overrides are forbidden.
4. **Stop loss:** `disabled`. Exits are 100% governed by `exit_rule`.

ADR-0030 emerged from the 2026-04-18 handoff via `C:\Users\leo-a\agents_bridge\` where four distinct reinterpretations (double-strip causal, limit-at-trigger survivor bias, 2%-risk sizing, stop-loss active) inflated Sharpe +6 to +8 and PnL +990% until corrected.

### Do NOT export
- Scaffolding / mock strategies (`dummy`, placeholder families).
- In-sample-only results.
- Strategies without an ADR.
- Strategies the user has not explicitly approved for handoff.

### After exporting
- Notify the user that a new manifest is ready.
- BotBinance will re-run its composite snowball backtest locally before activating. Expect a "re-validation passed/failed" reply.
- If re-validation fails on BotBinance side, investigate cost/risk parameter divergence — do **not** loosen criteria here to force approval.

---

## 9. V2/RAIO methodology guideline (Padrões 53-63)

**Mandatory reading** for any agent working on strategy approval, manifest export, or methodology. These were consolidated through V2/RAIO Cycles 1-10 (ADRs 0212-0225). They supersede V1 single-window approval methodology.

### Core gate (AND-conjunto for any new strategy promotion to manifest)

1. **Janela contínua ≥18 meses** (Padrão 60). Janelas curtas ≤6 meses inflacionam Sharpe via temporal selection bias. Datasets concat já existem: `*_1h_20230705_20251231_*_concat30m` e `*_10m_20240705_20251231_*_concat18m`.
2. **Fees ≥10bps** em screening (Padrão 53). Default V2; 5bps inflaciona Sh em estratégias high-turnover.
3. **Sh ≥ 1.0 ∧ trades ≥ 30 ∧ MDD ≤ 10%** sobre janela contínua (gate ADR-0030 reformulado).
4. **Cross-asset OR mecanismo causal asset-specific explícito** (Padrão 62). Asset-specific edges legítimos mas raros (ex S12 SOL).
5. **Block bootstrap não-paramétrico OR PSR(0)>0.95** (Padrão 56 alternativa Padrão 54). DSR strict Bailey-LdP penaliza demais em crypto kurt~20.
6. **Sensitivity local não-colapso** (Padrão 52 method): vizinhança paramétrica deve manter Sh > 0.94.
7. **Portfolio integration positiva (PF024) em ≥2 regimes distintos**. Single-window PF024 PASS é falso positivo (Padrão 60 retroativo).
8. **Padrão 58 mitigation se trend-long**: BHDrawdownFilter ou regime detector obrigatório; sem isso, trend-long crypto é catastrófico em bear (-6 a -20% drawdown).
9. **Script audit Padrão 55**: todo script V2 passa boolean flags CLI explicit (`--long-only`/`--no-long-only`, etc). Defaults mudam entre versões.

### Padrões falsificados (NÃO repetir)

- **Padrão 50** (trend-following bear-avoidance ETH 2025-H1 cluster): GRAVEYARD coletivo. ADR-0214 promoveu, ADR-0225 confirmou refutação. Era selection bias temporal puro.
- **Padrão 52** (ma_crossover 18/60 long-only): GRAVEYARD após 7 ciclos. Sh=3.02 em 2024-H2 → Sh ≈ 0 em janela contínua 30m.
- **Padrão 57** (trend-long como hedge): retroativamente refutado por Padrão 60.

### Padrões reabertura

- **TF 10m permanently graveyarded** engine-only (Padrão 46 MR + Padrão 63 trend). Reabertura só com microestrutura (orderbook, sweep detection, market-making).
- **P52 reabertura**: só com mecanismo causal pré-declarado para regime detectável que sustente 18m+ contínuos.

### Operational protocols

- **Stack canonical V1 health (ADR-0222)**: 1/13 ROBUST sob Padrão 60 (S12 SOL); 9/13 FAIL; 2/13 catastróficos (S10/S11 paper-trade observation 14d ADR-0224).
- **Não exportar combos baseados em V1 single-window** sem re-validação Padrão 60.
- **Não retirar manifests aprovados** sem ADR explícito + paper-trade observation extended.

### Methodology files

- [`HYPOTHESIS_TREE.md`](HYPOTHESIS_TREE.md): árvore RAIO viva.
- [`NODE_LOG.md`](NODE_LOG.md): diário append-only de cada nó.
- [`SEARCH_STATE.md`](SEARCH_STATE.md): estado operacional + best_open_nodes.
- [`GRAVEYARD.md`](GRAVEYARD.md): hipóteses enterradas com causa de morte.
- [`ROADMAP_ESTRATEGIAS_V2_METODOLOGICO.md`](ROADMAP_ESTRATEGIAS_V2_METODOLOGICO.md): 180 hipóteses falsificáveis em 7 famílias.
- [`LIGHTNING_SEARCH_PROTOCOL.md`](LIGHTNING_SEARCH_PROTOCOL.md): protocolo RAIO completo.
