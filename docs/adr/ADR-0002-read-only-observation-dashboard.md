# ADR-0002 — Painel web local e somente leitura

## Estado

Aceito.

## Contexto

O SisTer-HOA precisa tornar sua fase, governança e estado operacional visíveis sem antecipar uma interface de controle. Uma página web com ações mutáveis confundiria observação com autoridade e violaria a separação do Modo Harness.

## Decisão

Será disponibilizado um painel servido pelo núcleo C++23 com as seguintes restrições:

- escuta apenas em `127.0.0.1` no estágio H0;
- aceita apenas `GET` e `HEAD`;
- não expõe endpoints mutáveis;
- não executa comandos;
- não lê segredos;
- deriva o snapshot da mesma inspeção determinística usada por `health` e `doctor`;
- apresenta explicitamente o rótulo `READ ONLY`.

## Consequências

A interface oferece visibilidade sem se tornar plano de controle. Qualquer capacidade futura de operação web exigirá outro ADR, nova política de autoridade e progressão explícita de fase do Harness.
