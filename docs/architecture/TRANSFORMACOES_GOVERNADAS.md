# Transformações Governadas em Sistemas Reflexivos

## Fundamentos teórico-técnicos do Praxis

## 1. Propósito

Este documento estabelece a base conceitual para compreender mudanças de software no Praxis — originalmente desenvolvido como SisTer-HOA — não apenas como alterações textuais em arquivos, mas como **transformações governadas**: processos explicitamente orientados por objetivo, executados sob autoridade delimitada, verificados por mecanismos determinísticos e acompanhados de evidências reconstruíveis.

A formulação resulta da experiência de desenvolvimento do próprio HOA. Ao investigar como retirar do núcleo o vínculo direto com o SisTer, tornou-se evidente que o problema não era somente acrescentar um argumento `--project`. A questão mais profunda era definir como um operador pode receber um contexto, formular uma transformação, aplicá-la de maneira incremental, verificar seus efeitos e submeter o resultado à autoridade humana.

Os conceitos de **Transformação Governada** e **Série de Refatoração Arquitetural** são construções próprias do HOA. Eles não são apresentados como termos consolidados ou como substitutos de uma teoria única já existente. Sua fundamentação combina contribuições da engenharia de software, da cibernética, da reflexão computacional, da prática reflexiva, do desenho sociotécnico, da interação humano–automação, da proveniência e do assurance de software.

---

## 2. O problema do contexto implícito

Um operador de software torna-se estruturalmente acoplado ao sistema operado quando sua implementação pressupõe:

- uma identidade específica de projeto;
- nomes fixos de manifestos;
- diretórios e serviços conhecidos antecipadamente;
- variáveis de ambiente próprias do sistema observado;
- targets ou capacidades compilados no núcleo;
- uma única raiz possível de interpretação.

Nesse desenho, a identidade do operador, a raiz de sua implementação e o objeto observado tendem a ser confundidos:

```text
contexto do operador
    =
repositório do operador
    =
sistema operado
```

O acoplamento pode permanecer invisível enquanto existe um único sistema. Ele se torna arquiteturalmente relevante quando o mesmo operador precisa trabalhar com outros projetos ou consigo próprio.

A orientação a *workspace* introduz outra relação:

```text
HOA
  ↓ recebe
Workspace
  ↓ declara
Projeto
  ↓ publica
Manifesto, targets, skills, políticas e capacidades
  ↓
Operação governada
```

A pasta indicada deixa de ser apenas um caminho. Ela representa uma fronteira de contexto, interpretação, confinamento e autoridade.

---

## 3. Inversão de contexto operacional

Chamamos de **inversão de contexto operacional** a passagem de um operador que pressupõe internamente seu objeto para um operador cujo objeto é fornecido externamente e interpretado por contratos.

Antes:

```text
HOA
└── conhece antecipadamente o SisTer
```

Depois:

```text
HOA
└── conhece o conceito de Workspace
    └── o Workspace declara o projeto
```

Essa inversão se relaciona ao princípio de ocultação de informação de Parnas. Uma decomposição modular adequada deve isolar decisões suscetíveis a mudança, em vez de organizar o sistema apenas pela sequência de processamento. Identidade, disposição de arquivos, comandos operacionais, targets e políticas pertencem à variabilidade do projeto observado. Quando permanecem no núcleo, a variabilidade externa converte-se em acoplamento interno.

O `ProjectWorkspace` deve encapsular, no mínimo:

- raiz canônica;
- origem da seleção;
- manifesto encontrado;
- resolução segura de caminhos;
- limites de leitura e escrita;
- targets publicados;
- skills disponíveis;
- políticas aplicáveis.

O princípio resultante é:

> **O HOA não conhece antecipadamente o sistema. O HOA conhece um workspace capaz de declarar um sistema.**

---

## 4. Mudança arquitetural como revisão de teoria

Na perspectiva de Peter Naur, programar envolve a construção de uma teoria sobre o problema, o sistema e a relação entre ambos. O código é uma expressão dessa teoria, mas não a substitui.

