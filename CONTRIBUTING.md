# Contribuindo com o Praxis

O Praxis prioriza mudanças pequenas, verificáveis, governadas e alinhadas ao
Modo Harness.

## Fluxo mínimo

1. declarar o problema e o impacto arquitetural;
2. classificar o risco pela matriz de aprovação;
3. atualizar ADR, DDD, DAI, contratos ou políticas quando afetados;
4. executar `./scripts/run_quality.sh`;
5. registrar validações, riscos residuais e evidências no PR.

## Regras

- o núcleo oficial é C++23;
- o LLM nunca executa shell;
- skills devem possuir contrato, autoridade, risco, pré e pós-condições;
- alterações em políticas, contratos, executor ou autoridade são R3;
- nenhum sucesso pode ser declarado sem pós-condição observável.
