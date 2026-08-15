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

## Histórico de verificação

O histórico canônico possui dois estados válidos:

```text
empty       = NONE / 0000000 / NONE / NONE
established = marco / commit / gate / evidência
```

Os quatro campos formam uma tupla atômica. Misturar sentinelas de `empty` com
valores estabelecidos deve falhar fechado. Um repositório pode ter zero ou mais
commits enquanto seu histórico de verificação continua `empty`; commit de
proveniência não equivale a verificação científica.

A transição `empty -> established` é válida quando todas as provas usuais são
satisfeitas. A transição reversa é inválida na linha Git corrente, pois apagaria
histórico governado em vez de constituir um novo bootstrap.

## Bootstrap

`create_once` é a política preferida para scaffolds constitucionais. Reexecução
em projeto já constituído deve ser não destrutiva.

## Integridade

Gates devem rejeitar referências governadas quebradas e divergências entre
estado canônico, manifests de projeto e documentação que declare estado atual.

## Escopo da prova

`verified` deve ser interpretado apenas dentro do escopo efetivamente submetido
ao gate e sustentado pela evidência governada. Promoção de um marco não autoriza
reivindicar maturidade, capacidade, escala, integração ou prontidão operacional
que não tenham sido comprovadas.

## Avaliações independentes

Findings produzidos por revisão humana, LLM ou outra ferramenta externa são
insumos de investigação. Eles não alteram estado canônico, não promovem marcos e
não criam regras ou gates sem evidência e decisão governada subsequentes.

## Autoaplicabilidade

Quando uma política do método for materialmente aplicável ao próprio Praxis, a
implementação deve satisfazê-la ou registrar de forma explícita a fronteira que
justifica a exceção.
