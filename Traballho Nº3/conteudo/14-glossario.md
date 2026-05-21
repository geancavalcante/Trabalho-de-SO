# Glossário Técnico

> Artefato obrigatório nº 8

Ordenado alfabeticamente. Os termos em inglês são mantidos quando consagrados na literatura técnica.

---

**ASLR** *(Address Space Layout Randomization)* — técnica de proteção que randomiza as posições de stack, heap, bibliotecas e até do executável a cada execução, dificultando exploits que dependem de endereços fixos.

**BSS** *(Block Started by Symbol)* — segmento de memória de um processo que contém variáveis globais e estáticas não inicializadas. Não ocupa espaço no executável (ELF guarda só o tamanho), só é alocado e zerado em RAM no carregamento.

**Buddy allocator** — algoritmo do kernel Linux que aloca páginas físicas em potências de 2. Quando libera, tenta fundir blocos "irmãos" adjacentes para reduzir fragmentação externa.

**Cache (de CPU)** — memória pequena e rápida (L1, L2, L3) entre os registradores e a RAM. Não confundir com page cache. Gerenciada por hardware.

**Context switch** — troca de processo (ou thread) executando na CPU. Inclui salvar/restaurar registradores, e trocar o CR3 (ponteiro da tabela de páginas), o que invalida parte ou toda a TLB.

**COW** *(Copy-on-Write)* — técnica em que regiões de memória compartilhadas só são duplicadas no momento em que alguém tenta escrever. Base do `fork()` eficiente no Linux.

**CR3** — registrador do x86/x86-64 que aponta para a raiz da tabela de páginas do processo corrente. Trocado em cada context switch.

**Demand paging** — paginação sob demanda. Páginas só são alocadas em RAM quando o processo realmente as acessa, não no momento da requisição.

**DMA** *(Direct Memory Access)* — mecanismo pelo qual dispositivos acessam RAM diretamente, sem passar pela CPU. Exige cuidado especial (regiões reservadas, IOMMU em sistemas modernos).

**Dirty page** — página de memória cujo conteúdo foi modificado e ainda não foi persistido em disco (no caso de cache de arquivo) ou ainda não foi escrito em swap.

**Frame** *(quadro)* — unidade fixa de endereçamento físico. Mesmo tamanho da página virtual (4 KiB no Linux x86-64 por padrão).

**Fragmentação externa** — desperdício de memória causado por espaços livres pequenos e não-contíguos entre blocos alocados. Pode tornar inviável atender uma alocação grande mesmo com RAM total disponível.

**Fragmentação interna** — desperdício dentro de um bloco já alocado (ex.: última página parcialmente usada). Limitado e previsível.

**Huge page** — página de tamanho maior que o padrão (2 MiB ou 1 GiB no x86-64). Reduz pressão na TLB para regiões grandes, mas exige blocos contíguos físicos.

**KPTI** *(Kernel Page Table Isolation)* — mitigação introduzida após Meltdown. Mantém tabelas de páginas separadas para userspace e kernel, evitando que CPU especulativa exponha endereços do kernel.

**MMU** *(Memory Management Unit)* — unidade de hardware (dentro da CPU) responsável por traduzir endereços virtuais em físicos, consultando a tabela de páginas e aplicando permissões.

**Mmap** *(memory map)* — syscall que mapeia uma região do espaço virtual a um arquivo ou a memória anônima. Base do carregamento de bibliotecas, leitura zero-cópia de arquivos e alocações grandes.

**Modo kernel** *(modo privilegiado, ring 0)* — modo de execução em que a CPU pode executar todas as instruções, inclusive privilegiadas (alterar CR3, fazer I/O direto, etc.). Onde o kernel roda.

**Modo usuário** *(ring 3)* — modo restrito em que a CPU só executa instruções não-privilegiadas e só pode acessar páginas marcadas U=1. Onde processos comuns rodam.

**NUMA** *(Non-Uniform Memory Access)* — arquitetura em que múltiplos sockets de CPU têm bancos de RAM locais; acesso à RAM remota é mais lento. Kernel tenta alocar páginas no nó local do processo.

**NX bit** *(No Execute)* — bit na PTE que marca a página como não-executável. Mitiga ataques que injetam shellcode em região de dados.