A passagem para um HOA orientado a *workspace* altera a teoria organizadora do projeto:

```text
Teoria anterior:
O HOA é o operador do ecossistema SisTer.
```

```text
Teoria proposta:
O HOA é um operador governado de projetos
publicados por workspaces.
```

Por isso, uma mudança arquitetural relevante precisa explicitar:

- qual teoria anterior está sendo substituída;
- qual nova compreensão passa a organizar o sistema;
- quais decisões materializam essa compreensão;
- quais estados intermediários continuam válidos;
- como será demonstrado que a mudança atingiu seu objetivo.

A RFC registra a transformação maior. ADRs registram decisões arquiteturais delimitadas. Os patches materializam essas decisões no código. Testes e verificações confrontam as alegações. Evidências registram o ocorrido.

```text
Teoria
  ↓
RFC
  ↓
ADRs
  ↓
Série de patches
  ↓
Verificação
  ↓
Evidência
```

---

## 5. Reflexividade e prática reflexiva

Donald Schön descreve o projeto como uma conversação reflexiva com os materiais. Uma ação produz consequências; as consequências revelam propriedades não antecipadas; e o projetista reenquadra tanto o problema quanto a próxima ação.

Foi esse movimento que ocorreu no HOA:

```text
Pergunta inicial:
Como adicionar --project?

Reenquadramento:
Como o HOA representa, executa e verifica
uma transformação arquitetural?
```

Na reflexão computacional, um sistema mantém representações de aspectos de sua própria estrutura ou execução e pode operar sobre essas representações. Para o HOA, contudo, a capacidade reflexiva não basta. Ela precisa permanecer governada.

Podem ser distinguidos quatro níveis:

1. **Reflexividade estrutural:** leitura de manifestos, políticas, targets, skills e contratos.
2. **Reflexividade operacional:** observação de builds, testes, processos, endpoints, logs e alterações.
3. **Reflexividade causal:** capacidade de modificar o projeto observado.
4. **Reflexividade governada:** modificação causal condicionada por autoridade, escopo, risco, reversibilidade, verificação e evidência.

O objetivo não é um sistema que se altera livremente. É um sistema capaz de participar de sua transformação sem dissolver as distinções entre proposta, execução, verificação e autorização.

---

## 6. Transformação Governada

**Transformação Governada** é a unidade conceitual que relaciona intenção, mudança, autoridade, verificação e resultado.

Pode ser representada por:

```text
TG = ⟨O, C₀, R, P, A, V, E, H, C₁⟩
```

onde:

- `O` — objetivo declarado;
- `C₀` — contexto inicial observado;
- `R` — racional ou teoria da mudança;
- `P` — série ordenada de patches ou operações;
- `A` — política de autoridade;
- `V` — verificações;
- `E` — evidências e proveniência;
- `H` — decisões humanas requeridas;
- `C₁` — contexto resultante verificado.

Um patch é uma unidade de alteração. Uma transformação governada é a composição:

```text
intenção
+ alteração
+ legitimidade
+ verificação
+ evidência
+ recebimento
```

### 6.1 Invariantes

Toda Transformação Governada deve buscar os seguintes invariantes:

1. **Confinamento:** operações comuns permanecem no *workspace* selecionado.
2. **Atomicidade lógica:** cada patch expressa uma mudança compreensível.
3. **Validade intermediária:** os estados previstos da série permanecem compiláveis e testáveis.
4. **Verificação determinística:** a aceitação não depende apenas de julgamento textual da LLM.
5. **Separação de autoridade:** propor, executar, verificar e aprovar são responsabilidades distinguíveis.
6. **Proveniência:** entradas, comandos, saídas, hashes, atores e resultados podem ser reconstruídos.
7. **Reversibilidade declarada:** o retorno é definido ou a irreversibilidade é tratada como risco reforçado.
8. **Ausência de mutação oculta:** alterações relevantes aparecem no plano e no recibo.
9. **Correspondência objetivo–resultado:** o estado final é comparado com critérios definidos antes da execução.

