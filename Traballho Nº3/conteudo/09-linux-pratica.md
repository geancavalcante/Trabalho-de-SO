# Seção 9 — Linux na Prática: Como o Kernel Gerencia Memória de Verdade

> Artefato visual: **Bloco "Como o Linux gerencia memória na prática"** (artefato obrigatório nº 6)

Esta seção tira os conceitos do plano teórico e mostra como o Linux concretamente implementa cada um deles. Tudo aqui pode ser observado em um Linux rodando.

## 1. Memória física organizada em zonas

O kernel não trata RAM como um pool homogêneo. Divide em **zonas** porque diferentes regiões físicas têm propriedades diferentes (limites de hardware, acesso DMA, NUMA).

| Zona | Faixa típica (x86-64) | Para que serve |
|---|---|---|
| **ZONE_DMA** | 0 – 16 MB | Dispositivos legacy que só endereçam 24 bits |
| **ZONE_DMA32** | 16 MB – 4 GB | Dispositivos DMA de 32 bits |
| **ZONE_NORMAL** | acima de 4 GB | Uso geral do kernel e processos |
| **ZONE_MOVABLE** | (configurável) | Páginas que o kernel pode mover (facilita huge pages, hotplug) |

Em máquinas **NUMA** (multi-socket), cada nó tem seu próprio conjunto de zonas. Kernel tenta alocar páginas no nó local ao processo.

```bash
# Ver zonas e ocupação
cat /proc/zoneinfo

# Ver topologia NUMA
numactl --hardware
```

## 2. Alocação e liberação de memória física

### Para o kernel

| Mecanismo | Quando usar | Granularidade |
|---|---|---|
| **Buddy allocator** | Base de tudo — aloca em potências de 2 de páginas | 1, 2, 4, 8 ... páginas contíguas |
| **Slab / SLUB** | Objetos pequenos do kernel (struct inode, dentry, task_struct) | objeto a objeto, pool por tipo |
| **kmalloc()** | Alocação contígua física pequena | bytes a algumas páginas |
| **vmalloc()** | Alocação virtualmente contígua, fisicamente espalhada | qualquer tamanho |

### Para processos (userspace)

| Syscall | O que faz |
|---|---|
| `brk()` / `sbrk()` | Move o "topo do heap"; legado, usado pelo malloc para blocos pequenos |
| `mmap()` | Cria nova região no espaço virtual (anônima ou mapeada de arquivo) |
| `munmap()` | Desmapeia |
| `madvise()` | Dá dicas ao kernel ("vou usar sequencial", "pode descartar essa região") |

`malloc()` da glibc combina ambos: pedidos pequenos via `brk`, pedidos grandes (>128 KB por padrão) via `mmap` anônimo.

## 3. Memória virtual e VMAs

Cada processo tem uma lista de **VMAs** (*Virtual Memory Areas*) — uma para cada faixa contígua de endereços com mesmas permissões e mesmo "respaldo":

```text
struct vm_area_struct (simplificado):
  vm_start       endereço virtual inicial
  vm_end         endereço virtual final
  vm_flags       VM_READ | VM_WRITE | VM_EXEC | VM_SHARED ...
  vm_file        se mapeia um arquivo, ponteiro para ele
  vm_pgoff       offset dentro do arquivo
  vm_ops         operações (fault handler customizado)
```

Quando ocorre um page fault, o kernel localiza a VMA que contém o endereço falho e despacha o handler apropriado. Conteúdo do `/proc/<pid>/maps` é literalmente uma lista das VMAs.

## 4. Page cache — o ponto central

O **page cache** é a maior consumidor de RAM em um Linux saudável. Ele armazena em memória páginas de arquivos lidas do disco — para que leituras subsequentes sejam servidas instantaneamente.

```text
                  Aplicação
                     │
                  read() / write()
                     │
                     ▼
                ┌──────────────┐
                │  Page cache  │ ← se a página está aqui: leitura é μs
                └──────┬───────┘
                       │
                  miss │ flush
                       ▼
                  ┌────────┐
                  │ Disco  │ ← se não: ms
                  └────────┘
```

Características:

- **Memória "free" do `free -h`**: o kernel mostra muito como `buff/cache` porque o page cache é "elástico" — sob pressão, o kernel libera essas páginas em milissegundos
- `mmap()` de arquivo usa diretamente o page cache (sem cópia extra)
- `write()` em arquivo atualiza o page cache imediatamente; gravação real no disco é diferida (`pdflush`, agora `writeback` workers)
- Dirty pages = páginas que foram escritas mas ainda não persistidas. Limites em `/proc/sys/vm/dirty_*`

