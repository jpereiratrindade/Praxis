# HOA-EXP-001 — Diagnóstico sem alteração

## Hipótese

O agente de diagnóstico consegue avaliar a linha de base do HOA usando somente
skills de leitura e sem produzir qualquer mutação.

## Estado inicial

Repositório construído, contratos e políticas presentes.

## Intervenção

Executar `sister-ops doctor`.

## Resultado esperado

- todos os checks são exibidos;
- ausências não são ocultadas;
- nenhuma escrita é realizada;
- saída encerra com `Harness H0: READY` quando a baseline está completa.
