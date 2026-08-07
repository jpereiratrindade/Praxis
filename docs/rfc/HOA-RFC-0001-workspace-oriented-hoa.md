# HOA-RFC-0001 — Workspace-Oriented HOA

## Estado

**Proposta**

## Data

2026-08-06

## Tipo

Transformação arquitetural governada.

## Relações

- Fundamentação: `docs/architecture/TRANSFORMACOES_GOVERNADAS.md`
- Baseline observada: SisTer-HOA `0.4.1`
- Commit de referência: `51f688c098be18fb9ebcba5410384562317a287c`
- ADRs relacionadas: ADR-0001, ADR-0002 e ADR-0003

---

## 1. Resumo

Esta RFC propõe transformar o SisTer-HOA de operador cujo contexto principal está implicitamente vinculado ao próprio repositório e ao ecossistema SisTer em operador governado orientado a *workspace*.

Após a transformação, o HOA receberá uma pasta de projeto, descobrirá seu manifesto e seus recursos locais, delimitará sua autoridade a essa raiz e executará comandos de observação ou planejamento sobre o projeto selecionado.

A mudança será implementada por uma Série de Refatoração Arquitetural composta por patches pequenos, ordenados, compiláveis, testáveis e reversíveis por Git.

---

## 2. Contexto

Na baseline `0.4.1`, a entrada da CLI executa:

```cpp
const auto repositoryRoot = sister::hoa::locateRepositoryRoot();
return sister::hoa::runCommand(arguments, repositoryRoot);
```

A descoberta da raiz reconhece diretamente:

```text
project.sister.yaml
SISTER_HOA_HOME
```

O registro de targets carrega:

```text
config/targets/
```

relativamente à mesma raiz.

Esse desenho cumpre o estágio H1, mas mistura quatro conceitos:

1. raiz do código do HOA;
2. raiz da governança do próprio HOA;
3. raiz do projeto operado;
4. identidade do ecossistema SisTer.

Como consequência, o HOA observa targets externos, porém continua dependente de uma raiz privilegiada e de nomes específicos do SisTer para constituir seu contexto principal.

---

## 3. Problema

O núcleo atual não representa explicitamente um *workspace* operacional.

Isso produz os seguintes efeitos:

- não existe seleção explícita de projeto pela CLI;
- a descoberta do contexto depende de nomes específicos;
- targets do ecossistema observado residem no repositório do operador;
- o HOA não pode operar outro projeto sem configuração central;
- a autoaplicação sobre o próprio HOA não usa o mesmo protocolo destinado a outros projetos;
- limites de leitura e escrita não são modelados como propriedade do contexto;
- a identidade `SisTer-HOA` tende a ser confundida com a identidade do projeto operado.

---

## 4. Decisão

O HOA passará a operar sobre um `ProjectWorkspace` explicitamente selecionado.

O princípio normativo é:

> **O HOA não conhece antecipadamente o sistema. O HOA conhece um workspace capaz de declarar um sistema.**

A seleção inicial obedecerá à seguinte precedência:

```text
1. --project <pasta>
2. diretório atual
3. compatibilidade transitória da baseline antiga
```

O novo fluxo será:

```text
argumentos da CLI
  ↓
seleção da pasta
  ↓
canonicalização e validação
  ↓
ProjectWorkspace
  ↓
descoberta do ProjectManifest
  ↓
carregamento de targets e recursos locais
  ↓
execução do comando
```

---

## 5. Modelo de domínio

### 5.1 `ProjectWorkspace`

Representa a fronteira operacional selecionada.

Responsabilidades:

- armazenar a raiz canônica;
- registrar a origem da seleção;
- validar existência e tipo da pasta;
- resolver caminhos relativos com segurança;
- impedir escape não autorizado da raiz;
- localizar o manifesto;
- fornecer caminhos para targets e estado local.

Interface conceitual:

```cpp
namespace sister::hoa {

class ProjectWorkspace final {
public:
    explicit ProjectWorkspace(std::filesystem::path root);

    [[nodiscard]]
    const std::filesystem::path& root() const noexcept;

    [[nodiscard]]
    std::filesystem::path resolve(
        const std::filesystem::path& relative
    ) const;

    [[nodiscard]]
    bool contains(
        const std::filesystem::path& candidate
    ) const;

private:
    std::filesystem::path root_;
};

}
```