## 5. Parâmetros do subsistema VM (`/proc/sys/vm/`)

Parâmetros expostos no `/proc/sys/vm` controlam o comportamento do gerenciador de memória virtual:

| Parâmetro | Função | Default típico |
|---|---|---|
| `swappiness` | Tendência a mandar páginas anônimas para swap (0–100) | 60 |
| `vfs_cache_pressure` | Tendência a recuperar memória do dentry/inode cache | 100 |
| `min_free_kbytes` | Memória mínima que kswapd mantém livre | (calculado) |
| `dirty_ratio` | % de RAM até bloquear escritas | 20 |
| `dirty_background_ratio` | % de RAM para começar flush em background | 10 |
| `overcommit_memory` | Política de overcommit (0=heurística, 1=sempre permitir, 2=estrita) | 0 |
| `overcommit_ratio` | Quando =2, % de RAM+swap permitida em commit | 50 |
| `panic_on_oom` | Pânica ou só mata em OOM | 0 |

Documentação completa: `Documentation/admin-guide/sysctl/vm.rst` no código-fonte do kernel.

## 6. Ciclo de vida de um processo do ponto de vista da memória

```text
fork()                                        exec("/usr/bin/programa")
─────                                         ────────────────────────
1. Filho cria nova task_struct                1. Nova VMAs construídas a partir do ELF
2. Tabelas de páginas DUPLICADAS              2. Antigas VMAs liberadas
   (mas tudo apontando aos                    3. Espaço virtual zerado para
    mesmos frames físicos)                       o conteúdo do novo binário
3. TODAS as páginas marcadas R-O              4. Nenhuma página é carregada
4. COW: na primeira escrita, kernel              ainda — paginação sob demanda
   duplica AQUELA página específica           5. Primeiro acesso ao .text gera
                                                 page fault, kernel lê do ELF
```

### exit()

Quando o processo termina:

1. Kernel percorre as VMAs e desfaz cada mapeamento
2. Páginas **anônimas** (heap, stack) liberadas para o buddy
3. Páginas de arquivo (mmap de .so, .text): apenas decrementa contador de referência; ficam no page cache (outros processos podem usar; eventualmente recuperadas)
4. Tabelas de páginas liberadas
5. `task_struct` liberada via slab

## 7. OOM Killer

Quando o sistema esgota memória **e swap**, o kernel não consegue mais entregar páginas. Em vez de travar, dispara o **OOM Killer**:

1. Cada processo recebe um *score* (`/proc/<pid>/oom_score`) baseado em uso de RAM, idade, prioridade
2. Score pode ser ajustado por `/proc/<pid>/oom_score_adj` (-1000 = imune)
3. O processo de maior score é morto com `SIGKILL`
4. Logado em `dmesg` com a string `Out of memory: Killed process`

## Convenção do bloco visual (5 campos)

### Bloco — Subsistema VM do Linux  *(laranja)*

- **Nome:** Subsistema de Memória Virtual do Kernel Linux
- **Função:** Implementar paginação sob demanda, gerenciar page cache, fazer swap, atender alocações de processos e do próprio kernel.
- **Entrada:** Page faults, syscalls de memória (`mmap`/`brk`/`munmap`), eventos de pressão, dirty pages.
- **Saída:** Páginas alocadas/liberadas, I/O de swap, métricas em `/proc/meminfo`, `/proc/vmstat`.
- **Risco / Limitação:** Sob pressão extrema entra em *thrashing* ou aciona OOM killer; configurações erradas (swappiness, overcommit) degradam desempenho ou causam falhas inesperadas.

## Pontos a evidenciar no visual

- Bloco "Linux na prática" com sub-blocos: **Zonas**, **Buddy/Slab**, **VMAs**, **Page Cache**, **Swap**, **OOM**
- Page cache no centro, com setas: ↑ aplicações (read/write/mmap), ↓ disco
- Caixa lateral com 3–4 parâmetros importantes do `/proc/sys/vm/`
- Fluxo de `fork`+`exec` na lateral, mostrando COW e nova VM
- Cor **laranja** dominante (kernel); **cinza** nas pontas que tocam disco
