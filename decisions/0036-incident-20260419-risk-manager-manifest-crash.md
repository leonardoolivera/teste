# 0036 — Incidente 2026-04-19: crash do risk_manager em signals manifest + ativação de paper-mock contraprova

**Status:** Accepted (registro de incidente)
**Date:** 2026-04-19
**Deciders:** @botbinance (fix runtime) + agente AF (validação + paper-mock).
**Scope:** Operacional / integração AF↔bot. Não altera manifest aprovado nem engine canonical.

## Context

Após ativação paper (2026-04-19 00:25 UTC, 3 symbols; re-configurado 00:43 UTC removendo BTCUSDT, pós ADR-0032/0033), o runtime manifest do @botbinance executou por ~10h com bug silencioso no `risk_manager.evaluate_signal` path para engines manifest.

**Sequência do incidente (reportado por @botbinance no bridge):**

1. **03:00:25 UTC** — Engine `bollinger_manifest_v2` gerou `SIGNAL_CREATED` válido para SOLUSDT 1h (`long, trigger=85.56, macd=400.53`). Sinal consistente com ADR-0032 / BK.8 (SOL `semi_robust_window`).
2. **03:00:~25 UTC** — `risk_manager.evaluate_signal` crashou com `TypeError: RiskDecision.__init__() got an unexpected keyword argument 'estimated_risk_pct'`. Signal não executou.
3. **08:00:33 UTC** — Segundo SOLUSDT perdido; mesmo bug.
4. **08:00:32 UTC** — ETHUSDT também gerou signal válido, mesmo crash.

**Root cause (reportado):**

Um bloco "step 0" do `evaluate_signal` checava se `manifest.disallow_sizing_modes` conflitava com `snowball.enabled=true` (legado do bot). Se sim, construía uma `RiskDecision` de rejeição com:
- kwarg inexistente `estimated_risk_pct` (não é campo do dataclass).
- `reason` como string raw em vez de enum.

Como `snowball.enabled=true` é o padrão do bot para engines classics, o bloco batia em **todo** signal manifest → crash determinístico.

## Decisions (do lado AF)

### 1. Validação do fix do bot (bypass em vez de reject)

O @botbinance removeu o bloco step-0 e implementou `_calculate_sizing_manifest(signal, current_price, mf)`:
- `qty = fixed_notional / current_price`, com min_qty / step_size aplicados.
- Valida exposure gates (per-asset e total).
- Sem risk-per-trade gate (manifest ADR-0030 invariante 4 declara `stop=disabled`; `stop_distance` não existe → gate é estruturalmente inaplicável).
- `calculate_sizing` early-return para esse método quando `signal.manifest_contract != None`.

**Avaliação AF:** decisão arquitetural correta. O campo `disallow_sizing_modes` no manifest é uma restrição **sobre o combo**, não sobre o bot. Intent original (ADR-0029): "snowball/kelly/martingale não podem ser aplicados **neste** combo." Rejeitar signals quando snowball está enabled globalmente força "snowball xor manifest"; bypass honra "snowball ∥ manifest" como regimes independentes.

Aceitação condicional: ADR local do @botbinance precisa documentar explicitamente que o exposure gate consulta posições classics + manifest juntas. Se sim, manifest pode ser bloqueado por razão ortogonal ao contrato (exposure acima do cap). Não é erro, é escolha — mas precisa estar documentada para auditoria futura.

### 2. Signals perdidos não recuperados / não simulados

Os 3 signals (SOLUSDT 03:00, SOLUSDT 08:00, ETHUSDT 08:00) ficam **fora** de qualquer comparação AF↔bot e fora de qualquer estatística de edge live. Motivo: manifest-faithful (ADR-0030) implica runtime autoritativo — trades que o runtime não executou não existem no universo realizado. Simular/back-preencher violaria o contrato.

Aplicação prática: qualquer futuro relatório de "N trades live em paper" ignora os 3 eventos perdidos. Log fica como auditoria de integridade, não como fonte de dados estatísticos.

### 3. Paper-mock contraprova — acionada

A oferta prévia de paper-mock (posts 2026-04-19 early, antes do incidente) sai de "opcional" para "necessária". Racional:

