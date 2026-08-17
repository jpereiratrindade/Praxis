# PRAXIS-LIC-001 — Licenciamento governado

## Função

Permitir que a constituição de um projeto novo produza uma decisão de licença
explícita e verificável sem transformar ausência de metadata em autorização
para relicenciar projetos existentes.

## Operação

O template de novo projeto contém `.hoa/initial-constitution`. Antes de iniciar
o desenvolvimento, execute uma das formas abaixo a partir do Praxis:

```text
python3 scripts/bootstrap_project_licensing.py /caminho/projeto
python3 scripts/bootstrap_project_licensing.py /caminho/projeto --license MIT
python3 scripts/bootstrap_project_licensing.py /caminho/projeto \
  --policy-exception MIT --rationale "Decisão institucional GOV-42"
```

A forma sem escolha usa `GPL-3.0-or-later`. Escolha explícita e exceção usam um
`LICENSE` já presente ou `--artifact-source`; o bootstrap nunca substitui um
`LICENSE` existente. Todo `LICENSE` constituído deve declarar exatamente
`SPDX-License-Identifier: <resolved>`; o hash governa os bytes e a declaração
governa a identidade determinística afirmada para esses bytes. O validator é
somente leitura:

```text
python3 scripts/validate_governed_licensing.py /caminho/projeto
```

## Critérios executáveis

`tests/licensing/test_governed_licensing.py` cobre LIC-T01 a LIC-T12, além de
estados parciais, proveniência impossível, reexecução conflitante e tentativa
de fornecer artefato ao default. O gate governado é
`scripts/verify_praxis_licensing.sh`.

O escopo determinístico compreende schema, política interna, proveniência,
rationale, presença, SHA-256 e a declaração SPDX obrigatória do artefato. Não
classifica texto jurídico arbitrário nem detecta edição coordenada de metadata e
artefato que produza um novo estado internamente coerente.

A capability é uma autorização local positiva e consumível. Sua presença não
prova historicamente que o diretório nasceu deste template; quem pode criar o
marcador local pode conceder essa autorização. Os writes de `LICENSE` e metadata
são individualmente atômicos, mas a sequência completa não é uma transação. Uma
falha excepcional pode deixar estado parcial rejeitado pelo validator e exigir
recuperação explícita.
