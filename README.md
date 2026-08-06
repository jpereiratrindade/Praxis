# SisTer-HOA

<!-- NATIVE_CPP23_STATUS -->

> [!IMPORTANT]
> O núcleo oficial do SisTer-HOA é agora o executável nativo C++23 `sister-ops`.
> A implementação Python inicial foi preservada em `legacy/python-project-forge/`
> apenas como referência durante a migração incremental da Forja. O estágio atual
> é H0: `status`, `health`, `doctor`, contratos, agentes, skills, políticas e
> verificação da governança — sem LLM e sem operações mutáveis.


**Harness Operacional Assistido do ecossistema SisTer**

O **SisTer-HOA** é uma infraestrutura local para planejar, autorizar, executar, verificar e registrar operações de engenharia de software de forma governada.

Seu objetivo não é apenas automatizar comandos. O sistema procura garantir que cada operação possua:

- intenção explícita;
- plano inspecionável;
- avaliação de risco;
- autorização antes da mutação;
- execução determinística;
- pré-condições e pós-condições;
- evidências;
- recibos de execução;
- possibilidade de auditoria.

O primeiro incremento funcional do SisTer-HOA é a **Forja de Projetos Governados**, disponibilizada pela CLI `sister-ops`.

---

## Estado atual

Versão atual:

```text
sister-ops 0.1.1
```

Estado do projeto:

```text
MVP funcional
```

O MVP já permite:

- consultar o catálogo de blueprints;
- planejar a criação de projetos;
- revisar o destino e os arquivos previstos;
- autorizar explicitamente a execução;
- gerar projetos C++ ou Python;
- criar estruturas compatíveis com o padrão Harness;
- executar build e testes;
- verificar contratos e estruturas;
- registrar evidências e recibos;
- inspecionar projetos já materializados;
- impedir sobrescrita de diretórios existentes.

O seguinte ciclo foi validado experimentalmente:

```text
blueprint
    ↓
plano
    ↓
autorização
    ↓
materialização
    ↓
build e testes
    ↓
verificação
    ↓
evidência e recibo
```

Resultado obtido nos ensaios C++ e Python:

```text
HARNESS_READY
```

---

## Motivação

Geradores tradicionais de projetos normalmente criam diretórios, arquivos iniciais e configurações de build.

O SisTer-HOA acrescenta uma dimensão operacional:

> não basta gerar um projeto; é necessário tornar observável, autorizável e verificável o processo pelo qual ele foi gerado.

A Forja foi inspirada na experiência do **LabGestão**, mas diferencia:

- o repositório governado;
- a operação governada que cria o repositório;
- os contratos da execução;
- as evidências produzidas;
- a autoridade responsável por autorizar a ação.

O Harness não é tratado como uma nova linguagem ou uma categoria rígida de projeto. Ele é um perfil operacional que pode ser aplicado a diferentes combinações de linguagem, forma e papel.

---

## Project Blueprint

Um projeto é descrito por dimensões independentes:

```yaml
name: sister-agent
language: cpp
shape: cli
governance: harness
role: assistant
```

Dimensões atualmente reconhecidas:

### Linguagem

```text
cpp
python
```

### Forma

```text
cli
```

### Governança

```text
harness
```

### Papel

```text
standalone
subsystem
assistant
adapter
```

A estrutura foi desenhada para futuramente aceitar outras formas e perfis sem criar uma enumeração crescente de tipos como `C++ Harness Web`, `Python Governado Service` e outras combinações rígidas.

---

## Requisitos

Para utilizar a CLI:

- Linux;
- Bash;
- Python 3;
- Git.

Para gerar e verificar projetos C++:

- CMake;
- compilador com suporte ao padrão configurado pelo blueprint;
- CTest.

No Fedora Silverblue, o diretório pessoal pode aparecer fisicamente como:

```text
/var/home/<usuario>
```

Isso é esperado. A variável `$HOME` continua sendo a forma recomendada de referenciar o diretório pessoal.

---

## Instalação

Clone o repositório:

```bash
git clone git@github.com:jpereiratrindade/SisTer-HOA.git
cd SisTer-HOA
```

Confira a CLI:

```bash
./sister-ops --version
```

Saída esperada:

```text
sister-ops 0.1.1
```

Consulte o catálogo:

```bash
./sister-ops project catalog
```

Saída esperada:

```text
Blueprints disponíveis no MVP:

  cpp-cli-harness      language=cpp shape=cli governance=harness
  python-cli-harness   language=python shape=cli governance=harness

Papéis combináveis: standalone, subsystem, assistant, adapter
```

---

## Uso da Forja

### 1. Planejar um projeto C++

Crie o diretório que receberá os projetos:

```bash
mkdir -p "$HOME/dev/cpp"
```

Produza o plano:

```bash
./sister-ops project plan \
  --name sister-agent \
  --language cpp \
  --shape cli \
  --governance harness \
  --role assistant \
  --target "$HOME/dev/cpp"
```

O comando `plan` não cria o projeto.

Ele grava um plano em:

```text
.sister-hoa/plans/
```

