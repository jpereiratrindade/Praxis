# PRAXIS-METHOD-001 — Estado governado e prevenção de deriva

## Origem empírica

Cenário extraído do SisTer Atmos após A1-E001.

Foram observadas simultaneamente:

- README ainda em A0;
- manifests globais ainda em A0;
- A1-E001 já verificado em `main`;
- evidência final presente apenas em `.build`;
- referência de teste inexistente em metadata;
- bootstrap A0 capaz de reescrever scaffolding;
- caches CMake do build contendo caminho absoluto da máquina de origem.

## Hipótese

Um estado canônico + integridade referencial + evidência governada + bootstrap
monotônico detecta ou previne essas classes de deriva sem conhecer o domínio
científico do projeto.

## Critérios

1. manifesto canônico existe;
2. commit verificado é ancestral de HEAD;
3. gate e evidência declarados existem;
4. evidência prova PASS do marco;
5. build transitório não é versionado;
6. autorização do próximo marco é explícita;
7. bootstrap declara política `create_once` ou `idempotent`.

## Contraprovas futuras

O método deve evoluir quando projetos reais apresentarem uma deriva que passe
por todos os critérios acima. Nova regra só deve ser promovida após evidência.
