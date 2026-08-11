# Praxis

**Harness Operacional Assistido do ecossistema SisTer**

[![C++23](https://img.shields.io/badge/C%2B%2B-23-00599C)](#requisitos)
[![Harness](https://img.shields.io/badge/Harness-H1-13B8A6)](#estado-atual)
[![Governança](https://img.shields.io/badge/Governan%C3%A7a-READY-22C55E)](#governança)
[![Licença](https://img.shields.io/badge/licen%C3%A7a-GPL--3.0--only-8B5CF6)](LICENSE)

**Praxis** é um instrumento geral de experimentação governada sobre workspaces. Implementa um **Governed Operational Harness (HOA)** para observar, planejar e, progressivamente, transformar sistemas sob contratos explícitos, autoridade limitada, verificação e evidências.

Ele não trata automação como uma sequência livre de comandos. Cada capacidade deve pertencer ao ciclo:

```text
observar → interpretar → planejar → autorizar → executar → verificar → registrar → aprender
```

No estágio atual, o HOA observa alvos externos e produz planos governados, mas **não executa ações externas**.

## Estado atual

```text
versão                 0.4.1
implementação          C++23 nativo
fase do Harness        H1
baseline de governança READY
alvos externos         3
agentes                 2
skills                  9
execução externa        DISABLED
planejamento externo    ENABLED
painel web              READ_ONLY
LLM                     DISABLED
```

## Visão arquitetural

```text
                         Praxis

                         CLI C++23
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
 Autodiagnóstico       Observação externa      Action planning
       │                      │                      │
       └──────────────────────┼──────────────────────┘
                              │
                         Harness Core
                              │
        ┌─────────────┬───────┼────────┬─────────────┐
        │             │       │        │             │
      Agents        Skills  Policies Targets      Evidence
                              │
                  ┌───────────┼────────────┐
                  │           │            │
                SisTer    SisTer Nexo    Gateway
```

O dashboard é apenas uma projeção observacional desse núcleo. Ele não possui autoridade de controle.

## Início rápido

### Construir e testar

```bash
./scripts/run_quality.sh
```

### Descobrir a CLI

```bash
./sister-ops --help
./sister-ops help dashboard
```

### Diagnosticar o próprio Praxis

```bash
./sister-ops status
./sister-ops health
./sister-ops doctor
./sister-ops governance check
```

### Observar o ecossistema

```bash
./sister-ops target catalog
./sister-ops target inspect sister
./sister-ops target inspect sister-nexo
./sister-ops ecosystem status
./sister-ops ecosystem health
```

### Planejar uma ação externa

```bash
./sister-ops action catalog

./sister-ops action plan \
  project.build \
  --target sister
```

O plano será salvo no estado local governado do Praxis com o estado:

```text
PLANNED_NOT_EXECUTED
```

No H1, `action apply` é deliberadamente recusado.

## CLI

### Autodiagnóstico

| Comando | Função | Risco |
|---|---|---|
| `status` | Identidade, versão e fase do Harness | `read` |
| `health` | Resumo do núcleo e da governança | `read` |
| `doctor` | Diagnóstico detalhado do repositório | `read` |
| `governance check` | Validação da baseline governada | `read` |

### Observação externa

| Comando | Função | Autoridade |
|---|---|---|
| `target catalog` | Lista alvos registrados e estado observável | somente leitura |
| `target inspect <id>` | Inspeciona um alvo específico | somente leitura |
| `ecosystem status` | Resume o estado do ecossistema | somente leitura |
| `ecosystem health` | Classifica a saúde externa | somente leitura |

### Planejamento de ações

| Comando | Função | Estado |
|---|---|---|
| `action catalog` | Lista ações conhecidas | consulta |
| `action plan <op> --target <id>` | Produz plano governado | habilitado |
| `action apply` | Executaria um plano autorizado | desabilitado no H1 |

Ações atualmente registradas:

```text
project.build
project.test
service.restart
```

### Dashboard

```bash
./sister-ops dashboard snapshot
./sister-ops dashboard serve --port 8090
```

Acesse:

```text
http://127.0.0.1:8090
```

O servidor aceita somente `GET` e `HEAD`. Métodos mutáveis retornam `405 Method Not Allowed`.

## Targets

Os alvos externos vivem em `config/targets/`:

```text
config/targets/
├── sister.target
├── sister-nexo.target
└── sister-gateway.target
```

Exemplo:

```ini
id=sister
name=SisTer
kind=orchestrator
repository=~/dev/cpp/SisTer
host=127.0.0.1
port=8000
observations=filesystem,tcp
actions=project.build,project.test
```

A definição do alvo estabelece simultaneamente:

- onde observar;
- quais adapters usar;
- quais ações podem ser planejadas;
- qual é a fronteira de autoridade.

Registrar uma ação no HOA não concede automaticamente autoridade sobre todos os alvos.

## Governança

A governança do próprio repositório é materializada por:

```text
project.sister.yaml
CONTRIBUTING.md
.github/CODEOWNERS
.github/pull_request_template.md
.github/workflows/ci.yml
policies/
contracts/
docs/adr/
docs/architecture/
docs/dai/
harness/
mcp/contracts/
```

O validador é executado por:

```bash
python3 scripts/validate_governance_repo.py
```

E integra o quality gate:

```bash
./scripts/run_quality.sh
```

## Harness

### Agentes

```text
diagnostic-agent
ecosystem-operator
```

### Skills

```text
ecosystem.status
ecosystem.health
ecosystem.doctor
dashboard.observe
target.catalog
target.inspect
ecosystem.observe
action.catalog
action.plan
```

### Contratos

```text
contracts/operations/agent.schema.json
contracts/operations/skill.schema.json
contracts/operations/operation-plan.schema.json
contracts/operations/execution-receipt.schema.json
contracts/targets/target.schema.json
```

### Evidências e cenários

```text
harness/evidence/
harness/reports/
harness/scenarios/
```

## Fronteira de segurança

No estágio H1:

- LLM não executa operações;
- ações externas não são aplicadas;
- planos exigem alvo e operação allowlisted;
- o dashboard não recebe autoridade;
- endpoints e caminhos vêm do registro de targets;
- nenhuma URL ou comando livre deve ser produzido por modelo;
- publicação e destruição permanecem desabilitadas.

A relação de autoridade é:

```text
skill permitida
+ agente autorizado
+ alvo registrado
+ ação allowlisted no alvo
+ risco admitido
+ autorização válida
= operação elegível
```

No H1, a última condição ainda não habilita execução.

## Organização do código

```text
apps/sister-ops/                 entrada da CLI
include/sister/hoa/              contratos C++ públicos
src/cli/                         roteamento e apresentação
src/core/                        governança e registros
src/targets/                     carregamento dos alvos
src/observation/                 observações externas
src/action/                      produção de planos
src/dashboard/                   snapshot e HTTP read-only
config/targets/                  alvos externos
contracts/                       schemas
harness/                         agentes, skills e memória
policies/                        fronteiras de autoridade
web/                             painel observacional
tests/                           CTest
legacy/python-project-forge/     protótipo preservado
```

## Requisitos

- Linux;
- CMake 3.25 ou superior;
- compilador compatível com C++23;
- Ninja ou Make;
- Python 3 para os validadores de governança;
- Git.

## Desenvolvimento

```bash
./scripts/configure.sh
./scripts/build.sh
./scripts/test.sh
```

Antes de um commit:

```bash
git diff --check
./scripts/run_quality.sh
git status --short
```

## Roadmap

```text
H0  Bootstrap governado e autodiagnóstico                         READY
H1  Observação externa e action planning                         READY
H2  Execução externa autorizada, verificável e reversível        NEXT
H3  Assistência local por LLM em modo plan-only                  PLANNED
H4  Governança distribuída entre subsistemas                     RESEARCH
```

O próximo marco H2 deve introduzir:

- `action apply` com confirmação explícita;
- executores determinísticos;
- captura do estado inicial;
- pós-condições;
- rollback quando aplicável;
- recibo e evidência;
- ações inicialmente pequenas e reversíveis.

## Licença

Distribuído sob a **GNU General Public License version 3 only**:

```text
SPDX-License-Identifier: GPL-3.0-only
```

Consulte [LICENSE](LICENSE).

## Princípio orientador

> O assistente pode propor.<br>
> O plano deve explicitar.<br>
> A autoridade deve autorizar.<br>
> O executor deve obedecer.<br>
> O sistema deve verificar.<br>
> A evidência deve permanecer.
