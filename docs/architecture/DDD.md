# DDD — Praxis

## Problema governante

Reduzir esforço operacional sem transferir ao LLM autoridade, shell irrestrito,
segredos ou capacidade autônoma de alterar sistemas.

## Contexto delimitado

O Praxis implementa um Governed Operational Harness (HOA) para coordenar operações de engenharia e infraestrutura sobre workspaces selecionados. Não absorve domínio,
identidade, dados ou autoridade dos subsistemas.

## Linguagem ubíqua

- **Agente:** política operacional versionada que limita objetivo e repertório.
- **Skill:** capacidade versionada com autoridade, risco, contrato e executor.
- **Plano:** sequência validada de skills proposta para um objetivo.
- **Gate:** decisão que permite, restringe ou nega execução.
- **Adapter:** ligação determinística com CLI, API ou biblioteca autorizada.
- **Recibo:** registro reconstruível da tentativa, execução e verificação.
- **Finding:** constatação sem autoridade automática para agir.
- **Modo Harness:** observar, interpretar, planejar, autorizar, executar,
  verificar, registrar, avaliar e aprender.

## Agregados iniciais

- GovernanceBaseline
- AgentRegistry
- SkillRegistry
- OperationPlan
- ExecutionReceipt

## Invariantes

1. LLM não executa.
2. Skill não registrada não pode produzir efeito.
3. Risco mutável exige gate explícito.
4. Sucesso exige pós-condição.
5. Autoridade permanece no sistema governante.
