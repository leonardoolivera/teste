# 0063 — Política de sizing dual: fixed_notional + snowball em paralelo

**Status:** Accepted — substitui proibição absoluta de snowball de ADR-0028/0029
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0004 (fixed fractional), ADR-0028/0029 (proibição snowball v1), ADR-0030 (runtime faithful), ADR-0031 (schema v3), ADR-0060 (v3 ativo), ADR-0062 (CH PASS pendente promoção).

## Context

ADR-0028/0029 proibiu snowball com base em **um** teste real do BotBinance: ETH 2024-H1 long, snowball colapsou PnL +19% → +0.78% e subiu MDD 17% → 23%. Manifest v2 registra `disallow_sizing_modes: [snowball, kelly_like, martingale]` como absoluto.

Usuário pediu: a partir de agora, rodar séries em duplicata (fixed + snowball) e deixar o bot paper-tradar ambas em paralelo, decidindo o vencedor empiricamente.

Evidência pre-existente (1 teste, ETH long) é insuficiente pra proibir globalmente — pode ser específico a (a) ETH, (b) long, (c) 2024-H1, (d) Bollinger puro v1 sem filtro. Novas famílias (RSI, short) e novas composições (width 300) não foram testadas com snowball.

## Decisão

**Sizing é propriedade por-manifest, não política global.** Cada série valida os dois modos. Manifests aprovados declaram `sizing_mode` ∈ `{fixed_notional, snowball}`. Par de manifests (v3 fixed + v3b snowball) pode existir se ambos passarem gate.

### O que muda

1. **Engine**: passa a suportar snowball via `--sizing-mode` CLI. Fixed é default (preserva compatibilidade retroativa).
2. **Schema v3 manifest**: campo `sizing_mode` adicionado, substitui `position_sizing` fixo.
3. **ADR-0028/0029 `disallow_sizing_modes`**: reinterpretado de "proibição absoluta global" → "lista de modos que degradaram historicamente neste manifest específico (informativo)". Não bloqueia teste de snowball em outros manifests.
4. **Política de séries futuras**: toda série nova roda **duplicata** fixed + snowball. Summarizer compara combo-a-combo.
5. **Manifests existentes**: v2 (long) e v3 (short Bollinger) permanecem fixed. v4 (RSI short) promovido será par fixed+snowball se snowball passar gate.

### Snowball — definição precisa

Snowball = fixed fractional com `capital_corrente` dinâmico:
- `notional = capital_corrente × fracao × alavancagem`
- `capital_corrente = capital_inicial + sum(pnl_realizado)` após cada trade fechado
- Trades abertos **não** impactam capital_corrente (evita contabilidade double-counting).
- Drawdown em trade aberto reduz capital_corrente futuro **quando o trade fecha**, não durante.

Fixed notional (v2/v3 atual) = capital_corrente **sempre** igual a capital_inicial.

### Gate snowball (mesmo gate manifest)

Um manifest snowball é aprovado se:
- Passa os 5 gates canônicos (trades≥30, Sharpe≥1.0, MDD≤20, MC p5>9500, cost_r≥0.95) **com capital_corrente dinâmico**.
- **Adicional**: MDD snowball ≤ MDD fixed × 1.5 (snowball amplifica MDD em streaks perdedoras; gate protege contra "Sharpe alto via capitalização lucky").

### Integração com runtime faithful (ADR-0030)

Runtime contract `faithful` continua válido. `sizing` literal muda de `fixed_notional_literal` → `{fixed_notional_literal, snowball_from_realized_pnl}`. Bot recebe qual dos dois via campo `engine.params.sizing_mode` no manifest.

Ambos modos preservam os outros 4 invariantes (fills, stop, arbitration).

### Comparação fair: baseline fixed é primary

Pra cada série: fixed é o **baseline**. Snowball só é promovido se **supera** fixed em USD absoluto **e** passa gate próprio. Se snowball tem USD maior mas viola gate MDD, fica arquivado como "candidato promissor" sem promoção.

## Hipóteses explícitas

1. **H-assimetria direcional**: snowball falha em mean-rev long (evidência ADR-0029 ETH) mas pode passar em mean-rev short. Razão: short em chop tem streaks de vitórias mais concentrados temporalmente — capitalização amplifica quando funciona.
2. **H-regime-dependente**: snowball passa em 2025-H1 chop (alta densidade de mean-rev wins) e falha em 2024-H2 bull.
3. **H-simetria (refutação)**: snowball falha em TODAS as famílias mean-rev. Razão: mean-rev por definição tem wins frequentes mas pequenos; capitalizar amplifica drawdowns de losses concentrados.

## Alternativas consideradas

### Revogar ADR-0028/0029 silenciosamente
Rejeitado. Proibição foi documentada publicamente no manifest. Revogação sem ADR explícito vira "movimento de régua post-hoc" — exatamente o padrão que anti-cherry-pick (ADR-0049 §Padrão 5) bloqueia.

### Testar snowball **em vez de** fixed nas próximas séries
Rejeitado. Perderia baseline de comparação. Duplicata fixed+snowball é o desenho que preserva falsificabilidade.

### Implementar kelly_like também
Rejeitado. ADR-0028/0029 listaram kelly_like e martingale junto com snowball. Snowball é o mais simples dos três; provar valor dele primeiro, se passar, ADR futura revisa os outros dois.

## Plano de execução

1. **Implementar snowball no engine** (ADR-0063-impl, deste ADR):
   - `SizingMode` enum em `risk/schemas.py`
   - Engine passa `capital_corrente` dinâmico quando `sizing_mode=snowball`
   - CLI `--sizing-mode {fixed_notional,snowball}`, default fixed
   - Testes unitários: snowball capitaliza após PnL+, deduz após PnL−, equivalente a fixed quando PnL=0

2. **Re-rodar Série CG com snowball** (ADR-0064, closeout + comparação):
   - 9 pilotos idênticos a CG, só `--sizing-mode snowball`
   - Summarizer compara USD combo-a-combo, aplica gate snowball
   - Se 4/9 passam e USD > fixed, candidato v3b

3. **Re-rodar Série CH com snowball** (ADR-0065):
   - Mesma estrutura, CH é RSI short

4. **Promoção v3b/v4b** (ADR-0066+):
   - Se ambos passam, 2 manifests novos complementares ao par v3+v4 fixed
   - Audit (espelho ADR-0059)
   - Notificação bot

5. **Bot roda 4 manifests em paralelo** (v2 + v3 + v4 + v3b/v4b aprovados):
   - 21d paper
   - Bot reporta qual par (fixed/snowball) rende mais em real

## Consequences

### Positive
- Rompe herança fixed-only sem descartar evidência ADR-0029.
- Dá ao bot decisão empírica entre sizings.
- Política replicável: toda família futura (Donchian short, MA crossover) testa dupla.

### Negative
- 2x compute por série daqui pra frente.
- 2x manifests ativos em bot (sobrecarga de paper reporting).
- Se snowball falhar consistentemente, tempo perdido — mas ganha validação empírica.

### Neutral
- V2/V3 não mudam (continuam fixed).
- Proibição ADR-0028/0029 não é deletada, é contextualizada.

## Critério de sucesso

1. Engine suporta snowball ✓
2. Testes passam ✓
3. Séries futuras rodam dupla ✓
4. Manifests v3b/v4b aprovados se snowball vence ✓

## Fora do escopo

- Kelly-like, martingale (ADR separada se snowball passar).
- Sizing adaptativo por regime (§D3 vol-adjusted, ADR-0050).
- Mudar fração ou alavancagem (deste ADR mantém 0.1 e 2x).
