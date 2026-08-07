# HOA-EXP-004 — Workspace C++ genérico

## Hipótese
O HOA consegue operar um projeto C++ que não pertence ao ecossistema SisTer.

## Preparação
Criar uma pasta temporária com `CMakeLists.txt`, inicializar Git e opcionalmente adicionar `.hoa/project.yaml`.

## Experimento

```bash
hoa --project /tmp/hoa-lab workspace inspect
hoa --project /tmp/hoa-lab workspace sync-status
```

## Critérios de aceitação
- a raiz exibida é canônica;
- CMake e Git são descobertos sem nomes SisTer;
- caminhos fora da raiz são rejeitados pelo modelo de workspace;
- a ausência do manifesto não impede inspeção básica;
- nenhuma operação externa é executada sem solicitação explícita.
