# 0060 — Manifest v3 audit closeout: PASS 3/3, ativação + notificação bot

**Status:** Accepted — manifest v3 ativado; bot notificado via bridge
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0058 (promoção), ADR-0059 (pré-registro audit), manifest `exports/approved/bollinger_short_width_20260419.json`.

## Context

ADR-0059 pré-registrou 3 gates de audit (A: estabilidade MC, B: filtro load-bearing, C: exclusão confirmada) com 14 runs. Executado. Dados crus: `exports/diag/manifest_v3_audit_summary.json`.

## Resultados

### Gate A — estabilidade MC: 12/12 PASS

Sharpe/MDD/cost_r **determinísticos** entre seeds 42/1337/2024 (WF determinístico, comportamento esperado). MC p5 variação máxima 180bp (CG.5: 9924 → 9779 em seed 2024, ainda acima do gate 9500).

| Combo | seed=42 MCp5 | seed=1337 MCp5 | seed=2024 MCp5 | delta max |
|---|---:|---:|---:|---:|
| CG.3 | 9729 | 9744 | 9709 | 35 |
| CG.4 | 9953 | 9954 | 9967 | 14 |
| CG.5 | 9924 | 9848 | 9779 | 145 |
| CG.6 | 10460 | 10279 | 10378 | 181 |

**Nenhum combo aproxima do gate** em nenhum seed. CG.5 é o mais sensível (−145bp pior em seed 2024) mas ainda folgado.

**Veredicto A: sem lucky-seed.** 4 combos estatisticamente estáveis.

### Gate B — filtro load-bearing: 4/4 PASS (gate ≥3/4)

| Combo | with Sh | no-filter Sh | Δ Sh | with cost_r | no-filter cost_r | sem filtro FAIL? |
|---|---:|---:|---:|---:|---:|---|
| CG.3 | 1.38 | 0.80 | +0.58 | 0.9505 | 0.9396 | Sharpe + MCp5 + cost_r |
| CG.4 | 1.24 | −0.07 | +1.31 | 0.9774 | 0.9403 | Sharpe + MCp5 + cost_r |
| CG.5 | 2.39 | 2.45 | −0.06 | 0.9594 | 0.9414 | cost_r |
| CG.6 | 2.71 | 1.92 | +0.79 | 0.9512 | 0.9419 | cost_r |

**Achado chave**: filtro é load-bearing **em todos 4** combos — todos os cost_r **sem filtro** ficam em 0.94 (abaixo do gate 0.95). Consistente com ADR-0048 Audit B no long (+0.89 Sharpe delta médio).

**CG.5 nuance**: Sharpe sem filtro (2.45) é marginalmente **maior** que com filtro (2.39), mas cost_r cai (0.9594 → 0.9414 FAIL). Filtro não é que "gera Sharpe"; é que **estabiliza custo** — remove trades de baixa width que são quem carrega stress de fees. Edge puro já é alto em ETH 2025-H1; filtro protege contra cenários de stress.

**Veredicto B: filtro load-bearing.** Manifest representa corretamente a origem do edge. Padrão 10 (ADR-0057) confirmado empiricamente.

### Gate C — exclusões confirmadas: 2/2 PASS

- **CG.1 seed=1337**: Sharpe 0.52 (idêntico seed 42). FAIL Sharpe. Exclusão mantida.
- **CG.9 seed=1337**: Sharpe 0.72, MC p5 9095, cost_r 0.9497. Triplo FAIL. Exclusão mantida.

Seeds alternativos não resgatam combos excluídos. `expansion_policy` robusta.

## Veredicto overall

**Manifest v3 PASS 3/3 gates.** Ativação autorizada.

## Ações imediatas

### 1. Atualizar `live_status` do manifest

```json
"live_status": "active"
"live_status_since": "2026-04-19T15:20:00Z"
```

Campo `live_status_unblock_adr` removido.

### 2. Notificar BotBinance via bridge

Postar em `inbox_botbinance.md`:
- Manifest path: `exports/approved/bollinger_short_width_20260419.json`
- 4 combos aprovados (CG.3/4/5/6)
- Runtime faithful idêntico a v2 — bot já tem adapter
- Manifest complementar a v2 (não supersede); bot deve rodar ambos em paralelo
- Signal-only: bot confirma leitura + reporta divergência de premissa se detectar

### 3. Timebox paper

21d paper-trade (ADR-0049 padrão). Se sem MANIFEST_EXIT-abaixo-do-entry e DD combinado < 5% em 21d → escalar conforme rollout_priority futura (por enquanto todos os 4 combos em wave 1, notional 2000).

## Consequences

### Positive
- Primeiro manifest short ativo no projeto.
- Audit B confirma padrão 10 empiricamente (filtro composicional parametrizado ao regime).
- Projeto agora tem 2 manifests complementares (long bull + short chop), cobrindo mais regimes.

### Negative
- Manifest depende de 2025-H1 pra 3 dos 4 combos. Se regime muda, combos podem degradar juntos.
- CG.5 é o único combo onde sem-filtro Sharpe > com-filtro — sinaliza que em ETH 2025-H1 a composição pode estar sobre-filtrando. Monitorar em paper.

### Neutral
- V2 inalterada.
- Audit B mostrou CG.5 Sharpe sem filtro maior — **não** motivo pra remover filtro (cost_r FAIL sem ele), mas documentação útil pra futura ADR sobre fine-tuning de min_width_bps.

## Critério de sucesso

1. Manifest atualizado com `live_status=active` ✓
2. Bot notificado via bridge ✓
3. Audit summary arquivado em `exports/diag/manifest_v3_audit_summary.json` ✓
4. Padrão 10 empiricamente validado ✓

## Fora do escopo

- Rollout priority detalhado por combo (todos em wave 1 notional 2000 — idêntico a v2 política).
- Fine-tuning `min_width_bps` (CG.5 sinaliza que talvez 250 seria melhor pra ETH 2025-H1, mas gate pré-registrado foi 300 — respeitar).
- Novos pilotos cross-regime.

## Próximo passo natural

Aguardar paper-trade 21d (timebox ADR-0049). Durante esse período:
- Série nova possível (ex: RSI short + filtro análogo, fora do manifest v3).
- Monitorar divergência bot vs AF (signal-only rule).
- Não tocar manifest v3 até fim do paper period.
