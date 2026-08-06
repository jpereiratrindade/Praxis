# ADR-0001 — Núcleo nativo C++23

## Estado

Aceito.

## Contexto

O MVP inicial validou a Forja em Python, mas não materializou a arquitetura C++
nem a governança do próprio HOA descritas em HOA-SisTer/0.1.

## Decisão

O executável oficial `sister-ops` será implementado em C++23. Python permanece
apenas como implementação de referência durante a migração da Forja.

A primeira entrega segue H0: `status`, `health`, `doctor`, registry mínimo,
contratos, políticas e validadores sem LLM e sem skills mutáveis.

## Consequências

- CMake e CTest passam a governar o núcleo;
- CI verifica C++23 e baseline de governança;
- novas capacidades devem entrar como skills registradas;
- a Forja Python será portada incrementalmente, sem expansão funcional paralela.
