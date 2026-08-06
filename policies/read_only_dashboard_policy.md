# Política do Painel de Observação

O painel web do SisTer-HOA é uma interface exclusivamente observacional.

## Autoridade

- autoridade para executar operações: nenhuma;
- autoridade para modificar arquivos: nenhuma;
- autoridade para alterar planos, agentes, skills ou políticas: nenhuma;
- autoridade para acessar segredos: nenhuma.

## Fronteira HTTP

- endereço padrão e obrigatório no H0: `127.0.0.1`;
- métodos permitidos: `GET` e `HEAD`;
- métodos rejeitados com `405 Method Not Allowed`: `POST`, `PUT`, `PATCH`, `DELETE` e demais métodos;
- não há endpoints de execução, correção, aprovação, publicação ou mutação.

## Dados

O painel pode apresentar apenas dados derivados de inspeções determinísticas do próprio repositório. Senhas, tokens, chaves privadas, arquivos `.env` e conteúdos integrais de logs não integram o snapshot.
