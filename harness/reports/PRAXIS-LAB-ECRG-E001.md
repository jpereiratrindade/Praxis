# PRAXIS-LAB-ECRG-E001 — Constituição experimental

## Estado encontrado

- branch: `main`
- HEAD inicial: `c3e24973a2a9c14bd44c4efa6c932ccb88a0c84e`
- working tree inicial: limpo
- estado canônico: H1 ativo; `PRAXIS-SG-001` é o último marco verificado; H2 permanece proposto e não autorizado
- estrutura laboratorial encontrada: `harness/scenarios`, `harness/reports`, `harness/evidence` e `harness/plans`
- Agents registrados: `diagnostic-agent` e `workspace-operator`
- Skills registradas: 11 manifests em `harness/skills`
- contratos relacionados: `project-state.schema.json` e `experiment-record.schema.json`
- policies relacionadas: estado governado, evidência/auditoria, autoridade de workspace e uso de IA
- gates relacionados: validadores de governança, metodologia, projeto governado e autogovernança do Praxis

## Decisão arquitetural

```text
ECRG pertence experimentalmente ao Praxis-Lab? SIM
```

No repositório atual, Praxis-Lab não é um novo componente ou diretório de topo. O papel laboratorial já é materializado pelo Harness, que possui áreas explícitas para cenários, relatórios e evidências. ECRG-E001 é constituído nessas áreas sem criar nova arquitetura e sem entrar no núcleo normativo.

## Classificação epistemológica

| Elemento | Origem | Classificação | Justificativa | Evidência independente | Pode alterar estado | Novo experimento |
|---|---|---|---|---|---|---|
| PASS dos gates atuais | Estado e evidência de PRAXIS-SG-001 | OBSERVATION | Há prova preservada dentro da fronteira dos gates existentes | sim | não | não |
| Governança semântica plena não demonstrada | Revisão Codex e avaliação posterior | FINDING | Divergências observáveis passam pelos gates estruturais | sim | não | sim |
| Fundação GREEN e fechamento semântico AMBER | Síntese da conversa | INTERPRETATION | Preserva a diferença entre prova existente e capacidade ainda não provada | parcial | não | sim |
| Conversa como circuito reflexivo de engenharia | Hipótese ECRG | MRE_CANDIDATE | É compreensão provisória, ainda falsificável | não | não | sim |
| PRAXIS-SG-001 continua como último marco verificado | Estado canônico, evidência e Git | MOG_CLAIM | A claim possui referências governadas resolvíveis | sim | não | não |
| SG2-I01 a SG2-I09 | Propostas da conversa | NORMATIVE_PROPOSAL | São candidatos, não regras aprovadas | parcial | não | sim |
| Conversation-to-Governed-Experiment | Prompt ECRG-E001 | EXPERIMENTAL_HYPOTHESIS | É a hipótese desta constituição e admite resultado negativo | não | não | sim |
| Criar registro, relatório, verificador e evidência no Harness | Autoridade explícita do prompt | AUTHORIZED_ACTION | Mutação limitada à área experimental existente | sim | somente Harness experimental | não |
| Alterar Core, governança normativa, estado, Agents, Skills ou SG-002 | Proibições explícitas do prompt | NOT_AUTHORIZED | Finding não amplia autoridade | sim | não | sim, com autorização própria |

## Refinamento dos invariantes

- `ECRG1-I01`: aceito; instancia a política vigente de que finding não promove estado.
- `ECRG1-I02`: aceito; MRE preserva compreensão provisória e MOG preserva prova/autorização.
- `ECRG1-I03`: refinado para “claim de estado governado”, evitando exigir evidência formal para toda frase interpretativa.
- `ECRG1-I04`: aceito; é a fronteira operacional central desta execução.
- `ECRG1-I05`: aceito; impede promoção metodológica por um único caso.
- `ECRG1-I06`: aceito; ECRG-E001 e PRAXIS-SG-002 possuem hipóteses e autoridades distintas.
- `ECRG1-I07`: aceito; aplica M05 aos artefatos e digests dos insumos.
- `ECRG1-I08`: aceito; preserva falsificabilidade e permite `NOT_SUPPORTED` ou `INCONCLUSIVE`.

Não foi identificado conflito com M01–M07. Há redundância deliberada entre I01, I04, I05 e I06: todos protegem autoridade, mas em fronteiras diferentes. I03 e I07 especializam integridade referencial e evidência.

## Fronteira de prova

Uma execução bem-sucedida do verificador sustenta somente esta claim:

> A conversa recebida foi transformada em um registro experimental `proposed`, rastreável e confinado ao Harness, sem alteração do estado canônico ou promoção de ECRG/SG-002.

Ela não sustenta que ECRG seja um método comprovado, que PRAXIS-SG-002 esteja autorizado ou que a governança semântica do Praxis esteja encerrada.

## Próxima pergunta experimental

Uma segunda execução independente consegue reconstruir a classificação e detectar promoção indevida usando apenas os artefatos governados de ECRG-E001?