A interface final poderá usar `std::expected` para erros de resolução e validação.

### 5.2 `ProjectManifest`

Representa a declaração do projeto publicada pelo *workspace*.

Localização preferencial:

```text
.hoa/project.yaml
```

Conteúdo inicial mínimo:

```yaml
schema: hoa-project/0.1
id: sister
name: SisTer

paths:
  targets: .hoa/targets
  state: .hoa/state
```

A primeira implementação não precisa interpretar todo o YAML. Poderá reconhecer apenas o manifesto e usar caminhos convencionais, preservando espaço para parser posterior.

### 5.3 Raiz do HOA e raiz do projeto

A implementação deve distinguir:

```text
hoaSourceRoot
workspaceRoot
```

`hoaSourceRoot` é usado somente para recursos pertencentes à instalação ou ao desenvolvimento do HOA.

`workspaceRoot` é usado para observar e planejar operações sobre o projeto selecionado.

Um comando não deve receber uma variável genericamente chamada `repositoryRoot` quando os dois conceitos puderem divergir.

---

## 6. Interface de linha de comando

### 6.1 Uso principal

```bash
hoa --project /caminho/do/projeto status
hoa --project /caminho/do/projeto doctor
hoa --project /caminho/do/projeto target catalog
```

Dentro da pasta:

```bash
cd /caminho/do/projeto
hoa doctor
```

### 6.2 Comando de inspeção

A série deverá introduzir ou preparar:

```bash
hoa workspace inspect
```

Saída mínima:

```text
Workspace root: /caminho/canonico
Selection source: command-line | current-directory | compatibility
Manifest: .hoa/project.yaml | legacy | not-found
Targets: .hoa/targets
Access boundary: confined
```

### 6.3 Nome do executável

O executável neutro será:

```text
hoa
```

Durante a transição, `sister-ops` será preservado como alias ou wrapper compatível.

A RFC não exige, nesta série, a renomeação dos namespaces C++, dos targets CMake ou da identidade institucional `SisTer-HOA`.

---

## 7. Organização do projeto operado

Estrutura preferencial:

```text
<workspace>/
├── .git/
├── .hoa/
│   ├── project.yaml
│   ├── targets/
│   ├── skills/
│   ├── policies/
│   ├── series/
│   └── state/
├── CMakeLists.txt
├── src/
└── ...
```

O conhecimento específico do projeto deve residir prioritariamente no próprio *workspace*.

O núcleo do HOA mantém mecanismos genéricos para:

- localizar;
- interpretar;
- observar;
- planejar;
- validar;
- registrar.

---

## 8. Migração e compatibilidade

### 8.1 Manifesto

Preferencial:

```text
.hoa/project.yaml
```

Legado temporariamente aceito:

```text
project.sister.yaml
```

Quando o legado for usado, a CLI deverá emitir aviso não fatal:

```text
WARN: legacy project manifest detected: project.sister.yaml
      migrate to .hoa/project.yaml
```

### 8.2 Targets

Preferencial:

```text
.hoa/targets/
```

Legado temporariamente aceito:

```text
config/targets/
```

Precedência:

```text
1. .hoa/targets
2. config/targets
```

Não deve ocorrer mesclagem silenciosa das duas árvores na primeira versão. Se ambas existirem, a origem preferencial será usada e o legado será informado.

### 8.3 Variável de ambiente

`SISTER_HOA_HOME` não deve continuar como mecanismo geral de seleção do projeto.

Ela poderá ser reconhecida temporariamente apenas no modo de compatibilidade necessário à governança da própria baseline. Uma futura RFC poderá substituí-la por uma variável neutra, caso ainda exista necessidade operacional.

---

## 9. Confinamento e segurança

O *workspace* é uma fronteira de autoridade, não apenas de conveniência.

### 9.1 Regras

1. Caminhos relativos serão resolvidos contra a raiz canônica.
2. `..`, links simbólicos e canonicalização não poderão produzir escape silencioso.
3. Operações somente leitura poderão permanecer no nível padrão.
4. Escritas dentro do *workspace* exigirão política explícita quando habilitadas.
5. Escritas externas ao *workspace* exigirão autoridade reforçada.
6. A indicação de uma pasta não concederá automaticamente autoridade para executar comandos arbitrários nela.