---

## 7. Série de Refatoração Arquitetural

A **Série de Refatoração Arquitetural** é a materialização incremental de uma Transformação Governada no código.

A disciplina de patches do kernel Linux oferece um antecedente importante: mudanças logicamente distintas devem ser separadas, explicáveis e válidas em seus estados intermediários. O HOA amplia essa disciplina ao relacionar cada série com racional, autoridade, verificações e evidências.

Estrutura conceitual:

```text
series/
└── HOA-RFC-0001/
    ├── series.yaml
    ├── rationale.md
    ├── 0001-introduce-project-workspace.patch
    ├── 0002-add-project-manifest.patch
    ├── 0003-separate-hoa-root.patch
    ├── ...
    ├── verification.yaml
    └── expected-state.yaml
```

A série constitui um **argumento executável de transformação**:

```text
rationale.md
    → explica por que mudar

patches
    → demonstram como a mudança foi decomposta

verification.yaml
    → define como as alegações serão confrontadas

evidence/
    → registra o que efetivamente aconteceu

receipt
    → relaciona intenção, execução e resultado
```

A série não é apenas uma forma conveniente de transportar diffs. Sua ordem e granularidade expressam dependências conceituais e tornam a teoria da mudança tecnicamente examinável.

---

## 8. Verificação, assurance e proveniência

Uma transformação gerada ou auxiliada por LLM não se torna confiável por estar acompanhada de uma justificativa convincente. A confiança deve decorrer de evidências independentes e verificáveis.

O HOA aproxima-se, nesse aspecto, de três tradições:

- **assurance cases:** alegações sustentadas por argumentos e evidências;
- **in-toto:** encadeamento verificável de etapas, atores, comandos e artefatos;
- **SLSA:** proveniência de artefatos e verificabilidade da cadeia de produção.

O HOA não precisa adotar integralmente esses padrões em sua primeira implementação. Deve preservar, entretanto, sua disciplina fundamental:

> **Nenhuma transformação deve depender somente da confiança narrativa no executor.**

Uma verificação adequada pode incluir:

- correspondência da baseline Git;
- `git apply --check`;
- configuração e compilação;
- testes unitários e de integração;
- verificação de políticas;
- inspeção do diff;
- confinamento dos caminhos alterados;
- pós-condições específicas da mudança;
- registro de hashes e resultados.

---

## 9. Ciclo cibernético

A Transformação Governada possui afinidade com o ciclo MAPE-K da computação autonômica, mas acrescenta explicitamente autoridade humana, verificação, evidência e recebimento.

```text
Objetivo
  ↓
Observação do contexto
  ↓
Análise
  ↓
Plano e série
  ↓
Avaliação de autoridade
  ↓
Aplicação
  ↓
Verificação
  ↓
Evidência
  ↓
Recebimento humano
  ↓
Atualização do conhecimento
```

O ciclo é cibernético porque compara estados, seleciona ações e usa seus efeitos como realimentação. Contudo, a capacidade de executar não equivale à autoridade para decidir. A distinção entre operação, inteligência e política, presente na cibernética organizacional de Stafford Beer, é particularmente importante para o HOA.

Uma transformação bem-sucedida produz dois resultados:

1. uma alteração válida no sistema;
2. conhecimento verificável sobre como e por que essa alteração ocorreu.

O segundo resultado permite aprendizagem institucional sem depender de uma memória opaca da LLM.

---

## 10. Distribuição de agência

A automação pode atuar em diferentes etapas: aquisição de informação, análise, seleção de decisão e implementação da ação. O nível de automação deve ser uma decisão arquitetural e sociotécnica, não uma consequência automática da disponibilidade tecnológica.

### 10.1 LLM — agência propositiva e interpretativa

A LLM pode:

- interpretar objetivos;
- formular hipóteses;
- propor decomposições;
- redigir racional e documentação;
- identificar alternativas e riscos;
- explicar resultados.

