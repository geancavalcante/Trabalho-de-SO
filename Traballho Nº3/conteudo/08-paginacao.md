# Seção 8 — Paginação e Memória Virtual

> Artefato visual: **Páginas, Quadros, Page Fault e Substituição**

## Conceitos fundamentais

| Termo | Significado |
|---|---|
| **Página** | Unidade fixa de endereçamento **virtual** (tamanho típico: 4 KiB no Linux x86-64) |
| **Quadro / Frame** | Unidade fixa de endereçamento **físico**, mesmo tamanho da página |
| **Tabela de páginas** | Estrutura que mapeia cada página virtual em um frame físico (ou marca como ausente) |
| **PTE** (Page Table Entry) | Uma linha da tabela: contém o número do frame + bits de controle |
| **TLB** (Translation Lookaside Buffer) | Cache de hardware para as traduções mais recentes |
| **Page fault** | Exceção gerada quando a tradução falha (página ausente, permissão inválida) |
| **Paginação sob demanda** | Páginas só são alocadas em RAM quando efetivamente acessadas |
| **Substituição de página** | Política do kernel para escolher qual frame liberar quando precisa de espaço |

## Páginas e quadros — quebrando o requisito de contiguidade

```text
Memória virtual de um processo            Memória física (RAM)
(contígua do ponto de vista lógico)

Páginas:                                  Frames:
┌────────────┐                            ┌────────────┐
│  Página 0  │────PTE────────────────────→│  Frame 17  │
├────────────┤                            ├────────────┤
│  Página 1  │────PTE────────┐            │  Frame 18  │
├────────────┤               │            ├────────────┤
│  Página 2  │────PTE────────┼──────┐     │  Frame 19  │ ← (livre)
├────────────┤               │      │     ├────────────┤
│  Página 3  │────PTE────────┼──────┼────→│  Frame 20  │
├────────────┤               │      │     ├────────────┤
│  Página 4  │────PTE───→ disk│     │     │  Frame 21  │ ← (de outro processo)
└────────────┘                │     │     ├────────────┤
                              │     └────→│  Frame 22  │
                              └──────────→│  Frame 23  │
                                          └────────────┘
```

A página 4 está mapeada, mas o conteúdo está em disco/swap. PTE marca **P=0**. Acesso a ela → page fault → kernel traz do disco → mapeia em um frame livre → atualiza PTE.

## Estrutura de uma PTE (Linux x86-64)

```text
Bit  63        52 51                          12 11        0
     ┌──────────┬──────────────────────────────┬───────────┐
     │ NX, AVL  │      Número do frame         │ Bits de   │
     │ ...      │      (40 bits = 4 TB)        │ controle  │
     └──────────┴──────────────────────────────┴───────────┘

Bits de controle (12 bits inferiores):
  P    Present       (página está em RAM?)
  R/W  Read/Write    (permite escrita?)
  U/S  User/Supervisor (acessível em modo usuário?)
  PWT  Write-through (política de cache)
  PCD  Cache disable
  A    Accessed      (foi lida/escrita?)
  D    Dirty         (foi escrita?)
  PS   Page Size     (página normal ou huge?)
  G    Global        (não invalidar TLB em troca de processo)
```

## Tabela de páginas hierárquica (x86-64, 4 níveis)

```text
Endereço virtual de 48 bits:

  47       39 38       30 29       21 20       12 11        0
  ┌─────────┬───────────┬───────────┬───────────┬───────────┐
  │  PGD    │   PUD     │   PMD     │   PTE     │  Offset   │
  │  idx    │   idx     │   idx     │   idx     │           │
  └─────────┴───────────┴───────────┴───────────┴───────────┘
       │          │           │           │
       ▼          ▼           ▼           ▼
   tabela     tabela       tabela     tabela
   nível 4    nível 3      nível 2    nível 1     ┌──────────┐
   (PGD)      (PUD)        (PMD)      (PT)  ─────→│  Frame   │
                                                  └──────────┘

   CR3 ──→ PGD raiz                              + offset
                                                  = endereço físico
```

