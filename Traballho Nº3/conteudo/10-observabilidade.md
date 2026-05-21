# Seção 10 — Observabilidade e Monitoramento

> Artefato visual: **Bloco de Observabilidade** (artefato obrigatório nº 7)

## Por que observabilidade importa

Memória é o recurso mais difícil de raciocinar a olho. Diferentemente de CPU (vejo `top`), disco (vejo `df`/`iostat`) ou rede (vejo `iftop`), memória esconde sua complexidade: cache parece "livre", swap parece "usado", processo parece "consumindo muito" quando na verdade compartilha bibliotecas.

As ferramentas abaixo são o caminho oficial para diagnosticar problemas. Cada uma mostra uma faceta diferente.

## Mapa rápido das ferramentas

| Ferramenta / arquivo | Escopo | O que mostra | Quando usar |
|---|---|---|---|
| `free` | Sistema inteiro | RAM total/usada/livre, buff/cache, swap | "Quanto de RAM o sistema tá usando?" |
| `top` | Processos | Lista interativa: CPU, RES, VIRT, SHR, %MEM | "Quem está consumindo memória?" |
| `htop` | Processos | Versão amigável do top: cores, árvore, scroll, kill | Mesma pergunta, com UX melhor |
| `vmstat` | Sistema (séries) | Paginação, swap, I/O, CPU em intervalos | "Há paginação anormal? Swap-in/out?" |
| `/proc/<pid>/maps` | Processo específico | Cada VMA: faixa, permissões, arquivo, offset | "O que está mapeado no espaço desse processo?" |
| `/proc/<pid>/smaps` | Processo específico | maps + tamanho, RSS, PSS, swap por VMA | "Quanto desse mapeamento está realmente em RAM?" |
| `/proc/meminfo` | Sistema (detalhado) | Dezenas de contadores: cache, slab, anon, mapped, dirty | Diagnóstico fino |
| `pmap <pid>` | Processo específico | Resumo legível dos mapas | Alternativa amigável ao /proc/maps |
| `pidstat -r` | Por processo (séries) | Page faults por segundo por processo | "Que processo está paginando muito?" |
| `sar -B` / `sar -r` | Histórico | Métricas de paginação ao longo do tempo | "Quando começou a degradar?" |

## Detalhamento de cada ferramenta

### `free`

```bash
$ free -h
               total        used        free      shared  buff/cache   available
Mem:            15Gi        4.2Gi       2.1Gi       320Mi        9.4Gi        11Gi
Swap:          2.0Gi          0B       2.0Gi
```

| Coluna | Significado |
|---|---|
| `total` | RAM total instalada |
| `used` | Em uso por processos + cache não-recuperável |
| `free` | Realmente ociosa (raro ser alto em sistema saudável) |
| `shared` | Memória compartilhada (tmpfs, shmget) |
| `buff/cache` | Page cache + buffers (recuperável sob pressão!) |
| `available` | **Estimativa do quanto cabe alocar sem swap** — é a métrica que importa |

**Erro clássico:** olhar `free` baixo e achar que o sistema está sem memória. O número que importa é **`available`**.

---

### `top` / `htop`

Colunas relevantes de memória:

| Coluna | Significado |
|---|---|
| `VIRT` | Tamanho **virtual** total do processo (espaço de endereçamento que ele *poderia* tocar; inclui mmap não tocado, libs, etc.) |
| `RES` | **Resident Set Size** — RAM física que o processo está usando *agora* |
| `SHR` | Memória compartilhada com outros processos (típico: bibliotecas) |
| `%MEM` | RES dividido pela RAM total |

**Cuidado:** somar `RES` de todos os processos pode passar do total da RAM, porque bibliotecas compartilhadas são contadas em cada um. **PSS** (no smaps) resolve isso.

---

### `vmstat`

```bash
$ vmstat 1
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 1  0      0 218764  20012 9412124    0    0    12     5  150  300  3  1 96  0  0
```

Colunas-chave para diagnóstico de memória:

| Coluna | Significado | Sinal de alarme |
|---|---|---|
| `si` | Swap-in (KB/s lendo de swap) | Qualquer valor > 0 sustentado é ruim |
| `so` | Swap-out (KB/s escrevendo em swap) | Idem |
| `bi`/`bo` | Block I/O | Alto correlacionado com `si`/`so` = thrashing |
| `wa` (CPU) | Tempo aguardando I/O | Alto + so/si alto = thrashing confirmado |
| `free` | RAM livre | Cair perto de zero junto com cache caindo = pressão |

---

### `/proc/<pid>/maps`

