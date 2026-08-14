# PRAXIS-METHOD-002 — Fronteira da prova e não-superinterpretação

## Origem empírica

Cenário extraído da revisão independente do SisTer Atmos após o fechamento
governado de A1-E002.

O marco possuía build C++23, testes, sanitizers, Golden Cases, evidência
governada, checksum, ancestralidade Git e consistência do estado em PASS. Ao
mesmo tempo, providers reais, persistência, H3 operacional, API, escala de
produção e integração operacional permaneciam deliberadamente fora do escopo.

## Problema observado

Um estado `verified` tecnicamente legítimo pode ser superinterpretado como
prontidão global do sistema quando a fronteira da prova não é preservada na
leitura humana ou assistida.

## Hipótese

Separar explicitamente prova de maturidade global impede que sucesso localizado
seja convertido em reivindicação não sustentada.

## Regra derivada

Um estado verificado prova aquilo que foi governadamente submetido à prova; não
autoriza extrapolar maturidade, capacidade ou prontidão além dessa fronteira.

## Avaliação independente

A revisão externa que revelou o risco é tratada como `finding`, não como
autoridade. Recomendações de CI, property testing, benchmark ou mudanças de
modelo só se tornam obrigação quando houver escopo, evidência e decisão
governada que as justifiquem.

## Contraprovas futuras

O princípio deve ser revisto se projetos reais demonstrarem que a fronteira de
prova pode ser inferida de forma inequívoca e verificável sem declaração ou
política explícita.
