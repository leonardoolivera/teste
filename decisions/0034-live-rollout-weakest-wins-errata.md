# 0034 — Errata ao ADR-0033: `validation_window` é offline-only; `rollout_priority_live` usa weakest-wins por (symbol, engine)

**Status:** Accepted
**Date:** 2026-04-19
**Deciders:** Usuário (owner do projeto) + agente + @botbinance (handoff bridge).
**Errata target:** [0033 — Bollinger window sensitivity sweep BN](0033-bollinger-window-sensitivity-sweep-bn.md)

## Context

ADR-0033 produziu a tabela cross-axis 2D (BK × BN) com `rollout_priority` por combo:

| Combo | Classe 2D | Rollout |
|---|---|---|
| ETH 2024-H1 | fragile_2d | 2ª onda, 50% sizing |
| ETH 2025-H1 | semi_robust_num_std | 1ª onda |
| BTC 2024-H2 | fragile_2d | 2ª onda, 50% sizing |
| SOL 2024-H2 | semi_robust_window | 1ª onda |

A ativação paper pelo @botbinance às 2026-04-19 00:25 UTC (ETHUSDT + BTCUSDT + SOLUSDT 1h @ $2000 notional cada, depois BTC removido após ler ADR-0032/0033) expôs um erro metodológico: **`validation_window` não existe em runtime**. O runtime opera por `(symbol, engine, params)`, não por `(symbol, engine, params, validation_window)`. ETH é **uma stream só** em live — não há como distinguir "ETH 2024-H1 fragile" de "ETH 2025-H1 robust" quando os dois foram validados na mesma engine/params.

Implicação: a tabela de `rollout_priority` do ADR-0033 está projetando distinções offline (janela de validação) em runtime, o que é incoerente. O feedback runtime-aware veio do @botbinance: *"no runtime, as duas janelas colapsam no mesmo trade. O bot vê só 1 stream ETHUSDT."*

## Decision

### 1. Reformular `rollout_priority` como função `weakest_wins` por `(symbol, engine, params)`

Para cada `(symbol, engine, params)` que em live colapsa múltiplas validações offline, a classe operacional é a **mais fraca** entre as validações daquele symbol — não a melhor nem a média.

Motivação: em live, qualquer degradação observada pode ter projetado de qualquer uma das validações. Não há como atribuir o modo de falha à janela "boa" ou à janela "ruim". O sizing precisa cobrir o pior caso conhecido.

### 2. Re-classificação `rollout_priority_live` (valores novos)

Aplicando weakest-wins aos 4 combos do manifest v2:

| Symbol runtime | Validações offline | Classes cross-axis (BK×BN) | Weakest | `rollout_priority_live` |
|---|---|---|---|---|
| ETHUSDT 1h | 2024-H1, 2025-H1 | fragile_2d, semi_robust_num_std | fragile_2d | **`fragile_2d`** |
| BTCUSDT 1h | 2024-H2 | fragile_2d | fragile_2d | **`fragile_2d`** |
| SOLUSDT 1h | 2024-H2 | semi_robust_window | semi_robust_window | **`semi_robust_window`** |

Sobra: nenhum symbol em live tem classe `robust`. SOL é o único `semi_robust`. ETH e BTC são `fragile_2d`.

### 3. Ordem de rollout revisada

- **1ª onda (ativa desde 2026-04-19 00:25 UTC):** ETHUSDT + SOLUSDT 1h, fixed_notional $2000 cada. ETH entra como `fragile_2d` (não `semi_robust` como o ADR-0033 original sugeria), mas o valor de diversificação com SOL (`semi_robust_window`) justifica manter. O modo de falha esperado de cada um continua diferente.
- **2ª onda (gatilho: 14 dias corridos sem MANIFEST_EXIT-abaixo-do-entry em ETH ou SOL + DD combinado < 5%):** adicionar BTCUSDT 1h com **notional reduzido ($1000 = 50% do padrão)**. Motivo: BTC `fragile_2d` + ativo lento (BN.3 trades=29 < 30; BN.7 trades=30 no limiar). Notional reduzido reduz blast radius se BTC degradar rápido.
- **Não há 3ª onda planejada.** ETH já está em $2000 desde a 1ª onda; ajustar sizing de ETH para baixo agora seria churn operacional sem benefício estatístico claro.

