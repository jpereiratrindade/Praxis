# Política — Estado e evidência de projetos governados

## Estado canônico

Projetos que adotam `praxis-governed-engineering/0.1` devem registrar
`.hoa/project-state.yaml` ou equivalente declarado pelo workspace.

O manifesto deve ser pequeno, evitar narrativa e registrar no mínimo:

- projeto;
- método de governança;
- fase;
- último marco verificado;
- commit do último marco verificado;
- gate do último marco;
- evidência governada correspondente;
- próximo marco e seu estado de autorização;
- política/script de bootstrap quando houver.

## Autorização

Próximo marco proposto não equivale a marco autorizado.

A autorização deve ser explícita e legível por máquina.

## Evidência

Diretórios transitórios de build não são locais válidos como única evidência de
promoção.

## Bootstrap

`create_once` é a política preferida para scaffolds constitucionais. Reexecução
em projeto já constituído deve ser não destrutiva.

## Integridade

Gates devem rejeitar referências governadas quebradas e divergências entre
estado canônico, manifests de projeto e documentação que declare estado atual.
