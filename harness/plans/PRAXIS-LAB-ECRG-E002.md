# PRAXIS-LAB-ECRG-E002 — Minimal Governed Reconstruction

## Condição desta rodada

```text
status: proposed
execution: not authorized
implementation: absent by design
promotion: none
```

Este artefato contém somente o desenho experimental. Não constitui pacote de
reconstrução, protocolo executável, gate, evidência ou autorização para iniciar
E002.

## Pergunta experimental

> Qual é o menor conjunto governado de referências, conteúdos e metadados capaz
> de tornar ECRG-E001 reconstruível em um workspace independente, sem preservar
> integralmente a conversa e sem depender de caminhos absolutos externos?

## Origem da pergunta

E001 foi constituído e verificado no workspace originário. Uma reprodução
isolada confirmou que seu verificador depende da existência de inputs em
caminhos absolutos externos. O digest verifica a identidade de conteúdo
disponível, mas não preserva nem recupera esse conteúdo.

O resultado local de E001 permanece historicamente `SUPPORTED`. E002 investiga
somente a claim adicional de reconstrução independente e a composição mínima
capaz de sustentá-la.

## Hipótese

Um conjunto menor que a conversa e o ambiente completos pode ser suficiente se
preservar, para cada dependência material, conteúdo recuperável ou referência
governadamente resolvível, identidade verificável, baseline, procedimento de
verificação e a memória interpretativa mínima necessária para entender a claim.

## Unidade de análise

A unidade de análise é a reconstrução independente da constituição verificável
de `PRAXIS-LAB-ECRG-E001`, e não a reprodução palavra por palavra da conversa
que a antecedeu.

Reconstrução independente significa, para este desenho:

1. começar em workspace que não possua os caminhos externos do ambiente
   originário;
2. obter cada input material por fonte explicitamente declarada;
3. verificar a identidade dos conteúdos consumidos;
4. executar um protocolo declarado sem memória implícita da conversa;
5. produzir resultado e fronteira de prova auditáveis;
6. não depender de conteúdo, variável, cache ou mount originário não declarado.

Essa definição é operacional e específica ao experimento; não é uma definição
normativa de proveniência para todo o Praxis.

## Claims separadas

E002 deve avaliar separadamente:

- `C-RECONSTRUCTION`: ao menos uma composição delimitada permite reconstrução
  independente;
- `C-MINIMALITY`: a composição bem-sucedida não contém classes de elementos que
  possam ser removidas sem perda da reconstrução observada.

Um sucesso de reconstrução não implica, sozinho, que o conjunto seja mínimo.

## Elementos candidatos sob investigação

Os elementos abaixo são hipóteses de composição, não artefatos já aprovados:

| Classe candidata | Função a testar |
|---|---|
| manifestação de inputs | enumerar dependências materialmente necessárias |
| identidade verificável | confirmar os bytes efetivamente consumidos |
| conteúdo ou referência recuperável | disponibilizar cada dependência sem caminho originário |
| baseline do repositório | situar a árvore e o estado de partida |
| procedimento e dependências de execução | tornar a intervenção repetível |
| fronteira da claim | impedir que reconstrução local seja lida como promoção metodológica |
| memória interpretativa mínima | preservar decisões necessárias sem copiar a conversa completa |
| registro de autoridade | distinguir constituição, execução, verificação e promoção |

As classes `referência registrada`, `identidade verificável` e
`recuperabilidade governada` devem ser medidas como propriedades distinguíveis,
sem pressupor que formem uma escala universal.

## Condições experimentais candidatas

### C0 — Controle histórico

Cópia do repositório com as referências externas atuais, sem disponibilizar os
inputs nos caminhos absolutos originários.

Resultado previsto, não executado nesta rodada: falha de resolução de input.

### C1 — Identidade sem recuperação

Registro e digests disponíveis, mas sem conteúdo ou fonte recuperável.

Objetivo: testar se identidade declarada, isoladamente, é suficiente.

### C2 — Composição candidata

Conjunto explicitamente delimitado contendo apenas os elementos considerados
materialmente necessários para a reconstrução.

Objetivo: testar `C-RECONSTRUCTION` sem copiar ambiente ou conversa completos.

### C3 — Ablações

Partindo de uma composição que reconstrua E001, retirar uma classe candidata por
vez e repetir o protocolo no mesmo tipo de isolamento.

Objetivo: produzir evidência para `C-MINIMALITY`. Elementos cuja retirada não
altere o resultado não podem ser declarados necessários com base neste caso.

## Isolamento requerido para execução futura

Uma execução futura deverá usar workspace temporário ou sandbox no qual:

- os caminhos absolutos originários estejam ausentes;
- arquivos externos do host não sejam montados implicitamente;
- rede esteja desabilitada, salvo se uma fonte remota governada fizer parte da
  condição declarada;
- caches e variáveis locais não sejam herdados sem declaração;
- cada conteúdo consumido seja registrado;
- o workspace originário permaneça somente leitura ou totalmente inacessível.

O mecanismo concreto de isolamento será escolhido apenas na autorização de
execução. Este desenho não prescreve ferramenta específica.

## Procedimento futuro candidato

Se E002 for ativado por autorização própria:

1. declarar previamente a composição candidata e seus digests;
2. preparar o isolamento sem caminhos ou conteúdos originários implícitos;
3. materializar somente a condição experimental autorizada;
4. registrar todas as resoluções de input e conteúdos consumidos;
5. executar o protocolo de reconstrução;
6. classificar `C-RECONSTRUCTION`;
7. executar ablações controladas somente após uma reconstrução bem-sucedida;
8. classificar `C-MINIMALITY` separadamente;
9. preservar resultado negativo, parcial ou inconclusivo;
10. encerrar sem promover taxonomia ou regra normativa automaticamente.

Nenhuma dessas etapas foi executada nesta rodada.

## Observações e métricas requeridas

- inputs declarados, resolvidos, ausentes e consumidos;
- método de recuperação usado por input;
- correspondência entre digest esperado e observado;
- dependências implícitas descobertas durante a execução;
- resultado do protocolo e ponto exato de falha;
- elementos presentes em cada condição;
- efeito observado de cada ablação;
- quantidade de conteúdo conversacional preservado;
- diferenças entre workspace originário e independente;
- intervenções humanas necessárias para completar a reconstrução.

## Classificação dos resultados

### `SUPPORTED`

Para `C-RECONSTRUCTION`: uma composição delimitada conclui o protocolo no
isolamento e toda dependência consumida é declarada, recuperável e verificável.

Para `C-MINIMALITY`: além da reconstrução, as ablações sustentam a necessidade
das classes mantidas dentro da fronteira testada.

### `PARTIALLY_SUPPORTED`

A reconstrução funciona, mas ainda há dependência não governada, conteúdo
excessivo, intervenção manual não declarada ou evidência insuficiente de
minimalidade.

### `NOT_SUPPORTED`

As composições candidatas não reconstroem E001 sob o isolamento especificado,
sem que a falha possa ser atribuída a defeito do próprio protocolo experimental.

### `INCONCLUSIVE`

Problemas de ambiente, isolamento, disponibilidade ética/licencial dos inputs ou
instrumentação impedem atribuir o resultado à composição avaliada.

## Ameaças à validade

- confundir execução do verificador com reconstrução da compreensão original;
- declarar mínimo um conjunto apenas porque uma alternativa não foi tentada;
- introduzir no runner conhecimento implícito da conversa;
- deixar o workspace independente acessar arquivos do host sem registro;
- adaptar o verificador de modo que ele aceite a solução por construção;
- concluir uma taxonomia geral a partir de um único experimento;
- preservar conteúdo privado ou licenciado além do estritamente necessário.

## Critérios para futura ativação

Antes de `proposed -> active`, uma autorização separada deverá definir:

- composição inicial submetida ao teste;
- tratamento ético, privado e licencial dos inputs;
- mecanismo de isolamento;
- protocolo executável e seu verificador independente;
- caminhos de evidência operacional e governada;
- critérios de interrupção e descarte;
- autoridade para executar ablações;
- fronteira exata da claim de reconstrução.

Sem esses elementos, E002 permanece `proposed`.

## Artefatos deliberadamente ausentes

- pacote de inputs;
- cópia da conversa;
- script ou verificador de E002;
- evidência de execução;
- checksum de evidência inexistente;
- schema de proveniência;
- policy, gate normativo, Agent ou Skill;
- mudança no estado canônico;
- mudança nos documentos LaTeX.

## DOCUMENTATION_DELTA

### Documento ECRG v0.1.0 — mudança futura indicada

Há evidência suficiente para uma revisão documental futura, sem promoção
normativa, registrar que:

1. `PRAXIS-LAB-ECRG-E00x` é a sequência empírica do laboratório;
2. a numeração `ECRG-E001...E006` do programa prospectivo v0.1.0 é planejamento
   provisório e conflita com a sequência empírica agora constituída;
3. a revisão deve renumerar ou criar namespace explícito para o programa
   prospectivo, preservando a história dos IDs laboratoriais;
4. protocolos comportamentais experimentais devem usar `ECRG-OP01...09`,
   reservando `P-ECRG-*` para proposições do documento;
5. ECRG-F001 deve ser registrado como finding sustentado neste caso, sem ser
   convertido em princípio universal;
6. a distinção entre referência registrada, identidade verificável e
   recuperabilidade governada deve aparecer como MRE candidata a ser testada;
7. rastreabilidade até um experimento e reconstrução independente devem ser
   apresentadas como claims diferentes;
8. E002 deve aparecer como experimento empírico `proposed`, ainda não executado.

### Método Praxis v0.1.1 — mudança não sustentada nesta rodada

Não há evidência suficiente para alterar o contrato metodológico ou o documento
do Método Praxis nesta rodada. O caso é único, E002 não foi executado e a
distinção de proveniência permanece MRE candidata.

Além disso, M05 já exige referências mecanicamente resolvíveis quando possível,
e M06 já rejeita caminhos absolutos ou artefatos locais como prova exclusiva de
estado. ECRG-F001 é consistente com essas bases; ainda não demonstra lacuna que
exija nova regra, schema ou revisão do método.

Essa decisão deve ser reavaliada após evidência de E002 ou recorrência
independente do mesmo problema.
