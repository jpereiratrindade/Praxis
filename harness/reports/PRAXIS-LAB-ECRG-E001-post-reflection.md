# PRAXIS-LAB-ECRG-E001 — Reflexão pós-experimento

## Condição epistemológica

Este relatório preserva aprendizado posterior à constituição de
`PRAXIS-LAB-ECRG-E001`. Ele não altera o registro, o relatório, o verificador,
a evidência ou o resultado histórico do experimento.

## Estado verificado antes desta reflexão

- branch: `main`
- HEAD: `c3e24973a2a9c14bd44c4efa6c932ccb88a0c84e`
- estado canônico: H1 ativo; `PRAXIS-SG-001` permanece como último marco
  verificado; H2 permanece `proposed` e não autorizado
- working tree: somente os cinco artefatos não rastreados de E001
- verificador local de E001: `PASS`
- checksum da evidência histórica: `OK`

## Observação posterior reproduzida

O registro de E001 declara três inputs por caminhos absolutos externos ao
repositório e por seus digests SHA-256. O verificador exige que cada caminho
seja um arquivo existente antes de comparar o digest.

No workspace originário, os caminhos são resolvíveis e o verificador passa. Em
um namespace efêmero no qual o diretório externo `Downloads` não está
disponível, as verificações internas anteriores passam e a execução termina em:

```text
FAIL  input missing — /home/jpereiratrindade/Downloads/Prompt para Codex — PRAXIS-LAB-ECRG-E001.md
```

Essa reprodução não modificou os artefatos de E001.

## Reavaliação do resultado

O resultado histórico permanece `SUPPORTED` dentro de sua fronteira original:
constituição e verificação local de um experimento `proposed`, confinado ao
Harness, sem promoção de ECRG ou PRAXIS-SG-002.

A evidência não sustenta uma extensão dessa claim para reconstrução independente
ou proveniência portátil. Essa extensão é `NOT_SUPPORTED` no caso atual.

## Finding sustentado no caso

```text
ECRG-F001
External input identity does not imply portable provenance.
```

Um digest permite verificar a identidade de bytes disponíveis. Ele não preserva
esses bytes, não oferece por si só uma fonte de recuperação e não torna um
caminho absoluto resolvível em outro workspace.

O finding não autoriza correção de E001 nem generalização normativa.

## MRE candidata

O aprendizado mínimo sustentado é:

> Registrar caminho absoluto e digest permite localizar um input no ambiente
> originário e verificar a identidade de conteúdo disponível, mas não torna o
> input materialmente necessário recuperável em workspace independente.

As propriedades abaixo permanecem distinções candidatas, não taxonomia:

| Propriedade candidata | Pergunta respondida |
|---|---|
| referência registrada | Qual locator foi registrado? |
| identidade verificável | Um conteúdo candidato corresponde aos bytes esperados? |
| recuperabilidade governada | Os bytes podem ser obtidos de uma fonte governadamente resolvível? |

Não foi demonstrado que essas propriedades formem uma escala universal ou que
devam ser materializadas em schema, policy ou gate.

## Refinamento conceitual candidato de ECRG1-I07

Formulação histórica, preservada em E001:

> Todo artefato gerado possui proveniência reconstruível até este experimento.

Formulação candidata, sem efeito normativo:

> Todo artefato gerado deve ser rastreável ao registro deste experimento. Quando
> a claim incluir reprodução independente, cada input materialmente necessário
> deve estar preservado ou ser recuperável por uma referência governadamente
> resolvível, com identidade verificável.

## Protocolo comportamental experimental

Os identificadores abaixo substituem, para execuções laboratoriais futuras, a
numeração provisória `P-ECRG-01...09`, que colidia com uma proposição já
existente no documento conceitual. A renomeação não promove o protocolo:

- `ECRG-OP01` — observação não é interpretação;
- `ECRG-OP02` — finding não é autorização;
- `ECRG-OP03` — MRE não é MOG;
- `ECRG-OP04` — PASS possui fronteira;
- `ECRG-OP05` — o sistema executável participa da investigação;
- `ECRG-OP06` — usar a menor intervenção informativa;
- `ECRG-OP07` — não materializar literalmente a conversa;
- `ECRG-OP08` — autoridade não pode ser autoampliada;
- `ECRG-OP09` — resultado negativo é resultado válido.

## Integridade histórica observada

Hashes aferidos antes da constituição de E002:

```text
75bde02eef2d9962e75d1c4d2d96fda2492b6c34f50410f2e95e3cf1843d7f77  harness/scenarios/PRAXIS-LAB-ECRG-E001.json
11dc75f814f42d0d06e939b5eff0b3cf03bcb6bddb05449b244f17dfc3edd260  harness/reports/PRAXIS-LAB-ECRG-E001.md
7e562e73cb50835fa070f78fac556a1c9a07a24318fbc6ffe63ec9167d22ceb5  harness/scenarios/verify_praxis_lab_ecrg_e001.py
2808cc4a6922ce96efdb7d0cec4f89a0ed09bded34f6fa45cedb98b5731d57e6  harness/evidence/PRAXIS-LAB-ECRG-E001-verification.txt
22f199759c04335aa7cb601ba2ffe90d2c0d17bf53253bcc2076ba1be8a7558b  harness/evidence/PRAXIS-LAB-ECRG-E001-verification.sha256
```

O verificador histórico de E001 delimita o working tree aos cinco artefatos da
constituição original. Por isso, novos artefatos autorizados de E002 passam a
ser reportados por ele como mudanças inesperadas. Isso não altera os bytes ou a
evidência histórica de E001; demonstra que seu gate local não foi desenhado
como gate de sucessão para um Harness posteriormente ampliado.

## Consequência experimental

O finding e a MRE candidata justificam constituir, mas não executar,
`PRAXIS-LAB-ECRG-E002 — Minimal Governed Reconstruction`.
