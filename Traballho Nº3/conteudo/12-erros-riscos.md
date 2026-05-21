# Análise — Erros e Riscos

> Parte analítica obrigatória (item 10.2 do escopo)

Esta seção cataloga os modos clássicos de falha do subsistema de memória. Cada um tem causa identificável, impacto típico e mitigação prática.

## 1. Fragmentação

| Tipo | Onde aparece | Impacto | Mitigação |
|---|---|---|---|
| **Interna** | Última página de cada VMA; alocador userspace com size classes | Pequeno desperdício (~50% de uma página por VMA, em média) | Tamanhos de página menores; alocadores melhores |
| **Externa** | Espaço `vmalloc`, kernel reservations, alocação DMA contígua | Pode impedir alocações grandes mesmo com RAM livre | Paginação para userspace; compactação para huge pages |

**Como detectar:** `/proc/buddyinfo` mostra a distribuição de blocos livres por ordem. Se as ordens altas estão zeradas, há fragmentação externa para alocações grandes.

## 2. Swap excessivo (Thrashing)

**Causa:** working set total dos processos ativos excede a RAM disponível.

**Sintomas:**

- `vmstat` mostra `si` e `so` > 0 continuamente
- `wa` (I/O wait) alto na CPU
- Aplicações em pause longos imprevisíveis
- Sistema "trava" mas o disco trabalha frenético

**Impacto:** sistema fica praticamente inutilizável. Cada operação que tocaria memória vira I/O de disco.

**Mitigações:**

- Adicionar RAM (raiz do problema)
- Reduzir `vm.swappiness` para 10 ou menos (evita swap de processos ativos)
- Configurar `cgroups` com limites por aplicação
- Em servidores: monitorar `pidstat -r` e matar/reiniciar quem vaza

## 3. Overhead de Paginação

**Causa:** cada acesso a uma página nova exige consulta à tabela (page walk) quando TLB perde.

**Sintoma:** baixo throughput de aplicações intensivas em memória mesmo com RAM sobrando — sintoma sutil, exige `perf stat -e dTLB-load-misses,iTLB-load-misses`.

**Mitigações:**

- **Huge pages** (2 MiB / 1 GiB): uma entrada TLB cobre região 512×/262144× maior
- **Transparent Huge Pages** (THP): ativação automática
- **NUMA awareness**: alocar páginas no nó local do processo
- Layout de dados consciente de cache e TLB

## 4. Mau uso de cache

| Erro | Consequência |
|---|---|
| Drop intencional do page cache (`echo 3 > /proc/sys/vm/drop_caches`) em produção | Próximas leituras vão a disco; perda imediata de desempenho |
| Aplicação ignora `mmap()` e usa `read()` em loop em arquivo grande | Cópia extra entre kernel e userspace; pior uso da memória |
| Acessar arquivos sequencialmente sem `posix_fadvise(POSIX_FADV_SEQUENTIAL)` | Read-ahead subótimo |
| Trabalhar com arquivos enormes e marcar como "não cachear" (`O_DIRECT`) sem necessidade | Cache poderia acelerar; perde o ganho |

## 5. Falhas de proteção

| Erro do código | Sinal | Causa típica |
|---|---|---|
| Dereferência de ponteiro NULL | SIGSEGV | `*p` com `p == NULL` |
| Escrita em página read-only | SIGSEGV | `strcpy(s, "x")` onde `s` aponta para string literal |
| Stack overflow | SIGSEGV | Recursão infinita; local enorme no stack |
| Use-after-free | SIGSEGV (às vezes) ou silencioso | Acesso depois de `free()`; pior quando silencioso, abre vulnerabilidades |
| Buffer overflow | Corrupção de stack/heap | Escrita além do tamanho alocado; pode permitir execução de código |
| Acesso a memória do kernel | SIGSEGV | Tentativa de acessar `0xffff...` em modo usuário |

**Mitigações em hardware:**

- Bit NX (No Execute) — páginas de dados não executáveis
- SMAP / SMEP — kernel não pode acessar/executar páginas de usuário sem flag explícito
- ASLR — randomização do layout de endereços a cada execução

**Mitigações em software:**

- Compiladores com `-fstack-protector`, `-D_FORTIFY_SOURCE`
- AddressSanitizer / Valgrind para detectar erros antes de produção
- Linguagens com gerenciamento de memória seguro (Rust, Go)

## 6. Crescimento descontrolado de heap

**Causa:** *memory leak* — alocações sem `free()` correspondente.

**Sintomas:**

- `RES` do processo cresce continuamente, sem nunca cair
- `/proc/<pid>/status` mostra `VmRSS` aumentando
- Eventualmente: OOM kill, ou degradação por swap

**Diagnóstico:**

- `pmap <pid>` ao longo do tempo (heap crescendo)
- `valgrind --leak-check=full` em desenvolvimento
- `heaptrack`, `massif` para profiling de heap

**Cuidado:** crescimento não é sempre leak. Caches legítimos crescem até estabilizar. Diferenciador: leak cresce **sem limite**; cache cresce até um *plateau*.

## 7. Stack overflow

**Causa:** recursão profunda demais; arrays locais enormes; threads com stack limit baixo.

**Mitigação:**

- `ulimit -s` (padrão 8 MB no Linux) — ajustar se necessário
- Reescrever recursão como iteração quando possível
- Threads: `pthread_attr_setstacksize` para controlar tamanho

**Detecção:** SIGSEGV no endereço da stack, frequentemente um endereço próximo do limite inferior do segmento.

## 8. Leitura incorreta de métricas

Este risco é **operacional** mais que técnico — diagnóstico errado leva a ação errada.

| Erro de interpretação | Verdade |
|---|---|
| "Memória usada está em 90%, sistema está mal" | Page cache conta como "used"; olhe `available` |
| "Esse processo consome 500 MB (RES)" | Inclui bibliotecas compartilhadas; PSS dá visão honesta |
| "Tem 2 GB de swap usado, o sistema está paginando" | Pode ser swap *histórico*; olhe `si`/`so` para atividade *atual* |
| "Free está em 100 MB, RAM cheia!" | Em sistema saudável, free baixo é **normal** (cache enche) |
| "Vou liberar cache com `drop_caches` pra acelerar" | Faz exatamente o oposto: próximas leituras serão lentas |
| "OOM matou o processo errado" | O killer escolhe pelo `oom_score`, ajustável por `oom_score_adj` |

## 9. Riscos modernos

| Risco | Descrição |
|---|---|
| **Side-channels** (Meltdown, Spectre) | Vulnerabilidades em CPU exploram especulação para vazar memória entre privilégios. Mitigação: KPTI, microcode, IBRS — todas com custo de desempenho |
| **Rowhammer** | Acessos repetidos a uma linha de RAM podem flipar bits em linhas vizinhas. Mitigação: ECC, refresh agressivo |
| **DMA attacks** | Dispositivo via Thunderbolt/PCIe pode ler RAM diretamente. Mitigação: IOMMU, VT-d |
| **Cold boot** | RAM mantém conteúdo por segundos após desligar; chaves de cripto roubáveis. Mitigação: encriptação de RAM (SEV, TDX) |

## Pontos a evidenciar no visual

- Lista de **9 riscos** em formato de "cards" coloridos
- Cor **vermelha** para todos (tema da seção de riscos)
- Cada card: ícone, nome, causa em 1 linha, mitigação em 1 linha
- Caixa destacada para os 4 riscos modernos (mais sofisticados, menos óbvios)
