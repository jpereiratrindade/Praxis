# Política de autoridade de workspace

1. A raiz canônica do workspace define a fronteira operacional padrão.
2. Resolução de caminhos não pode escapar dessa raiz sem autorização específica.
3. Descoberta e inspeção são `read`.
4. `git fetch` é `mutate_local`: altera refs locais, mas não o working tree.
5. Push, merge, reset, checkout destrutivo e escrita fora do workspace não são implícitos.
6. Operações de transformação devem declarar risco, precondições, verificações e evidência.
7. Um workspace não herda automaticamente autoridade de outro workspace ou do repositório do HOA.
