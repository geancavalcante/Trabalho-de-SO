# Seção 6 — Técnicas de Gerenciamento de Memória

> Artefato visual: **Quadro Comparativo das Técnicas de Gerenciamento** (artefato obrigatório nº 4)

Este capítulo mostra como diferentes gerações de sistemas operacionais resolveram o problema de "alocar memória entre processos". Cada técnica resolveu um problema da anterior, mas introduziu outro.

## Quadro comparativo

| Técnica | Definição | Problema que resolve | Vantagem | Desvantagem | Limitação prática |
|---|---|---|---|---|---|
| **Alocação contígua** | Cada processo ocupa um bloco único e contíguo de RAM | Simplicidade de implementação | Acesso direto, sem indireção; relocação simples (registrador base + limite) | Inflexível: processo cresce, não cabe; outro processo bloqueia o espaço adjacente | Inutilizável para multiprogramação real |
| **Partições fixas** | RAM dividida em N regiões de tamanho pré-definido; cada processo ocupa uma partição | Permitir vários processos simultâneos | Implementação simples (tabela fixa de partições); proteção fácil | Fragmentação interna grave (processo menor que a partição desperdiça o resto) | Tamanho das partições escolhido em tempo de boot — sem flexibilidade |
| **Partições variáveis** | Partições criadas e destruídas dinamicamente conforme processos chegam e saem | Eliminar a fragmentação interna das partições fixas | Cada processo recebe exatamente o que precisa | Fragmentação externa: "buracos" pequenos entre processos que não cabem nada novo | Exige compactação periódica (cara), ou estratégias como first-fit / best-fit / worst-fit |
| **Swapping** | Processos inteiros são movidos entre RAM e disco quando há pressão | Rodar mais processos do que cabem em RAM | Aumenta o número de processos suportados | Trocar um processo inteiro custa caro (segundos para processos grandes); todo o processo fica parado | Sozinho não escala — base para técnicas mais finas (paginação) |
| **Paginação** | Espaço virtual e físico divididos em blocos de tamanho fixo (páginas/frames); qualquer página vai em qualquer frame | Eliminar fragmentação externa e permitir alocação não-contígua | Sem fragmentação externa; permite memória virtual e proteção fina; troca por página em vez de processo inteiro | Pequena fragmentação interna (última página meio vazia); overhead da tabela de páginas; TLB miss custa | Exige suporte de hardware (MMU); tabelas grandes precisam ser hierárquicas |
| **Segmentação** | Memória vista como conjunto de segmentos lógicos (código, dados, pilha) de tamanho variável | Refletir a estrutura lógica do programa diretamente | Compartilhamento e proteção naturais por segmento (ex.: código compartilhado read-only) | Fragmentação externa entre segmentos; lógica mais complexa | Praticamente abandonada como técnica única; combinada com paginação em sistemas modernos |

## Detalhamento de cada técnica

### 1. Alocação contígua

```text
RAM:  ┌─────────────────────────────────────────┐
      │   SO   │  P1  │            P2           │
      └─────────────────────────────────────────┘
       (base + limite por processo, em hardware)
```

- Modelo dos primeiros sistemas mono-programados
- Proteção feita por registradores base/limite: qualquer endereço fora do intervalo → erro
- Não suporta múltiplos processos simultâneos de forma natural

### 2. Partições fixas

```text
RAM:  ┌──────┬──────────┬──────┬────────────┬─────────┐
      │  SO  │   P0(8M) │  P1  │   P2(16M)  │  P3(8M) │
      └──────┴──────────┴──────┴────────────┴─────────┘
              ↑ 8M      ↑ 4M    ↑ 16M        ↑ 8M
```

- Cada partição tem um tamanho fixo
- Processo de 3 MB alocado numa partição de 8 MB → desperdiça 5 MB (**fragmentação interna**)
- Foi a abordagem do **OS/360 MFT** (IBM, anos 60)

### 3. Partições variáveis

