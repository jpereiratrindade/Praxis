# Engenharia de Workspace do HOA

O Laboratório Virtual trata cada pasta de projeto como objeto experimental explícito. A engenharia do HOA separa cinco dimensões:

1. **Descoberta** — raiz, CMake, Git e manifesto `.hoa/project.yaml`.
2. **Observação** — estado reproduzível sem alteração do produto observado.
3. **Transformação** — mudança declarada, confinada e classificada por risco.
4. **Verificação** — comparação determinística entre estado esperado e observado.
5. **Evidência** — registro reconstruível de entrada, operação, resultado e autoridade.

## Fluxo mínimo

```text
selecionar workspace
  -> canonicalizar fronteira
  -> descobrir recursos
  -> observar estado
  -> classificar discrepância
  -> propor/autorizar transformação
  -> verificar
  -> registrar evidência
```

## Git como primeiro laboratório

`hoa workspace sync-status [--fetch]` é a primeira operação transversal. Sem `--fetch`, apenas lê refs locais. Com `--fetch`, atualiza refs remotas locais e por isso é classificada como `mutate_local`, embora não altere arquivos de trabalho nem crie merge.

Estados: `UP_TO_DATE`, `AHEAD`, `BEHIND`, `DIVERGED`, `DIRTY`, `UNAVAILABLE`, `NOT_REPOSITORY`.

A futura operação `workspace sync` deverá aceitar automaticamente apenas `BEHIND` + working tree limpa + fast-forward possível. `AHEAD`, `DIVERGED` e `DIRTY` devem bloquear execução automática.
