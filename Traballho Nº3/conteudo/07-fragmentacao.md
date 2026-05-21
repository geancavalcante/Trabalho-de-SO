# Seção 7 — Fragmentação

> Artefato visual: **Quadro Fragmentação Interna vs Externa**

## Definição

**Fragmentação** é todo desperdício de memória que ocorre como efeito colateral das estratégias de alocação. A memória total disponível é maior do que a memória utilizável de fato — porque parte dela está "presa" em pedaços inúteis.

Existem dois tipos. Eles têm causas e mitigações diferentes — e nenhuma técnica de alocação elimina os dois ao mesmo tempo.

## Quadro comparativo

| Aspecto | Fragmentação interna | Fragmentação externa |
|---|---|---|
| **Onde ocorre** | Dentro de blocos já alocados a um processo | Entre blocos livres |
| **Causa** | Alocador entrega mais espaço do que o processo realmente usa | Sucessivas alocações/liberações deixam buracos pequenos e espalhados |
| **Característica visual** | Bloco alocado tem espaço sobrando no final | Memória total livre é grande, mas não há um bloco contíguo grande o suficiente |
| **Quando aparece mais** | Partições fixas, paginação (última página), alocadores com tamanho mínimo | Partições variáveis, segmentação, alocadores que não consolidam |
| **Mitigação principal** | Tamanhos de página menores; alocadores que ajustam o bloco ao pedido | Compactação; paginação (elimina o requisito de contiguidade) |
| **Custo da mitigação** | Mais overhead de tabela (páginas menores → tabelas maiores) | Compactação é caríssima (mover processos inteiros); paginação exige hardware (MMU) |

## Fragmentação interna — exemplo visual

```text
Processo pede 13 KB.
Sistema aloca 1 página inteira de 16 KB (granularidade fixa).

       Página alocada de 16 KB
       ┌───────────────────────────────────┐
       │   USADO (13 KB)        │ DESPER- │
       │                        │ DÍCIO   │
       │                        │  3 KB   │
       └───────────────────────────────────┘
                                  ↑
                       Esses 3 KB pertencem ao processo,
                       mas ele não os utiliza. Não podem
                       ser dados a outro processo.
```

### Onde aparece no Linux

- **Última página do heap, da stack, e de cada VMA**: em média, metade de uma página por VMA é desperdiçada (~2 KB com páginas de 4 KB)
- **Allocadores em userspace** (glibc malloc, jemalloc): usam *size classes*; pedido de 17 bytes pode virar bloco de 24 bytes
- **Slab allocator do kernel**: objetos com tamanhos fixos por classe

A fragmentação interna **é previsível e limitada** — sabemos quanto vamos perder por VMA. É o preço da simplicidade.

## Fragmentação externa — exemplo visual

```text
Tempo 0:  Memória livre, 100 MB total

[                                                  ] livre

Tempo 1:  Alocadas regiões de 30, 20, 25, 10 MB (sobra 15 MB)

[ A:30 ][ B:20 ][ C:25 ][ D:10 ][ livre:15 ]

Tempo 2:  B e D liberados

[ A:30 ][ livre:20 ][ C:25 ][ livre:25 ]

Total livre: 45 MB
Maior bloco contíguo livre: 25 MB
Pedido de 40 MB → NÃO CABE  (mesmo havendo 45 MB livres!)
```

Esse é o pesadelo da alocação contígua. **Memória existe, mas está fragmentada em buracos que não servem para nada grande.**

### Onde aparece no Linux

- **`vmalloc` no kernel**: aloca regiões virtualmente contíguas para o kernel (mas fisicamente espalhadas). O *espaço* `vmalloc` pode fragmentar.
- **Huge pages**: requerem blocos contíguos físicos de 2 MB. Sob fragmentação, o kernel pode não conseguir formar huge pages mesmo com RAM livre.
- **Alocações DMA grandes**: hardware antigo exige contiguidade física.

## Por que a paginação resolve a fragmentação externa

A paginação **quebra o requisito de contiguidade física**. Como qualquer página virtual pode ser mapeada em qualquer frame físico, basta haver frames livres em qualquer lugar — não precisam ser adjacentes.

```text
Antes (sem paginação):
   processo grande precisa de bloco contíguo grande
   ┌───────────────────────────────────────────┐
   │ não cabe se houver buracos no meio        │
   └───────────────────────────────────────────┘

Com paginação:
   processo dividido em páginas; cada página em qualquer frame
   ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
   │ pág 0 │ │ pág 1 │ │ pág 2 │ │ pág 3 │ │ pág 4 │
   └───────┘ └───────┘ └───────┘ └───────┘ └───────┘
       ↓        ↓         ↓         ↓         ↓
   frame 17  frame 3   frame 42  frame 8   frame 99
```

O custo: agora há **fragmentação interna** na última página de cada região, e há **overhead** das tabelas e da TLB.

> A paginação não elimina fragmentação. Ela troca fragmentação externa (grave, imprevisível, exige compactação) por fragmentação interna (pequena, previsível, limitada).

## Algoritmos de alocação clássicos e seu impacto

| Algoritmo | Como funciona | Tendência |
|---|---|---|
| **First-fit** | Pega o primeiro buraco que serve | Rápido; tende a fragmentar o início da memória |
| **Best-fit** | Pega o menor buraco que serve | Deixa buracos minúsculos inúteis → fragmentação externa |
| **Worst-fit** | Pega o maior buraco e divide | Em teoria evita buracos pequenos; na prática, ruim |
| **Buddy system** | Aloca em potências de 2; merge de "irmãos" livres | Usado no Linux para frames físicos; baixa fragmentação externa |
| **Slab** | Pools de objetos pré-alocados de tamanho fixo | Usado no kernel para objetos pequenos e frequentes |

## Pontos a evidenciar no visual

- Duas colunas grandes: **INTERNA** (à esquerda) e **EXTERNA** (à direita)
- Cor **vermelha** para o desperdício em ambos os casos
- Ilustração da última página com hachura mostrando o "pedaço perdido" para interna
- Ilustração do mapa de memória com buracos espalhados para externa
- Caixa inferior: "**Paginação troca externa por interna — e isso é uma vitória**" como conclusão visual
