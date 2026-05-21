# Seção 1 — Visão Macro da Arquitetura da Memória

> Artefato visual: **Diagrama Macro da Arquitetura** (artefato obrigatório nº 1)

## Cadeia mínima a ser representada

```text
Hardware  →  CPU  →  MMU / TLB  →  Kernel  →  Gerência de Memória do SO  →  Processos / Aplicações  →  Ferramentas de Observação
```

O diagrama responde a cinco perguntas-chave:

| Pergunta | Resposta visual no diagrama |
|---|---|
| Quem **acessa** memória? | CPU e processos |
| Quem **traduz** endereço? | MMU (com apoio da TLB) |
| Quem **protege**? | MMU + kernel (modo privilegiado) |
| Quem **aloca**? | Kernel (subsistema de memória) |
| Quem **monitora**? | Ferramentas Linux (`free`, `top`, `vmstat`, `/proc`) |

## Blocos do diagrama (convenção 5 campos)

### Bloco 1 — Hardware  *(cor: azul)*

- **Nome:** Hardware
- **Função:** Fornecer o substrato físico que armazena bits — RAM, barramentos, controladores de memória, discos.
- **Entrada:** Endereços físicos colocados no barramento e sinais de controle (leitura/escrita).
- **Saída:** Dados lidos ou confirmação de escrita; sinais de erro de hardware (ECC, falha de barramento).
- **Risco / Limitação:** Capacidade finita, latência crescente conforme o nível (registradores < cache < RAM < disco), falhas de hardware corrompem dados.

### Bloco 2 — CPU  *(cor: azul)*

- **Nome:** CPU (núcleo de processamento)
- **Função:** Executar instruções; gerar endereços lógicos/virtuais para cada acesso a dado ou instrução.
- **Entrada:** Instruções carregadas da memória; dados de operandos.
- **Saída:** Endereços virtuais enviados à MMU; resultados de computação escritos de volta na memória.
- **Risco / Limitação:** Depende do desempenho da hierarquia de memória — *cache miss* e *page fault* paralisam a execução até o dado chegar.

### Bloco 3 — MMU / TLB  *(cor: roxo)*

- **Nome:** MMU (Memory Management Unit) + TLB (Translation Lookaside Buffer)
- **Função:** Traduzir endereço virtual em endereço físico em hardware, aplicando permissões de página.
- **Entrada:** Endereço virtual emitido pela CPU.
- **Saída:** Endereço físico correspondente, ou **exceção de page fault** quando a tradução não pode ser concluída.
- **Risco / Limitação:** TLB pequena → *TLB miss* exige varredura da tabela de páginas; tradução incorreta seria catastrófica para o isolamento.

### Bloco 4 — Kernel  *(cor: laranja)*

- **Nome:** Kernel do sistema operacional
- **Função:** Manter as tabelas de páginas, tratar page faults, alocar/liberar memória física, fazer swap, aplicar políticas de proteção, criar e destruir espaços virtuais (`fork`/`exec`/`exit`).
- **Entrada:** Interrupções e exceções vindas da MMU; chamadas de sistema vindas dos processos (`mmap`, `brk`, `munmap`, `madvise`).
- **Saída:** Atualizações nas tabelas de páginas, decisões de alocação, leitura/escrita de páginas em swap, eventual encerramento do processo (`SIGSEGV`).
- **Risco / Limitação:** Roda em modo privilegiado — bugs aqui derrubam o sistema inteiro. Decisões erradas (substituição agressiva, dimensionamento ruim de cache) destroem desempenho.

### Bloco 5 — Gerência de Memória do SO  *(cor: laranja)*

- **Nome:** Subsistema de gerência de memória (parte do kernel)
- **Função:** Implementar paginação sob demanda, page cache, zonas de memória, swap, *kmalloc*/*vmalloc*, *slab allocator*.
- **Entrada:** Requisições de páginas, eventos de pressão de memória, parâmetros de `/proc/sys/vm`.
- **Saída:** Páginas alocadas, páginas liberadas, páginas escritas em swap, métricas em `/proc/meminfo`.
- **Risco / Limitação:** Sob alta pressão de memória, pode entrar em *thrashing* (substituição contínua) ou acionar o **OOM killer**.

### Bloco 6 — Processos / Aplicações  *(cor: verde)*

- **Nome:** Processo em espaço de usuário
- **Função:** Executar o programa do usuário usando o espaço virtual fornecido pelo kernel.
- **Entrada:** Espaço de endereçamento virtual privado; permissões por região (r/w/x).
- **Saída:** Instruções executadas, dados manipulados, chamadas de sistema requisitando recursos.
- **Risco / Limitação:** Cresce sem controle (vazamento de heap, stack overflow); tentativas de acesso fora do permitido geram falha de segmentação.

### Bloco 7 — Ferramentas de Observação  *(cor: verde para userspace / cinza para arquivos do kernel)*

- **Nome:** Ferramentas de observabilidade do Linux
- **Função:** Expor o estado da memória do sistema e de processos individuais para diagnóstico.
- **Entrada:** Leituras de `/proc/meminfo`, `/proc/<pid>/maps`, `/proc/<pid>/smaps`, contadores do kernel.
- **Saída:** Métricas legíveis: RSS, PSS, swap, cache, paginação por segundo, uso por processo.
- **Risco / Limitação:** Leitura incorreta das métricas leva a diagnóstico errado (ex.: confundir cache cheio com falta de memória).

## Setas e legenda

- Setas **azuis cheias**: fluxo de instrução/dado (CPU ↔ memória)
- Setas **roxas tracejadas**: fluxo de tradução de endereço (CPU → MMU → tabela)
- Setas **laranjas**: comandos de gerência (kernel atuando sobre páginas)
- Setas **verdes**: chamadas de sistema (processo → kernel)
- Setas **cinzas**: I/O para swap / disco

## Pontos a evidenciar no visual

- Modo **kernel** vs modo **usuário** separados por uma linha horizontal explícita
- A MMU/TLB fica **fisicamente dentro da CPU**, mas é desenhada como bloco próprio porque sua função (tradução + proteção) é o pivô do system design
- As ferramentas de observação devem ter uma faixa lateral apontando para os blocos que elas observam
