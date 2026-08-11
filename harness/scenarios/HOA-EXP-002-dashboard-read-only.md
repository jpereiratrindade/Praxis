# HOA-EXP-002 — Painel observacional não mutável

## Hipótese

É possível apresentar o estado do Praxis em uma interface web útil sem conceder autoridade operacional à interface.

## Estado inicial

- núcleo C++23 compilado;
- baseline de governança pronta;
- fase H0;
- skills mutáveis desabilitadas.

## Intervenção autorizada

Iniciar `sister-ops dashboard serve` em `127.0.0.1` e consultar rotas por HTTP.

## Resultado esperado

- `GET /` retorna o painel;
- `GET /api/snapshot` retorna JSON observacional;
- `HEAD` retorna cabeçalhos sem corpo;
- `POST`, `PUT`, `PATCH` e `DELETE` retornam `405`;
- nenhum arquivo ou contrato é modificado.

## Evidência mínima

- saída do comando;
- códigos HTTP observados;
- resultado dos testes `dashboard_read_only_tests`.