Exemplo de resultado:

```text
Plano: plan-project-20260806-173054-4a86c2
Operação: project.create
Risco: mutate_local

Projeto: sister-agent
Blueprint: cpp-cli-harness + role=assistant
Destino: /var/home/usuario/dev/cpp/sister-agent

Arquivos previstos: 31
Nenhum arquivo do projeto foi criado.
```

### 2. Consultar o plano

Liste os planos:

```bash
ls -lah .sister-hoa/plans/
```

Visualize um plano:

```bash
python3 -m json.tool \
  .sister-hoa/plans/plan-project-IDENTIFICADOR.json |
  less
```

### 3. Aplicar o plano

```bash
./sister-ops project apply \
  plan-project-IDENTIFICADOR
```

Antes de executar, a CLI apresenta:

- destino;
- quantidade de arquivos;
- existência ou não do diretório;
- confirmação de que arquivos externos não serão sobrescritos;
- solicitação explícita de autorização.

Exemplo:

```text
Criar 31 arquivos em:

/var/home/usuario/dev/cpp/sister-agent

O diretório ainda não existe.
Nenhum arquivo externo será sobrescrito.

Aplicar plano? [y/N]
```

Após a confirmação, a Forja:

1. cria o projeto em área temporária;
2. valida a materialização;
3. promove o diretório;
4. configura o build;
5. compila;
6. executa os testes;
7. verifica contratos e estruturas;
8. registra a evidência;
9. emite o recibo.

### 4. Verificar o projeto

```bash
./sister-ops project verify \
  "$HOME/dev/cpp/sister-agent"
```

Resultado esperado:

```text
Project Blueprint        PASS
Linguagem detectada      PASS
Estrutura esperada       PASS
Contratos JSON           PASS
Agentes registrados      PASS
Skills registradas       PASS
Configuração CMake       PASS
Build                    PASS
Testes                   PASS

Resultado: HARNESS_READY
```

Para verificar somente a estrutura:

```bash
./sister-ops project verify \
  "$HOME/dev/cpp/sister-agent" \
  --structure-only
```

### 5. Inspecionar o projeto

```bash
./sister-ops project inspect \
  "$HOME/dev/cpp/sister-agent"
```

Exemplo:

```text
Projeto: /var/home/usuario/dev/cpp/sister-agent
Linguagem: cpp
Forma: cli
Governança: harness
Papel: assistant
Harness: materializado
```

---

## Projeto Python

Crie o destino:

```bash
mkdir -p "$HOME/dev/python"
```

Planeje:

```bash
./sister-ops project plan \
  --name campo-observations \
  --language python \
  --shape cli \
  --governance harness \
  --role subsystem \
  --target "$HOME/dev/python"
```

Aplique:

```bash
./sister-ops project apply \
  plan-project-IDENTIFICADOR
```

Verifique:

```bash
./sister-ops project verify \
  "$HOME/dev/python/campo-observations"
```

A verificação Python inclui:

- compilação dos módulos;
- execução de testes;
- validação dos contratos;
- validação da estrutura Harness.

---

## Estrutura de um projeto Harness

Um projeto C++ criado pela Forja possui uma estrutura semelhante a:

```text
project-name/
├── project.sister.yaml
├── CMakeLists.txt
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── main.cpp
├── include/
├── tests/
├── contracts/
│   ├── project-blueprint.schema.json
│   └── operations/
│       ├── agent.schema.json
│       ├── skill.schema.json
│       ├── operation-plan.schema.json
│       └── execution-receipt.schema.json
├── harness/
│   ├── agents/
│   ├── skills/
│   ├── plans/
│   ├── scenarios/
│   ├── evidence/
│   └── reports/
├── policies/
│   ├── risk-policy.yaml
│   ├── approval-matrix.yaml
│   └── context-boundary.md
├── docs/
│   ├── adr/
│   └── architecture/
├── scripts/
│   ├── configure.sh
│   ├── build.sh
│   ├── test.sh
│   └── run_quality.sh
└── .github/
    └── workflows/
        └── ci.yml
```

---

## Contratos operacionais

O MVP inclui contratos para:

- Project Blueprint;
- agentes;
- skills;
- planos de operação;
- recibos de execução.

As três skills iniciais são:

```text
project.create@0.1.0
project.inspect@0.1.0
project.verify@0.1.0
```

Essas skills descrevem operações permitidas pelo Harness. Elas não representam comandos livres produzidos por um modelo de linguagem.

---

## Segurança operacional

O MVP adota as seguintes restrições:

- não utiliza `eval`;
- não utiliza `shell=True`;
- não executa texto arbitrário como comando;
- utiliza executável e vetor de argumentos;
- exige autorização antes de ações mutáveis;
- recusa criar projetos em diretórios já existentes;
- não sobrescreve automaticamente projetos;
- separa planejamento de execução;
- registra evidências após as operações;
- mantém planos e recibos locais fora do versionamento principal.

Uma segunda tentativa de aplicar um plano cujo destino já exista deve resultar em:

```text
ERRO: destino já existe; nada foi alterado
```