### 4. Sizing em live é por-symbol, não por-combo

Notional override deve ser implementável no bot como `{symbol: notional_usd}` dentro do manifest/config, não como tabela por combo-validation. O loader do @botbinance tem isso na fila (viável, sem pressa até 2ª onda).

### 5. Opacidade diagnóstica documentada

Quando uma degradação aparecer em ETH live, **não há atribuição runtime-wise** entre "ETH 2024-H1 projetou mal" vs "ETH 2025-H1 projetou mal". Só se sabe que a distribuição ETH 2024-H1→2025-H1 incluía uma janela frágil e essa fragilidade se materializou. Mitigação: paper-mock contraprova (feed das barras reais do live + log runtime do bot + AF engine canonical) pode isolar se a falha é metodológica (modelagem) ou estrutural (regime mudou vs janelas validadas). Acionar apenas se sinal anômalo aparecer nos primeiros 5-20 trades.

## Consequences

**Prós:**
- Narrativa do rollout alinhada com o que o runtime de fato enxerga. Elimina risco de falsa confiança ("ETH é robust, relaxa").
- Regra `weakest_wins` é simples e defensiva: qualquer validação nova adicionada ao mesmo symbol só pode piorar a classe em live, nunca melhorar (porque live já carrega o pior caso existente).
- Sizing reduzido para BTC na 2ª onda preserva o princípio "fragile = menor blast radius" sem depender de projeção de validation_window.

**Contras:**
- Perde-se a discriminação entre "ETH 2025-H1 foi passada em 2 eixos de perturbação" (informação real offline) e "ETH em live é fragile_2d" (informação real online). Alguém lendo só o live pode subestimar a robustez offline do config atual.
- Regra `weakest_wins` desencoraja adicionar validações em semestres adicionais — elas só podem piorar a classe live se forem frágeis. Incentivo perverso: preferir não validar a validar e descobrir fragilidade.
- Mitigação contra (contras acima): manter `robustness.num_std_sensitivity`, `window_sensitivity`, `cross_axis_2d` por-combo no manifest (offline) + adicionar `rollout_priority_live` por-symbol (online) como campos distintos. Ambos ficam auditáveis. O ADR-0033 não é deletado, só anotado.

**Riscos residuais:**
- Em degradação aguda (primeiros 5 trades fora do esperado), o modo de falha é opaco. Paper-mock contraprova é a única ferramenta isolada disponível. Aceita.
- Critério da 2ª onda ("14 dias + DD <5%") é estimativa, não backtested. Pode ser curto demais para capturar regime switch lento. Revisado em ADR futuro se paper mostrar que 14d é insuficiente para decidir.

## Follow-ups

- [ ] Atualizar `exports/approved/bollinger_width_regime_20260418_v2.json` adicionando campo top-level `rollout_priority_live` por-symbol (não por-combo).
- [ ] Anotar ADR-0033 com cross-reference a este ADR (addendum, não revisão do corpo).
- [ ] Notificar @botbinance no bridge (feito no post 2026-04-19 que deu origem a este ADR).
- [ ] Monitorar primeiros fills de ETH/SOL live (1º candle 01:00 UTC) via reports do bot. Acionar paper-mock contraprova apenas se sinal anômalo.
- [ ] Não abrir nova Série offline antes de ≥ 2 semanas de paper limpo. Reservas: Série BO (min_width_bps), Série BL (4h), fila Cat B (6 combos auditoria) — prioridade relativa a ser decidida após ver comportamento live.

## Artefatos

- Bridge log: `c:/Users/leo-a/agents_bridge/conversa.md` — posts 2026-04-19 (verdict BK, verdict BN, pergunta rápida, ack+ajuste do bot, ack ativação).
- ADR raiz: `decisions/0033-bollinger-window-sensitivity-sweep-bn.md`.
- Manifest: `exports/approved/bollinger_width_regime_20260418_v2.json`.
