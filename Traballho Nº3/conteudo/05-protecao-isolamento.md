# Seção 5 — Proteção e Isolamento

> Artefato visual: **Bloco de Proteção e Isolamento** (artefato obrigatório nº 5)

## Por que proteger memória?

Sem proteção, um processo poderia:

- Ler segredos de outro processo (senhas, chaves criptográficas, dados pessoais)
- Sobrescrever código ou dados de outro processo, corrompendo sua execução
- Modificar estruturas do kernel, ganhando privilégios totais
- Travar o sistema inteiro por engano (bug) ou de propósito (ataque)

A proteção de memória é o que torna possível executar **vários programas, de usuários diferentes, simultaneamente**, sem que um interfira no outro.

## Três pilares da proteção

```text
┌───────────────────────────────────────────────────────────┐
│                                                           │
│   1. ESPAÇOS VIRTUAIS SEPARADOS POR PROCESSO              │
│      → cada processo tem sua tabela de páginas            │
│                                                           │
│   2. PERMISSÕES POR PÁGINA (bits R/W/X/U/S)               │
│      → MMU recusa acesso incompatível                     │
│                                                           │
│   3. MODOS DE EXECUÇÃO (usuário ↔ kernel)                 │
│      → instruções privilegiadas só em modo kernel         │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## Modo usuário vs modo kernel

A CPU opera em dois (ou mais) **níveis de privilégio**, chamados *rings* no x86:

| Modo | Ring | Quem roda aqui | O que pode fazer |
|---|---|---|---|
| **Usuário** | Ring 3 | Processos comuns | Apenas instruções não-privilegiadas; acessa apenas suas próprias páginas |
| **Kernel** | Ring 0 | Kernel, drivers | Tudo: configurar MMU, fazer I/O, alterar tabelas de páginas, executar instruções privilegiadas |

A transição **usuário → kernel** acontece em três situações:

1. **Chamada de sistema** (`syscall` / `int 0x80`) — o processo pede um serviço
2. **Exceção** — page fault, divisão por zero, instrução inválida
3. **Interrupção** — hardware (teclado, timer, disco) sinaliza algo

Em todas, a CPU:

- Salva o estado do processo
- Troca para modo kernel
- Pula para um handler **pré-registrado** pelo kernel (impossível o processo escolher onde "entrar")

Quando o kernel termina, executa `iret`/`sysret` e devolve a CPU ao modo usuário no ponto exato onde o processo parou.

## Papel da MMU na proteção

A MMU não é só "tradutora de endereço" — é **guarda de segurança em hardware**. Para cada acesso, ela verifica os bits da PTE:

| Bit | O que faz |
|---|---|
| **U/S** (User/Supervisor) | Página pertence a userspace ou só ao kernel? Se um processo em modo usuário tentar acessar página com U=0 → fault |
| **R/W** (Read/Write) | Página permite escrita? Tentar escrever em página R=1, W=0 → fault |
| **NX** (No Execute) | Página é executável? Tentar executar instrução em página com NX=1 → fault. Mitigação clássica contra *buffer overflow* clássicos |
| **P** (Present) | Página está mapeada? Acesso em P=0 → page fault (não necessariamente erro, pode ser demand paging) |

Cada uma dessas verificações ocorre em **hardware, em paralelo com a tradução**. Sem custo extra. Se algo falha, a MMU dispara uma exceção e o controle vai para o kernel.

## Como o kernel implementa o isolamento

### Tabela de páginas por processo

```text
Processo A                    Processo B
┌────────────┐                ┌────────────┐
│ vaddr      │                │ vaddr      │
│ 0x400000   │──── PTE_A ──→ frame 0x1A00  │ 0x400000   │──── PTE_B ──→ frame 0x4C00
│            │                │            │
│ stack      │──── PTE_A ──→ frame 0xFF20  │ stack      │──── PTE_B ──→ frame 0x8800
└────────────┘                └────────────┘
```

Cada processo tem sua árvore de tabelas de páginas. O registrador **CR3** (x86) aponta para a raiz da tabela do processo atual. Em cada *context switch*, o kernel troca o CR3 — automaticamente, a MMU passa a usar a tabela do novo processo. **Resultado:** o endereço virtual `0x400000` do processo A aponta para um frame físico diferente do `0x400000` do processo B.

### Bibliotecas compartilhadas

A mesma região física (frame de RAM com `libc.so`) pode ser mapeada nas tabelas de **vários processos**, todos com permissão `r-x`. Isso economiza memória sem quebrar isolamento — ninguém pode escrever ali.

### Copy-on-Write (COW)

Em `fork()`, o filho herda o mesmo espaço do pai. Em vez de duplicar tudo, o kernel:

1. Marca todas as páginas dos dois (pai e filho) como **read-only**
2. Quando um deles tenta escrever → page fault
3. Kernel duplica aquela página específica, deixa cada um com sua cópia, libera escrita

Isolamento é mantido sem o custo de cópia integral.

## Convenção do bloco visual (5 campos)

### Bloco — Proteção de Memória  *(vermelho)*

- **Nome:** Subsistema de Proteção de Memória
- **Função:** Garantir que processos só acessem regiões permitidas, e impedir que userspace alcance recursos privilegiados.
- **Entrada:** Cada acesso a memória da CPU; cada syscall; cada exceção da MMU.
- **Saída:** Acesso permitido (sem ação visível), ou exceção (SIGSEGV / SIGBUS / OOM kill).
- **Risco / Limitação:** Bugs no kernel ou na CPU podem furar o isolamento (ex.: Meltdown, Spectre). Performance: cada syscall custa centenas de ciclos por causa da troca de modo.

## Onde a proteção pode falhar (do ponto de vista do processo)

| Erro do processo | Sinal recebido | Causa raiz |
|---|---|---|
| Escrita em código (`.text`) | SIGSEGV | Bit W=0 |
| Execução de dados | SIGSEGV | Bit NX=1 |
| Acesso a endereço não-mapeado | SIGSEGV | P=0 e endereço fora de qualquer VMA |
| Acesso a região do kernel | SIGSEGV | U=0 e processo em modo usuário |
| Stack overflow | SIGSEGV | Guard page invadida |
| Acesso a memória mapeada de arquivo encurtado | SIGBUS | Offset além do tamanho real do arquivo |

## Pontos a evidenciar no visual

- Bloco grande com a fronteira **vermelha** "usuário ↔ kernel"
- MMU no centro, atuando como **filtro** entre processo e RAM
- Setas de exceção em vermelho, saindo da MMU em direção ao kernel
- Caixas pequenas mostrando os bits da PTE como flags ativáveis
- Diagrama lateral de duas tabelas de páginas (uma para cada processo) apontando para frames físicos