### 9.2 Classes preliminares de acesso

```cpp
enum class WorkspaceAccess {
    read_only,
    project_write,
    external_write
};
```

A presente RFC implementa prioritariamente a seleção e a observação. A execução mutável externa permanece bloqueada pelo estágio H1 e pela ADR-0003.

---

## 10. Série de Refatoração Arquitetural

A implementação será dividida em dez patches.

### 0001 — Introduzir `ProjectWorkspace`

- adicionar contrato C++;
- canonicalizar e validar raiz;
- incluir testes unitários;
- não alterar comportamento externo.

### 0002 — Introduzir descoberta de manifesto

- reconhecer `.hoa/project.yaml`;
- reconhecer `project.sister.yaml` como legado;
- representar a origem da descoberta;
- adicionar testes de precedência.

### 0003 — Separar raiz do HOA e raiz do workspace

- remover ambiguidade de `repositoryRoot`;
- introduzir nomes explícitos;
- preservar comandos existentes;
- atualizar assinaturas internas.

### 0004 — Adicionar opção global `--project`

- interpretar pasta informada;
- usar diretório atual por padrão;
- rejeitar pasta inexistente;
- atualizar ajuda e testes da CLI.

### 0005 — Adicionar inspeção do workspace

- criar projeção observacional;
- mostrar raiz, origem, manifesto e limites;
- não conceder autoridade mutável.

### 0006 — Migrar descoberta de targets

- preferir `.hoa/targets`;
- manter `config/targets` como legado;
- impedir mesclagem silenciosa;
- atualizar testes do `TargetRegistry`.

### 0007 — Migrar o próprio SisTer-HOA

- criar `.hoa/project.yaml`;
- mover ou copiar targets para `.hoa/targets` durante a transição;
- preservar baseline de governança;
- ajustar scripts e CI.

### 0008 — Introduzir executável neutro `hoa`

- produzir `hoa` no CMake;
- manter `sister-ops` como alias ou wrapper;
- atualizar mensagens de uso sem remover compatibilidade.

### 0009 — Atualizar documentação e governança

- atualizar README, DDD, DAI, ADRs e políticas pertinentes;
- registrar nova linguagem ubíqua;
- atualizar o validador da baseline.

### 0010 — Remover acoplamentos operacionais restantes

- revisar strings, caminhos e pressupostos específicos;
- manter apenas identidade institucional onde apropriado;
- executar busca automatizada de acoplamentos;
- produzir relatório final de conformidade.

---

## 11. Requisitos por patch

Cada patch da série deverá:

1. representar uma única mudança lógica;
2. aplicar sobre a baseline declarada;
3. passar em `git apply --check` quando transportado como patch;
4. compilar com C++23;
5. passar nos testes aplicáveis;
6. passar em `git diff --check`;
7. não incluir artefatos de build ou estado local;
8. possuir mensagem de commit explicativa;
9. ser reversível por Git;
10. deixar o projeto em estado intermediário válido.

---

## 12. Plano de verificação

