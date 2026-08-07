# ADR-0004 — Workspace como fronteira operacional

## Estado
Aceito para implementação incremental.

## Decisão
O HOA não assume identidade, topologia ou convenções do SisTer para constituir seu contexto operacional. Toda observação e transformação inicia em um `ProjectWorkspace` explicitamente selecionado por `--project` ou pelo diretório atual.

O workspace é uma fronteira de autoridade: caminhos relativos devem permanecer contidos em sua raiz canônica. Recursos pertencentes à instalação do HOA não se confundem com recursos do projeto operado.

## Compatibilidade
O executável `sister-ops` permanece disponível durante a migração. O executável neutro `hoa` é a interface preferencial para operações orientadas a workspace.

## Consequências
- qualquer projeto C++ pode ser inspecionado sem registro central no SisTer;
- `.hoa/project.yaml` é o manifesto preferencial, mas sua ausência não impede descoberta básica;
- operações mutáveis devem declarar autoridade e produzir evidência;
- nomes específicos do SisTer passam a ser configuração/caso de uso, não conhecimento do núcleo.
