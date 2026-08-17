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

## Licensing prospectivo

Novos projetos criados a partir do template Praxis recebem a capacidade
consumível `.hoa/initial-constitution`. Somente essa evidência positiva autoriza
`bootstrap_project_licensing.py` a constituir uma decisão ausente. Sem escolha
explícita, o default interno é `GPL-3.0-or-later`; uma escolha explícita preserva
sua proveniência mesmo quando difere do default.

A presença do marcador reconhecido expressa autorização local para executar a
constituição inicial. Ela não constitui prova histórica ou criptográfica de que
o diretório se originou do template Praxis. Criar o marcador manualmente é uma
concessão explícita dessa autorização local e deve permanecer uma ação
governada pelo responsável pelo workspace.

Uma exceção real ao default é uma categoria separada, deve divergir do default
e exige rationale. A constituição cria `.hoa/licensing.yaml`, vincula a decisão
ao `LICENSE` por SHA-256, exige no artefato uma declaração
`SPDX-License-Identifier` igual à licença resolvida e consome a capacidade
inicial. Reexecuções validam e preservam a decisão existente.

Ausência de `.hoa/licensing.yaml` sem a capacidade inicial significa legado ou
decisão ainda não constituída; nunca significa autorização para criar ou
substituir `LICENSE`. Essa política verifica coerência e proveniência de
engenharia, não compatibilidade ou conformidade jurídica.

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