```text
Tempo 0:   ┌──────┬──────┬──────────┬──────┐
           │  SO  │  A   │     B    │  C   │
           └──────┴──────┴──────────┴──────┘

B termina:
Tempo 1:   ┌──────┬──────┬──────────┬──────┐
           │  SO  │  A   │  (livre) │  C   │   ← buraco de tamanho B
           └──────┴──────┴──────────┴──────┘

D pequeno chega, F grande chega:
Tempo 2:   ┌──────┬──────┬───┬──┬────┬──────┐
           │  SO  │  A   │ D │  │ F  │   C  │   ← buracos pequenos: fragmentação externa
           └──────┴──────┴───┴──┴────┴──────┘
```

- Estratégias de alocação: **first-fit**, **best-fit**, **worst-fit**
- Para eliminar buracos: **compactação** — mover todos os processos para um lado, juntando o espaço livre (custoso, exige relocação)

### 4. Swapping

```text
RAM:  ┌─────┬─────┬─────┐           Disco (área de swap):
      │ SO  │ P1  │ P2  │  ←─────→  ┌─────────┐
      └─────┴─────┴─────┘           │   P3    │
                                    │   P4    │
                                    └─────────┘
       (P3 sai pra entrar P5)
```

- Sozinho, não é uma estratégia de alocação — é um mecanismo para **estender RAM**
- Combinado com paginação, vira a base da memória virtual moderna (swap em granularidade de página)

### 5. Paginação

```text
Memória virtual do processo P:      Memória física (RAM):
┌─────────────┐                     ┌─────────┬─────────┬─────────┐
│ Página 0 ───┼──── PTE ─────────→  │ Frame   │ Frame   │ Frame   │
│ Página 1 ───┼──── PTE ─────────→  │   17    │   42    │    5    │
│ Página 2 ───┼──── PTE ─────→ disco│         │         │         │
│ Página 3 ───┼──── PTE ─────────→  └─────────┴─────────┴─────────┘
└─────────────┘
```

- Tamanho típico de página: **4 KiB** (também há *huge pages* de 2 MiB e 1 GiB em x86-64)
- Tabela de páginas é hierárquica (4 ou 5 níveis no x86-64)
- TLB acelera traduções recentes
- Permite memória virtual com swap fino, COW, mmap, sharing

### 6. Segmentação

```text
Espaço lógico do processo:           Memória física:
┌──────────────┐                     ┌─────────────────┐
│ Segmento     │                     │  segmento dados │
│   de código  │──── seletor ────→   │                 │
├──────────────┤                     ├─────────────────┤
│ Segmento     │                     │ segmento código │
│   de dados   │                     │                 │
├──────────────┤                     ├─────────────────┤
│ Segmento     │                     │ segmento stack  │
│   de pilha   │                     │                 │
└──────────────┘                     └─────────────────┘
```

- Cada segmento tem sua base e limite separados
- Mais natural do ponto de vista do programador (um segmento ≈ uma estrutura lógica)
- x86 tinha suporte completo (CS, DS, SS), praticamente desativado em x86-64
- Hoje, **segmentação + paginação** combinadas existem só conceitualmente (cada VMA do Linux pode ser visto como um "segmento")

## Evolução histórica resumida

```text
Anos 50    ────  Alocação contígua (mono-programação)
Anos 60    ────  Partições fixas, partições variáveis, swapping (multi-programação)
Anos 70    ────  Segmentação + paginação (memória virtual)
Anos 80–   ────  Paginação por demanda + TLB + COW (modelo atual)
Anos 2000+ ────  NUMA, huge pages, memory tiering, transparent COW
```

## Pontos a evidenciar no visual

- Quadro comparativo em formato de **tabela visual** (6 colunas × 5 linhas), com cores diferenciando técnicas obsoletas (cinza pálido) de técnicas modernas (laranja para paginação)
- Mini-diagrama ao lado de cada técnica ilustrando o conceito principal
- Setas indicando "evolução" entre as técnicas (uma resolveu o problema da anterior)
- Marcar com selo "técnica em uso hoje" as que sobreviveram: paginação (sozinha) e paginação + elementos de segmentação (VMAs)