- Bug passou pelo P7 suite porque o cenário específico (`snowball.enabled=true` × `signal.manifest_contract != None`) não estava exercitado.
- Ausência desse caso em testes significa que **outros cenários-fronteira podem estar igualmente não-cobertos**. Não dá pra deduzir confiança do restante do code path manifest só por unit tests existentes.
- Paper-mock roda a engine canonical AF contra o mesmo stream de candles que o bot consome, em paralelo, e compara fill/exit tick-a-tick. Detecta divergências antes que virem perda realizada.

**Spec do feed solicitado:**

Preferência: **candles 1h reais** em parquet ou CSV, com colunas `timestamp_utc, open, high, low, close, volume`. Cobertura: últimas 120h + append incremental pós-close de cada candle 1h. Destino: `c:/Users/leo-a/agents_bridge/paper_mock_feed/`.

Alternativa: **log de eventos JSONL** do bot (SIGNAL_CREATED, RISK_EVALUATED, POSITION_OPENED, POSITION_CLOSED com payload completo). Exige replicação independente do candle stream do meu lado via Binance public API + join-by-timestamp.

Opção A é mais robusta (elimina drift de clock/endpoint entre AF e bot). Opção B é fallback.

### 4. Critério de encerramento do paper-mock

- **(a) Sucesso:** ≥10 trades live em ETH+SOL combinados sem divergência detectada → encerrar paper-mock, confiança restaurada.
- **(b) Falha:** divergência detectada (fill price, exit timing, sizing, decisão de entry/exit) → parar tudo imediatamente, abrir ADR de incidente 2, triage conjunto com @botbinance.
- **(c) Timeout:** 7 dias corridos sem trades suficientes → encerrar por ausência de amostra, re-avaliar.

### 5. Impacto no rollout do ADR-0034

Nenhum. Estado atual continua válido:
- ETHUSDT + SOLUSDT 1h @ $2000 notional, active_since 2026-04-19 00:25 UTC (com bug 03:00-10:34 mas agora corrigido).
- BTCUSDT deferred até 21d corridos de paper limpo (elevado de 14d no ADR-0035).
- `rollout_priority_live` weakest-wins continua válido.

O paper-mock **não substitui** o paper ao vivo — roda em paralelo como contraprova de runtime integrity.

## Consequences

**Prós:**
- Incidente registrado com timeline e root cause → auditável.
- Fix validado do ponto de vista do contrato ADR-0030 (bypass é coerente, reject não era).
- Paper-mock ativa detecção de divergências silenciosas para cenários não cobertos por unit tests.
- Critérios de sucesso/falha/timeout declarados antes de rodar → evita redefinir terms depois.

**Contras:**
- Paper-mock custa trabalho de infra (export de feed do bot + loader do meu lado). Valor é condicional: só paga se houver divergência real ou se der sinal de saúde para o resto do rollout.
- Signals perdidos (3) representam ~1 dia de edge potencial não-capturado em SOL/ETH. Em volume, SOL 2024-H2 validation deu 69 trades em 6 meses ≈ 0.38 trades/dia; 2 SOL + 1 ETH perdidos em 10h é consistente com sampling estocástico, não um sinal de perda sistemática.

**Riscos residuais:**
- Se outro bug silencioso existir em code path diferente (ex: POSITION_CLOSED), só o paper-mock pode detectar. Sem ele, descobriríamos por perda realizada.
- Paper-mock depende de integridade do export do bot. Se o export for inconsistente (ex: usa clock local vs UTC), a comparação fica ruidosa. Precisa ack explícito do @botbinance que o feed usa timestamps canonizados.

## Follow-ups

- [ ] Aguardar resposta do @botbinance sobre Opção A vs B do feed.
- [ ] Construir `tools/paper_mock_cross_check.py` quando o feed começar a chegar: carrega feed real, roda engine canonical, emite diff vs log de eventos do bot.
- [ ] Monitorar primeiros signals 11:00 UTC pós-fix. Se todos passarem sem exception, paper-mock continua útil mas urgência diminui.
- [ ] Se 10+ trades clean em 5-7 dias → encerrar paper-mock, registrar resultado em follow-up ADR.
- [ ] Se qualquer divergência detectada → parar tudo, abrir ADR-0037 incidente 2.

## Artefatos

- Bridge log: `c:/Users/leo-a/agents_bridge/conversa.md` — timeline 2026-04-19.
- ADR-0030 (runtime-faithful contract) — invariantes mantidos.
- ADR-0034 (weakest-wins live) — rollout não alterado.
- ADR-0035 (Série BO) — critério 2ª onda elevado 14d→21d (aceito por @botbinance).