Esse comportamento é intencional.

---

## Estrutura do SisTer-HOA

```text
SisTer-HOA/
├── sister-ops
├── tools/
│   └── project_forge/
│       └── sister_ops.py
├── .sister-hoa/
│   ├── plans/
│   └── receipts/
├── .gitignore
├── LICENSE
└── README.md
```

O diretório `.sister-hoa/` armazena estado operacional local e não deve ser versionado.

---

## Relação com o LabGestão

A direção arquitetural pretendida é:

```text
LabGestão
    ↓
interface gráfica para criação e acompanhamento

SisTer-HOA / sister-ops
    ↓
interface CLI governada e assistida

project-forge-core
    ↓
núcleo compartilhado de blueprint, planejamento,
geração, validação e evidências
```

No MVP, a implementação da Forja ainda está concentrada em:

```text
tools/project_forge/sister_ops.py
```

Essa implementação serve como bootstrap verificável. A evolução prevista é extrair um núcleo reutilizável e reduzir o acoplamento entre interface, domínio e infraestrutura.

---

## Limitações do MVP

A versão `0.1.1` ainda não inclui:

- adoção de projetos existentes;
- atualização incremental de estruturas;
- interface web;
- integração com Ollama;
- interpretação de intenção por LLM;
- blueprints `basic` e `governed`;
- formas `service`, `library`, `web` e `hybrid`;
- execução distribuída;
- gestão de remotos Git;
- commit e push governados;
- núcleo definitivo em C++.

O comando `project adopt` ainda está planejado e não deve ser considerado disponível.

---

## Roadmap

### v0.1.x

- documentação completa;
- licença GPLv3;
- propagação explícita de licença para projetos gerados;
- testes automatizados da própria Forja;
- melhoria das mensagens de erro;
- validação dos manifests YAML.

### v0.2.0

- `project adopt`;
- inspeção de projetos LabGestão;
- plano de adoção não destrutivo;
- comparação entre estrutura atual e estrutura Harness;
- geração de patches e recibos de adoção.

### v0.3.0

- separação do `project-forge-core`;
- arquitetura interna modular;
- catálogo externo de blueprints;
- versionamento dos templates.

### v0.4.0

- servidor local;
- página web simples;
- consulta de planos, recibos e evidências;
- autorização pela interface web.

### Futuro

- integração com LLM local;
- tradução de intenção para Project Blueprint;
- recomendações assistidas;
- agentes e skills adicionais;
- operações Git governadas;
- gestão de infraestrutura do ecossistema SisTer.

---

## Inteligência artificial

A integração futura com LLM deverá respeitar a seguinte regra:

> o modelo pode interpretar, recomendar e propor; somente executores determinísticos e autorizados podem modificar o sistema.

Exemplo futuro:

```bash
sister-ops ask \
  "crie um assistente CLI em C++ governado para administrar o CampoNode"
```

A intenção seria convertida em um `ProjectBlueprint` validável.

O modelo não teria autorização para inventar e executar comandos arbitrários.

---

## Desenvolvimento

Verifique a sintaxe Python:

```bash
python3 -m py_compile \
  tools/project_forge/sister_ops.py
```

Consulte a versão:

```bash
./sister-ops --version
```

Consulte o catálogo:

```bash
./sister-ops project catalog
```

Antes de um commit:

```bash
git diff --check
git status --short
```

Os artefatos Python locais devem ser ignorados:

```gitignore
__pycache__/
*.py[cod]
```

---

## Repositórios

O projeto é mantido em dois remotos:

```text
GitHub: jpereiratrindade/SisTer-HOA
GitLab: jpereiratrindade/SisTer-HOA
```

O GitHub é utilizado como upstream principal da branch local:

```bash
git push origin main
```

O GitLab recebe o espelhamento:

```bash
git push gitlab main
```

---

## Licença

O SisTer-HOA é software livre, distribuído sob os termos da:

```text
GNU General Public License, version 3
SPDX-License-Identifier: GPL-3.0-only
```

Consulte o arquivo `LICENSE` para o texto completo da licença.

A GPLv3 garante, entre outros direitos, a liberdade de:

- executar o programa;
- estudar seu funcionamento;
- modificar o código;
- redistribuir cópias;
- distribuir versões modificadas sob os mesmos termos.

Projetos derivados ou distribuições que incorporem código do SisTer-HOA devem respeitar as condições da GPLv3.

A licença dos projetos criados pela Forja deverá ser declarada explicitamente no respectivo Project Blueprint. Até que essa dimensão seja implementada na CLI, o arquivo `LICENSE` dos projetos gerados deve ser conferido durante a revisão do plano e da materialização.

---

## Autoria

Desenvolvido no contexto do ecossistema **SisTer — Sistemas Sociotécnicos Governados**.

Copyright © 2026 José Pedro Trindade

---

## Princípio orientador

> O assistente pode propor.
> O plano deve explicitar.
> A autoridade deve autorizar.
> O executor deve obedecer.
> O sistema deve verificar.
> A evidência deve permanecer.
