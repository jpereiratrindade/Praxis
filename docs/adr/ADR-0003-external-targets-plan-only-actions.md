# ADR-0003 — Alvos externos e ações plan-only

## Estado
Aceito.

## Decisão
O HOA H1 registra alvos externos em `config/targets`, observa filesystem e TCP por adapters determinísticos e permite apenas a produção de planos para ações externas allowlisted. `action apply` permanece desabilitado.
