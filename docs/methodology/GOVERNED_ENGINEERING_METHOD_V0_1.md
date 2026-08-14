# Praxis Governed Engineering Method v0.1

## Propósito

Transformar aprendizado obtido durante a construção de sistemas em memória
operacional governada e em mecanismos verificáveis que reduzam recorrência de
erros estruturais.

O método não substitui o domínio do projeto. Ele governa **como o projeto sabe
onde está, o que comprovou e o que está autorizado a fazer em seguida**.

## Princípios

### M01 — Canonical State

Todo projeto governado possui um manifesto pequeno e legível por máquina que é
a fonte canônica de sua posição corrente.

Documentos humanos podem refletir esse estado, mas não constituem fonte de
verdade concorrente.

### M02 — Governed Milestones

Avanços relevantes devem ser ligados a um marco/experimento identificável,
com escopo, critérios e gate explícitos.

Um marco não é considerado comprovado apenas porque seu código existe.

### M03 — Operational Evidence ≠ Governed Evidence

Resultados produzidos em `build/`, `.build/`, `.run/` ou diretórios equivalentes
são evidência operacional transitória.

Quando um resultado sustenta promoção de estado, uma evidência governada deve
ser preservada em caminho versionável e verificável, preferencialmente com
checksum.

### M04 — Monotonic Bootstrap

Bootstrap inicializa; não regride.

Ao reconhecer um projeto já constituído, o bootstrap deve ser `create_once` ou
idempotente e jamais sobrescrever silenciosamente memória de fases posteriores.

### M05 — Referential Integrity of Governed Metadata

Metadados governados são testáveis.

Arquivos, gates, testes, evidências e commits declarados devem existir e
continuar coerentes com o repositório.

### M06 — Build Is Transient

Build não representa estado do projeto.

Artefatos de build devem ser descartáveis e reconstruíveis a partir da árvore
versionada. Caminhos absolutos ou caches de outra máquina não podem ser usados
como prova de estado.

### M07 — Learning → Rule → Gate

Uma falha estrutural recorrível não está completamente resolvida quando apenas
se corrige sua ocorrência atual.

O fechamento preferido é:

`problema → diagnóstico → correção → aprendizado → regra → gate`

A generalização deve nascer de fatos observados nos projetos, evitando criar
burocracia preventiva sem evidência.

## Memória operacional governada

A memória governada mínima combina:

1. estado canônico;
2. manifesto do marco/experimento;
3. gate reproduzível;
4. evidência preservada;
5. proveniência Git.

Documentação explica. Memória governada registra o que foi comprovado.

## Ciclo de uso

1. observar divergência ou risco;
2. decidir se o problema é local ou generalizável;
3. corrigir o projeto sem ampliar escopo funcional;
4. preservar a prova da correção;
5. extrair regra geral quando houver evidência suficiente;
6. implementar verificador/gate reutilizável;
7. aplicar o método em novos projetos;
8. revisar o método à luz de novas contraprovas.

## Relação com o ciclo reflexivo

O método operacionaliza a passagem entre:

- observação/compreensão;
- coevolução/adaptação;
- estruturação técnico-científica.

O Praxis governa essa memória e seus verificadores. O runtime dos projetos não
depende do Praxis para operar.
