# Seção 3 — Fluxo de Acesso à Memória

> Artefato visual: **Fluxo de Tradução de Endereço** (artefato obrigatório nº 2)
>
> Pergunta-chave: *O que acontece quando um processo tenta acessar um dado na memória?*

## Premissas técnicas

- Em sistemas com memória virtual, a CPU sempre trabalha com **endereços virtuais**
- A tradução virtual → físico é feita em hardware pela **MMU**, consultando **tabelas de páginas hierárquicas**
- A **TLB** funciona como cache para essa tradução
- Quando a tradução falha (página ausente, permissão inválida), gera-se uma **exceção de page fault** que o kernel trata

## Sequência completa do fluxo

```text
[1] Processo emite endereço virtual (load/store)
       │
       ▼
[2] CPU executa a instrução de acesso
       │
       ▼
[3] MMU consulta a TLB
       │
       ├── TLB HIT  ────────────┐
       │                        │
       └── TLB MISS             │
            │                   │
            ▼                   │
[4] MMU varre as tabelas        │
    de páginas (page walk)      │
            │                   │
            ▼                   │
[5] Entrada encontrada e válida?│
            │                   │
   ┌────────┴────────┐          │
   │ SIM             │ NÃO      │
   │                 │          │
   ▼                 ▼          │
[6] Endereço         [7] PAGE   │
    físico montado       FAULT  │
   (frame + offset)      ↓      │
   │                 [8] Kernel │
   │                     trata  │
   │                     │      │
   │     ┌───────────────┴──┐   │
   │     │  Tipo de falha   │   │
   │     ├──────────────────┤   │
   │     │ minor: alocar    │   │
   │     │ major: swap/disk │   │
   │     │ inválida: SIGSEGV│   │
   │     └────────┬─────────┘   │
   │              │             │
   │              ▼             │
   │     [9] Tabela atualizada, │
   │         TLB invalidada,    │
   │         instrução refeita  │
   │              │             │
   ▼              ▼             ▼
[10] Acesso à memória física (RAM)
       │
       ▼
[11] Dado retornado à CPU
```

## Passos detalhados

### Passo 1 — Endereço virtual emitido

O processo, em modo usuário, executa por exemplo `mov rax, [0x7ffe1234]`. O endereço `0x7ffe1234` é **virtual** — só faz sentido dentro do espaço de endereçamento daquele processo.

### Passo 2 — CPU repassa o acesso à MMU

A MMU fica fisicamente dentro do pacote do processador. Cada acesso a dado ou instrução passa por ela antes de chegar à RAM.

### Passo 3 — Consulta à TLB

A TLB é uma cache associativa pequena (tipicamente 64–2048 entradas) que guarda traduções recentes virtual→físico. Se a entrada estiver presente e válida, o tempo de tradução é praticamente zero (**TLB hit**).

### Passo 4 — Page walk (em caso de TLB miss)

A MMU percorre a tabela de páginas hierárquica em RAM. No x86-64 com paginação de 4 níveis: **PGD → P4D → PUD → PMD → PTE**. Cada nível indexa uma porção dos bits do endereço virtual até chegar na entrada final (PTE), que aponta para o **frame físico**.

### Passo 5 — Validação da entrada

A PTE contém bits importantes:

| Bit | Significado |
|---|---|
| Presente (P) | Página está em RAM? |
| Read/Write (R/W) | Permite escrita? |
| User/Supervisor (U/S) | Acessível em modo usuário? |
| Acessado (A) | Foi acessada recentemente? (usado por algoritmos de substituição) |
| Modificado (D) | Foi escrita? (usado para decidir se precisa salvar em swap) |
| NX | Página não-executável (proteção contra exploits) |

### Passo 6 — Endereço físico montado

Se a entrada é válida e a permissão é compatível com o tipo de acesso, MMU combina o número do frame com o offset interno da página e produz o **endereço físico**. Acesso prossegue normalmente.

### Passo 7 — Page Fault

A MMU gera uma exceção. Os três tipos comuns:

| Tipo | Causa | Quem resolve |
|---|---|---|
| **Minor fault** | Página existe mas ainda não foi mapeada (alocação preguiçosa, *demand paging* de zero-page) | Kernel mapeia em RAM |
| **Major fault** | Página precisa ser trazida de disco (swap-in ou primeira leitura de mmap de arquivo) | Kernel agenda I/O e bloqueia o processo |
| **Inválida** | Acesso fora do espaço permitido, ou permissão violada | Kernel envia `SIGSEGV` — segmentation fault |

### Passo 8 — Kernel trata a falha

O kernel:

1. Identifica qual região do processo gerou o fault (consulta o VMA — *Virtual Memory Area*)
2. Decide a ação: alocar nova página, fazer swap-in, copiar da imagem do arquivo, ou negar
3. Atualiza a tabela de páginas
4. Invalida a entrada antiga na TLB
5. Retoma a instrução que falhou

### Passo 9 — Retomada

A instrução que disparou o fault é re-executada. Desta vez a tradução tem sucesso (a página agora está mapeada).

### Passos 10–11 — Acesso e retorno

Com endereço físico válido, o controlador de memória entrega o dado. A CPU recebe e continua a execução.

## Tempos relativos (escala)

| Situação | Custo aproximado |
|---|---|
| TLB hit | ~1 ciclo |
| TLB miss + page walk | dezenas a centenas de ciclos |
| Minor page fault | ~microssegundos |
| Major page fault (swap-in de SSD) | ~100 μs – 1 ms |
| Major page fault (swap-in de HD) | ~10 ms |

Um único major fault custa o equivalente a executar **milhões de instruções**. Por isso, evitar swap é essencial para desempenho.

## Pontos a evidenciar no visual

- TLB e MMU em **roxo** (camada de tradução)
- Bloco do kernel em **laranja**, com seta entrando pelo lado da MMU (interrupção de page fault)
- Branch do page fault destacado em **vermelho** (caminho de exceção)
- Acesso normal (sem fault) deve ser visualmente o caminho "feliz", em linha contínua e mais espessa
- Setas tracejadas para indicar "instrução refeita após o tratamento"