### 12.1 Verificações por patch

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
git diff --check
```

Quando aplicável:

```bash
python3 scripts/validate_governance_repo.py
./scripts/run_quality.sh
```

### 12.2 Cenários obrigatórios

#### Seleção explícita

```bash
hoa --project /tmp/projeto doctor
```

Deve usar `/tmp/projeto` como *workspace*.

#### Diretório atual

```bash
cd /tmp/projeto
hoa doctor
```

Deve usar o diretório atual.

#### Pasta inexistente

```bash
hoa --project /nao/existe doctor
```

Deve falhar sem executar o comando.

#### Manifesto preferencial

Quando `.hoa/project.yaml` e `project.sister.yaml` existirem, o manifesto `.hoa` deve prevalecer.

#### Targets preferenciais

Quando `.hoa/targets` e `config/targets` existirem, apenas `.hoa/targets` deve ser carregado e o legado deve ser informado.

#### Confinamento

A resolução de `../../fora` deve ser rejeitada para operações confinadas.

#### Autoaplicação

```bash
hoa --project "$PWD" doctor
```

Executado na raiz do SisTer-HOA, deve usar o mesmo mecanismo destinado a qualquer projeto.

#### Compatibilidade

```bash
./sister-ops doctor
```

Deve permanecer funcional durante a janela de transição.

---

## 13. Evidências requeridas

A conclusão da série deverá produzir:

- hash da baseline;
- lista ordenada dos patches;
- hashes dos commits produzidos;
- resultados de build e testes por etapa;
- resultado do validador de governança;
- relatório de busca por acoplamentos restantes;
- diff final;
- estado final do repositório;
- declaração de compatibilidade;
- decisão humana de recebimento.

Estrutura futura sugerida:

```text
.hoa/series/HOA-RFC-0001/
├── series.yaml
├── patches/
├── verification.yaml
├── evidence/
└── receipt.json
```

---

## 14. Critérios de aceite

A RFC será considerada implementada quando:

1. o HOA aceitar um *workspace* por `--project`;
2. a ausência de `--project` usar o diretório atual;
3. `.hoa/project.yaml` for reconhecido como manifesto preferencial;
4. `.hoa/targets` for reconhecido como origem preferencial de targets;
5. a raiz do HOA e a raiz do projeto forem conceitos distintos no código;
6. caminhos confinados não escaparem silenciosamente do *workspace*;
7. o próprio HOA puder ser operado pelo mesmo mecanismo;
8. `sister-ops` permanecer funcional durante a transição;
9. todos os testes e gates aplicáveis passarem;
10. evidências da série forem produzidas e recebidas por autoridade humana.

---

## 15. Não objetivos

Esta RFC não implementa:

- execução autônoma de operações mutáveis;
- shell irrestrito;
- integração com LLM;
- servidor MCP;
- parser YAML completo;
- sistema geral de plugins;
- descoberta remota de projetos;
- renomeação integral dos namespaces C++;
- remoção imediata de todos os nomes institucionais SisTer-HOA;
- promoção automática a produção.

Esses temas poderão ser tratados em RFCs posteriores.

---

## 16. Riscos

### Confusão entre identidade e neutralidade

Desacoplar o projeto operado não exige apagar a história ou a identidade do SisTer-HOA. O nome institucional pode permanecer; o mecanismo operacional deve ser genérico.

### Compatibilidade prolongada

A camada legada pode tornar-se permanente. A janela de compatibilidade deverá ser explicitamente encerrada por RFC ou release futura.

### Manifesto prematuro

Um manifesto excessivamente amplo pode cristalizar decisões cedo demais. A versão `0.1` deverá permanecer mínima.

### Falsa sensação de segurança

Confinamento de caminhos não equivale a sandbox completa. Execução de processos e autoridade de sistema exigirão controles adicionais.

### Série excessivamente fragmentada

Patches pequenos não devem perder coerência. Cada unidade precisa ser logicamente completa e contribuir para uma narrativa compreensível.

---

## 17. Consequências

### Positivas

- reutilização do HOA em outros projetos;
- redução de acoplamento ao SisTer;
- autoaplicação coerente;
- fronteira operacional explícita;
- conhecimento específico próximo do projeto;
- base para skills, agentes e MCP orientados a contexto;
- primeira aplicação concreta de Transformação Governada.

### Custos

- novas abstrações de domínio;
- migração de estrutura;
- compatibilidade temporária;
- ampliação dos testes;
- atualização de documentação e scripts;
- necessidade de disciplinar precedência e confinamento.

---

## 18. Decisão de autoridade

Enquanto esta RFC estiver em estado **Proposta**:

- os documentos podem ser revisados;
- a série pode ser preparada;
- `git apply --check` e testes em cópia descartável são autorizados;
- aplicação ao repositório principal exige aprovação humana explícita;
- commits e pushes não são autorizados implicitamente pela existência da RFC.

A passagem para **Aceita** deverá registrar a autoridade que aprovou a transformação e a baseline sobre a qual a série será aplicada.

---

## 19. Resultado esperado

Antes:

```text
SisTer-HOA
└── conhece o ecossistema SisTer
```

Depois:

```text
SisTer-HOA
└── opera um ProjectWorkspace
    ├── manifesto
    ├── targets
    ├── skills
    ├── políticas
    └── séries de transformação
```

A primeira prova da arquitetura será o próprio HOA operar sua transformação:

```bash
hoa --project ~/dev/cpp/SisTer-HOA \
    series verify HOA-RFC-0001
```

Esse comando pertence a uma fase posterior. A presente RFC constrói a base que tornará sua implementação coerente.
