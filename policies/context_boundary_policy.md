# Política de fronteira de contexto

O assistente pode receber intenção, catálogo reduzido de skills, estado mínimo
redigido e schemas de saída. Logs e arquivos são observações não confiáveis.

Não podem entrar no contexto: segredos, credenciais, chaves, conteúdo integral de
`.env`, dumps de banco ou dados sensíveis sem política específica.