- Cada nível indexa 9 bits → 512 entradas por tabela
- Cada tabela cabe em uma única página (8 bytes × 512 = 4 KiB)
- Tabelas vazias **não são criadas** — economiza muita memória (a maior parte do espaço virtual fica não-mapeada)
- 4 níveis cobrem 256 TiB; CPUs recentes têm **5 níveis** (PML5), cobrindo 128 PiB

## Paginação sob demanda

Páginas **não** são carregadas até que o processo realmente as acesse. Vantagens:

- Programa grande inicia rápido (só carrega a página inicial do `main`)
- Páginas nunca usadas (código de tratamento de erro raríssimo, p.ex.) nunca ocupam RAM
- BSS e heap fresh: kernel mapeia uma **zero-page** compartilhada de truque (read-only); só duplica quando o processo escreve (COW)

```text
exec("/usr/bin/programa")
  │
  ▼
1. Kernel cria espaço virtual com VMAs apontando para o arquivo
2. NENHUMA página do programa é carregada ainda
3. CPU tenta executar a primeira instrução em vaddr 0x400000
4. Page fault! (P=0)
5. Kernel: "ah, essa VMA aponta pra /usr/bin/programa offset 0"
6. Kernel lê 1 página do arquivo, mapeia em um frame, retoma execução
7. Execução prossegue até o próximo acesso a página não-carregada → repete
```

## Substituição de página (page replacement)

Quando a RAM enche e o kernel precisa de um frame livre, ele escolhe uma vítima.

### Algoritmos clássicos

| Algoritmo | Como decide | Qualidade |
|---|---|---|
| **FIFO** | Substitui a página mais antiga (que entrou primeiro) | Ruim — pode tirar páginas ainda muito usadas |
| **LRU** | Substitui a menos recentemente usada (Least Recently Used) | Boa, mas implementação exata é cara |
| **LRU aproximado / Clock** | Bit "acessado" + ponteiro circular; revisa em rodada | Boa qualidade, custo aceitável — usado em produção |
| **Working Set** | Mantém na RAM apenas as páginas usadas no intervalo recente | Conceito teórico, base para variantes práticas |
| **LFU** | Menos frequentemente usada | Sofre com mudança de fase do programa |

### O que o Linux faz

O kernel usa **duas listas LRU** por zona: *active list* e *inactive list*. Páginas que envelhecem migram de uma para outra. Páginas na *inactive* são candidatas a sair. Há também **kswapd**, thread em background que faz reclaim antecipado.

## Page fault — os três sabores (revisão)

```text
                          page fault
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
   MINOR                   MAJOR                  INVÁLIDO
   ─────────               ─────────              ─────────
   página existe           página precisa         acesso fora
   conceitualmente,        vir de disco           do espaço
   só falta mapear         (swap, mmap            permitido
                            de arquivo)
   custo: μs               custo: ms              custo: morte
                                                  do processo
                                                  (SIGSEGV)
```

## Thrashing — o ponto de colapso

Quando o conjunto de páginas ativas dos processos (*working set total*) excede a RAM:

1. Kernel manda página para swap
2. Algum processo logo precisa dela de volta → traz de swap
3. Para trazer, tem que mandar outra para swap
4. Sistema gasta mais tempo paginando do que executando

Sintoma: CPU baixa, disco 100%, sistema lento ou travado. Resposta: matar processos (OOM killer) ou adicionar RAM.

## Pontos a evidenciar no visual

- Diagrama lado-a-lado de **memória virtual** (esquerda, verde, contígua) vs **memória física** (direita, com frames espalhados)
- Setas indo da página virtual para frame físico (algumas atravessando, outras indo para disco — em cinza)
- Mini-diagrama da estrutura hierárquica da tabela de páginas (4 níveis)
- Quadro destacado em **vermelho**: page fault e suas variantes
- Cor **roxa** para tudo que envolve tradução (PTE, TLB, MMU)
- Cor **cinza** para swap e disco