A LLM não é a fonte final de verdade operacional.

### 10.2 HOA — agência processual e verificadora

O HOA pode:

- delimitar o *workspace*;
- validar contratos;
- aplicar patches autorizados;
- executar builds e testes;
- coletar evidências;
- bloquear violações de política;
- produzir recibos auditáveis.

O HOA não possui autoridade normativa ilimitada.

### 10.3 Humano — agência normativa e autoridade

O humano:

- define ou aceita objetivos;
- aprova mudanças conforme risco;
- decide conflitos de valor;
- aceita, rejeita ou solicita revisão;
- autoriza promoções de maior consequência;
- responde institucionalmente pela decisão.

O desenho resultante é de **autonomia assistiva com autoridade graduada**.

---

## 11. O HOA como sistema sociotécnico

O sistema operacional real não é apenas o executável HOA:

```text
LLM
+ HOA
+ repositório
+ ferramentas
+ políticas
+ humano
+ instituição
```

Uma série de patches é simultaneamente:

- objeto técnico;
- proposta de mudança;
- meio de comunicação;
- unidade de revisão;
- registro de responsabilidade;
- evidência de trabalho;
- instrumento de coordenação.

A autoridade precisa, portanto, integrar o modelo de domínio. A pergunta não é apenas “a ferramenta consegue executar?”, mas:

```text
Quem pode autorizar?
Em qual contexto?
Com quais evidências?
Sob quais condições de reversão?
Quem recebe o resultado?
```

A Transformação Governada é um processo sociotécnico mesmo quando sua execução é amplamente automatizada.

---

## 12. Autoaplicação e reflexividade delimitada

Quando o HOA puder receber o próprio repositório como *workspace*, interpretar uma RFC, validar sua série, aplicar patches, executar verificações e produzir recibos, ocorrerá uma forma limitada de autoaplicação.

Isso não equivale a autonomia geral. O HOA não define sozinho seus fins, sua legitimidade ou suas políticas fundamentais. Ele aplica sobre si o mesmo protocolo que aplica a outros projetos.

Essa propriedade é denominada:

> **reflexividade operacional sob autoridade delimitada**

Ela funciona como:

- teste de generalidade;
- teste de coerência;
- teste de governança.

O instrumento participa da transformação do próprio instrumento, mas continua submetido a contratos externos de autoridade.

---

## 13. Modelo de domínio preliminar

Entidades iniciais:

```text
ProjectWorkspace
ProjectManifest
TransformationSeries
PatchUnit
VerificationPlan
AuthorityDecision
EvidenceRecord
ExecutionReceipt
```

Estados possíveis de uma série:

```text
draft
  → proposed
  → reviewed
  → approved
  → applying
  → verified
  → committed
  → received
```

Estados alternativos:

```text
rejected
blocked
failed
rolled_back
superseded
```

`committed` significa que a alteração foi registrada no repositório. `received` significa que a autoridade humana reconheceu formalmente o resultado da transformação.

---

## 14. Proposições para pesquisa e desenvolvimento

### P1 — A mudança arquitetural pode ser objeto de domínio

Refatorações relevantes podem tornar-se entidades identificáveis, versionadas, verificadas e recebidas.

### P2 — Uma série de patches pode representar uma teoria operacional de mudança

A ordem e a granularidade dos patches expressam dependências conceituais, e não apenas textuais.

### P3 — A série pode funcionar como argumento executável

A alegação arquitetural é ligada a operações e verificações executáveis contra um contexto concreto.

### P4 — A proveniência pode converter automação generativa em engenharia auditável

A LLM propõe; a confiança decorre das verificações e evidências produzidas pelo HOA.

### P5 — A autoridade é uma dimensão arquitetural

Permissão, aprovação, responsabilidade e recebimento fazem parte do modelo de execução.

### P6 — A autoaplicação é um teste forte de generalidade

Um HOA orientado a *workspace* deve operar seu próprio repositório sem caminhos privilegiados.