**OOM killer** *(Out-Of-Memory killer)* — componente do kernel que mata processos quando RAM e swap esgotaram, evitando travamento total. Escolhe vítima por *oom_score*.

**Overcommit** — prática de prometer mais memória virtual aos processos do que existe fisicamente disponível. Linux permite por padrão (`vm.overcommit_memory=0`).

**Page** *(página)* — unidade fixa de endereçamento virtual. 4 KiB por padrão no Linux x86-64.

**Page cache** — região da RAM usada pelo kernel para cachear conteúdo de arquivos do disco. Elástica: cede sob pressão de memória.

**Page fault** — exceção gerada pela MMU quando a tradução de um endereço virtual falha. Pode ser minor (página existe, só faltava mapear), major (precisa vir de disco) ou inválida (acesso não permitido — SIGSEGV).

**Page table** *(tabela de páginas)* — estrutura de dados que mapeia cada página virtual a um frame físico (ou marca como ausente). No x86-64 é hierárquica de 4 ou 5 níveis.

**PSS** *(Proportional Set Size)* — métrica que mede o uso de memória de um processo dividindo cada página compartilhada proporcionalmente entre os processos que a compartilham. Mais honesta que RSS para somatórios.

**PTE** *(Page Table Entry)* — entrada individual na tabela de páginas. Contém o número do frame físico e bits de controle (P, R/W, U/S, A, D, NX, etc.).

**RAM** *(Random Access Memory)* — memória principal, volátil. Onde processos efetivamente rodam.

**Registrador** — célula de armazenamento dentro da CPU acessível no mesmo ciclo de clock. Em quantidade pequena (dezenas), gerenciados pelo compilador.

**RSS** *(Resident Set Size)* — quantidade de memória física que um processo está usando no momento. Inclui bibliotecas compartilhadas (que aparecem em todos os processos que as usam — atenção ao somar).

**Segmentação** — técnica de gerenciamento que divide memória em segmentos lógicos de tamanho variável (código, dados, pilha). Combinada com paginação em alguns sistemas antigos; praticamente abandonada no x86-64.

**Slab allocator** — alocador do kernel para objetos pequenos e frequentemente usados (struct inode, dentry). Mantém pools por tipo.

**Stack** *(pilha)* — região do espaço virtual onde ficam os frames de chamada de função: parâmetros, locais, endereço de retorno. Cresce de endereços altos para baixos.

**Swap** — área de armazenamento secundário (partição ou arquivo) usada para guardar páginas que estavam em RAM e foram escolhidas para sair, estendendo a memória disponível.

**Swappiness** — parâmetro do kernel (`vm.swappiness`) que controla a tendência de mandar páginas anônimas para swap. Vai de 0 a 100.

**Syscall** *(chamada de sistema)* — interface pela qual processos em userspace pedem serviços ao kernel. Envolve troca de modo (usuário → kernel), com custo de centenas de ciclos.

**Thrashing** — estado em que o sistema gasta mais tempo paginando do que executando. Ocorre quando o conjunto de páginas ativas excede a RAM.

**TLB** *(Translation Lookaside Buffer)* — cache associativo de hardware com as traduções virtuais→físicas mais recentes. Acerto em TLB = tradução em 1 ciclo; miss = page walk.

**Userspace** *(espaço do usuário)* — onde processos comuns executam, em modo usuário, com acesso restrito.

**VMA** *(Virtual Memory Area)* — descritor interno do kernel para uma região contígua do espaço virtual de um processo com mesmas permissões e mesma origem. Cada linha de `/proc/<pid>/maps` corresponde a uma VMA.

**Zona de memória** — subdivisão da RAM física feita pelo kernel para refletir limites de hardware: ZONE_DMA, ZONE_DMA32, ZONE_NORMAL, ZONE_MOVABLE.

**Zero-page** — página física toda preenchida com zeros, mantida pelo kernel. Páginas de BSS e mapeamentos anônimos novos são inicialmente mapeadas (em read-only) para ela; só duplicam quando o processo escreve.

## Pontos a evidenciar no visual

- Glossário em formato de **duas colunas** lado a lado, ou em **lista ordenada** dependendo do tamanho da página
- Negrito nos termos; texto explicativo logo em seguida
- Pode ser distribuído como apêndice no fim do design, ou como página dedicada