```bash
$ cat /proc/$$/maps | head -5
55a9b8a00000-55a9b8a23000 r-xp 00000000 fd:00 1234567  /usr/bin/bash
55a9b8c22000-55a9b8c26000 r--p 00022000 fd:00 1234567  /usr/bin/bash
55a9b8c26000-55a9b8c2f000 rw-p 00026000 fd:00 1234567  /usr/bin/bash
55a9b8c2f000-55a9b8c54000 rw-p 00000000 00:00 0        [heap]
7f12a4000000-7f12a4022000 rw-p 00000000 00:00 0
```

Formato: `inicio-fim permissoes offset dispositivo inode caminho`

Permissões: `r-x` = código; `r--` = dados constantes; `rw-` = dados/heap/stack; `p` = privado (com COW); `s` = compartilhado.

Caminhos especiais:

- `[heap]` — heap do processo
- `[stack]` — stack principal (cada thread também tem o seu)
- `[vdso]` — vDSO, biblioteca compartilhada injetada pelo kernel (otimização de syscalls)
- `[vvar]` — variáveis expostas pelo kernel
- `[anon:<nome>]` — mapeamento anônimo nomeado (`prctl PR_SET_VMA`)

---

### `/proc/<pid>/smaps`

Mesma informação do `maps`, **mais** para cada VMA:

```text
Size:               4096 kB    ← tamanho virtual reservado
Rss:                2048 kB    ← residente em RAM
Pss:                 512 kB    ← residente proporcional (rateado entre quem compartilha)
Shared_Clean:       1024 kB
Shared_Dirty:          0 kB
Private_Clean:        64 kB
Private_Dirty:      1024 kB
Swap:                512 kB    ← está em swap
```

**PSS é a métrica mais honesta** para somar "uso real" entre processos: cada página compartilhada é dividida entre os N processos que a usam.

---

### `/proc/meminfo`

Painel completo do estado da memória:

```text
MemTotal:       16284444 kB
MemFree:         2156820 kB
MemAvailable:   11463724 kB
Buffers:           20012 kB
Cached:          8923108 kB    ← page cache de arquivos
SwapCached:            0 kB
Active:          5234100 kB
Inactive:        4012348 kB
AnonPages:       3245620 kB    ← páginas anônimas (heap, stack)
Mapped:           876544 kB    ← arquivos mapeados (mmap)
Shmem:            123456 kB
Slab:             456123 kB    ← objetos do kernel
SwapTotal:       2097148 kB
SwapFree:        2097148 kB
Dirty:                88 kB    ← páginas modificadas aguardando flush
Writeback:             0 kB    ← páginas sendo flushadas agora
```

## Receitas práticas de diagnóstico

| Sintoma | Comando |
|---|---|
| "Quanto de memória sobra?" | `free -h` (olhe `available`) |
| "Quem tá comendo memória?" | `top` ordenado por `%MEM` (tecla `M`) ou `htop` |
| "Esse processo específico, o que tem mapeado?" | `cat /proc/<pid>/maps` ou `pmap <pid>` |
| "Quanto esse processo realmente usa, descontando shared?" | `grep Pss /proc/<pid>/smaps \| awk '{sum+=$2} END {print sum " kB"}'` |
| "Sistema lento, será swap?" | `vmstat 1` — olhe `si` e `so` |
| "Quem está paginando?" | `pidstat -r 1` |
| "Histórico do dia" | `sar -B` (page faults), `sar -r` (uso de RAM) |

## Convenção do bloco visual (5 campos)

### Bloco — Observabilidade  *(verde para ferramentas userspace; cinza para arquivos do kernel)*

- **Nome:** Conjunto de ferramentas de observabilidade de memória do Linux
- **Função:** Expor o estado do subsistema de memória para diagnóstico de capacidade e desempenho.
- **Entrada:** Leituras dos contadores do kernel via `/proc` e syscalls específicas.
- **Saída:** Métricas legíveis: RSS, PSS, swap, paginação por segundo, ocupação por processo e por VMA.
- **Risco / Limitação:** Interpretação errada das métricas (ex.: assumir que `buff/cache` é "memória perdida") leva a diagnóstico equivocado.

## Pontos a evidenciar no visual

- Bloco em formato de painel com **6 ícones** (uma por ferramenta)
- Setas saindo de cada ferramenta apontando para o bloco que ela "lê" (top → processos; vmstat → kernel; smaps → VMAs)
- Tabela compacta com "quando usar cada uma"
- Destaque **vermelho** para a armadilha clássica: confundir `buff/cache` com memória usada