### P7 — O conhecimento específico deve residir prioritariamente no projeto

Manifestos, targets, skills e políticas particulares são publicados pelo *workspace*. O núcleo preserva conceitos e mecanismos genéricos.

### P8 — O procedimento confiável deve preceder sua automação

Primeiro definem-se estados, invariantes, evidências e autoridade. Depois o HOA recebe capacidade de executar o processo.

---

## 15. Síntese

A contribuição central não é um argumento de CLI. É uma nova unidade de engenharia:

```text
objetivo
+ teoria da mudança
+ série ordenada
+ autoridade
+ verificação
+ evidência
+ recebimento
```

Nesse desenho:

```text
LLM
    amplia formulação e decomposição

HOA
    transforma propostas em processos verificáveis

Humano
    preserva autoridade normativa
```

O sistema torna-se reflexivo sem se tornar soberano, adaptativo sem se tornar opaco e automatizado sem eliminar responsabilidade.

---

## Referências

BEER, Stafford. The Viable System Model: Its Provenance, Development, Methodology and Pathology. *Journal of the Operational Research Society*, v. 35, n. 1, p. 7–25, 1984. DOI: 10.1057/jors.1984.2.

BLAIR, Gordon S.; BENCOMO, Nelly; FRANCE, Robert B. Models@run.time. *Computer*, v. 42, n. 10, p. 22–27, 2009. DOI: 10.1109/MC.2009.326.

CHERNS, Albert. The Principles of Sociotechnical Design. *Human Relations*, v. 29, n. 8, p. 783–792, 1976. DOI: 10.1177/001872677602900806.

KEPHART, Jeffrey O.; CHESS, David M. The Vision of Autonomic Computing. *Computer*, v. 36, n. 1, p. 41–50, 2003. DOI: 10.1109/MC.2003.1160055.

MAES, Pattie. Concepts and Experiments in Computational Reflection. *ACM SIGPLAN Notices*, v. 22, n. 12, p. 147–155, 1987. DOI: 10.1145/38807.38821.

MUMFORD, Enid. The Story of Socio-Technical Design: Reflections on Its Successes, Failures and Potential. *Information Systems Journal*, v. 16, n. 4, p. 317–342, 2006. DOI: 10.1111/j.1365-2575.2006.00221.x.

NAUR, Peter. Programming as Theory Building. *Microprocessing and Microprogramming*, v. 15, n. 5, p. 253–261, 1985. DOI: 10.1016/0165-6074(85)90032-8.

NYGARD, Michael. Documenting Architecture Decisions. Cognitect, 2011.

PARASURAMAN, Raja; SHERIDAN, Thomas B.; WICKENS, Christopher D. A Model for Types and Levels of Human Interaction with Automation. *IEEE Transactions on Systems, Man, and Cybernetics – Part A*, v. 30, n. 3, p. 286–297, 2000. DOI: 10.1109/3468.844354.

PARNAS, David L. On the Criteria to Be Used in Decomposing Systems into Modules. *Communications of the ACM*, v. 15, n. 12, p. 1053–1058, 1972. DOI: 10.1145/361598.361623.

SCHÖN, Donald A. *The Reflective Practitioner: How Professionals Think in Action*. New York: Basic Books, 1983.

SMITH, Brian Cantwell. *Reflection and Semantics in a Procedural Language*. Tese de doutorado — Massachusetts Institute of Technology, 1982.

TRIST, Eric L.; BAMFORTH, Ken W. Some Social and Psychological Consequences of the Longwall Method of Coal-Getting. *Human Relations*, v. 4, n. 1, p. 3–38, 1951. DOI: 10.1177/001872675100400101.

IN-TOTO. *A framework to secure the integrity of software supply chains*.

SLSA. *Supply-chain Levels for Software Artifacts — Specification v1.2*.

THE LINUX KERNEL DOCUMENTATION. *Submitting patches: the essential guide to getting your code into the kernel*.
