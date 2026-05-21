# Conteúdo do Trabalho — System Design da Memória

Este diretório contém o conteúdo técnico organizado por seção. Cada arquivo serve a dois propósitos:

1. **Insumo para o documento visual** — os blocos com a convenção fixa (nome, função, entrada, saída, risco) entram direto nos diagramas
2. **Insumo para o texto de apoio** — a redação em prosa do material vira a base das 2 a 4 páginas finais

## Mapa dos arquivos

### Conteúdo das 10 seções obrigatórias

| Seção | Arquivo | Artefato visual relacionado |
|---|---|---|
| 1. Visão Macro da Arquitetura | [01-visao-macro.md](01-visao-macro.md) | Diagrama macro |
| 2. Classificação das Memórias | [02-classificacao-memorias.md](02-classificacao-memorias.md) | Pirâmide de hierarquia |
| 3. Fluxo de Acesso à Memória | [03-fluxo-acesso.md](03-fluxo-acesso.md) | Fluxo de tradução |
| 4. Visão por Processo | [04-visao-processo.md](04-visao-processo.md) | Mapa do espaço de endereçamento |
| 5. Proteção e Isolamento | [05-protecao-isolamento.md](05-protecao-isolamento.md) | Bloco de proteção |
| 6. Técnicas de Gerenciamento | [06-tecnicas-gerenciamento.md](06-tecnicas-gerenciamento.md) | Quadro comparativo |
| 7. Fragmentação | [07-fragmentacao.md](07-fragmentacao.md) | Quadro interna vs externa |
| 8. Paginação e Memória Virtual | [08-paginacao.md](08-paginacao.md) | Páginas, quadros, page fault |
| 9. Linux na Prática | [09-linux-pratica.md](09-linux-pratica.md) | Bloco Linux |
| 10. Observabilidade | [10-observabilidade.md](10-observabilidade.md) | Bloco de ferramentas |

### Análise crítica

| Tópico | Arquivo |
|---|---|
| Trade-offs | [11-trade-offs.md](11-trade-offs.md) |
| Erros e Riscos | [12-erros-riscos.md](12-erros-riscos.md) |
| Conclusão Crítica | [13-conclusao-critica.md](13-conclusao-critica.md) |

### Material complementar

| Item | Arquivo |
|---|---|
| Glossário Técnico | [14-glossario.md](14-glossario.md) |
| Texto de Apoio (2–4 páginas) | [15-texto-apoio.md](15-texto-apoio.md) |

## Padrão visual a ser aplicado nos diagramas

| Cor | Componente |
|---|---|
| Azul | Hardware e CPU |
| Roxo | MMU, TLB e tradução |
| Verde | Processo, aplicação e espaço do usuário |
| Vermelho | Proteção, falha, violação e fragmentação |
| Laranja | Kernel e subsistema de memória |
| Cinza | Armazenamento secundário e swap |

## Convenção textual obrigatória

Cada bloco visual contém:

- **Nome do componente**
- **Função** — o que ele faz
- **Entrada** — o que recebe
- **Saída** — o que produz
- **Risco / Limitação** — o que pode dar errado
