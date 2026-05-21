# Seção 4 — Visão da Memória por Processo

> Artefato visual: **Mapa do Espaço de Memória de um Processo** (artefato obrigatório nº 3)

## Ideia central

- O processo **enxerga memória de forma lógica/virtual** — para ele, parece ter um endereço contínuo do começo ao fim
- O hardware trabalha com **memória física** (frames de RAM, em locais arbitrários)
- A MMU faz a ponte: páginas virtuais → frames físicos, conforme as tabelas de páginas
- Cada processo tem seu **próprio** espaço virtual: dois processos podem ter o mesmo endereço virtual apontando para frames físicos diferentes (ou, em alguns casos, o mesmo — *shared mapping*)
- O kernel controla todos os mapeamentos e permissões

## Layout típico de um processo em Linux x86-64

```text
0xFFFFFFFFFFFFFFFF  ┌──────────────────────────────┐
                    │      ESPAÇO DO KERNEL        │  Acessível só em modo
                    │   (compartilhado por todos   │  privilegiado. Mapeado
                    │    os processos, protegido)  │  em todos os processos
                    ├══════════════════════════════┤  ← fronteira user/kernel
0x00007FFFFFFFFFFF  │                              │
                    │           STACK              │  Cresce ↓ (alto → baixo)
                    │      (uma por thread)        │  Locais, frames, retorno
                    │            ↓ ↓               │
                    ├──────────────────────────────┤
                    │                              │
                    │   REGIÕES MAPEADAS (mmap)    │  Bibliotecas .so, arquivos
                    │   ┌──────────────────────┐   │  mapeados com mmap(),
                    │   │  libc.so             │   │  buffers grandes
                    │   │  libpthread.so       │   │
                    │   │  mmap(arquivo, ...)  │   │
                    │   └──────────────────────┘   │
                    │                              │
                    ├──────────────────────────────┤
                    │            ↑ ↑               │
                    │           HEAP               │  Cresce ↑ (baixo → alto)
                    │  (malloc, new, brk/sbrk)     │  Dados dinâmicos
                    ├──────────────────────────────┤
                    │     BSS (não inicializados)  │  Variáveis globais = 0
                    ├──────────────────────────────┤
                    │     DADOS (inicializados)    │  Globais com valor inicial
                    ├──────────────────────────────┤
                    │   TEXTO / CÓDIGO (.text)     │  Instruções do programa
                    │   read-only, executável      │
0x0000000000400000  └──────────────────────────────┘
                    │   (página zero — inacessível) │  Acesso aqui = SIGSEGV
0x0000000000000000  └──────────────────────────────┘
```

## Regiões (convenção 5 campos)

### Texto / Código  *(verde — espaço do usuário)*

- **Nome:** Segmento de texto (`.text`)
- **Função:** Conter as instruções de máquina do programa.
- **Entrada:** Carregado pelo loader a partir do ELF executável durante `exec()`.
- **Saída:** Instruções lidas pela CPU; geralmente mapeado como arquivo (page cache compartilhado entre processos que rodam o mesmo binário).
- **Risco / Limitação:** **Read-only e executável**. Tentativa de escrita gera segfault. Exploits clássicos tentam burlar essa proteção.

### Dados inicializados  *(verde)*

- **Nome:** Segmento de dados (`.data`)
- **Função:** Conter variáveis globais e estáticas **com valor inicial** (ex.: `int contador = 10`).
- **Entrada:** Valores vindos do ELF executável.
- **Saída:** Leituras e escritas do programa.
- **Risco / Limitação:** Tamanho fixo definido em tempo de compilação.

### BSS  *(verde)*

- **Nome:** Segmento BSS (Block Started by Symbol)
- **Função:** Variáveis globais e estáticas **não inicializadas** (zeradas pelo kernel).
- **Entrada:** Apenas o tamanho — não há dados no executável (economia de espaço em disco).
- **Saída:** Páginas zeradas sob demanda no primeiro acesso (zero-page mapping, depois COW).
- **Risco / Limitação:** Tamanho cresce o executável apenas como número, mas em RAM gasta espaço quando acessado.

### Heap  *(verde)*

- **Nome:** Heap
- **Função:** Alocação dinâmica em tempo de execução (`malloc`, `new`, `brk`/`sbrk`).
- **Entrada:** Requisições de alocação do programa.
- **Saída:** Ponteiros para regiões alocadas; libera com `free`.
- **Risco / Limitação:** **Cresce ↑**. Vazamentos de memória (leak) inflam o heap; alocações intermediárias podem causar fragmentação interna no alocador.

### Mmap / Bibliotecas compartilhadas  *(verde, com elementos cinzas se for arquivo mapeado)*

- **Nome:** Região de mapeamentos (`mmap`)
- **Função:** Carregar bibliotecas dinâmicas (`.so`/`.dll`), arquivos mapeados em memória, e grandes blocos anônimos (alocadores modernos preferem mmap a brk para blocos grandes).
- **Entrada:** Chamadas `mmap()`, ou carga automática pelo loader dinâmico.
- **Saída:** Regiões mapeadas com permissões específicas; compartilhadas entre processos quando `MAP_SHARED`.
- **Risco / Limitação:** Mapeamentos errados (permissões ou flags) viram falhas. Bibliotecas compartilhadas precisam de relocação (ASLR ajuda contra exploits).

### Stack  *(verde)*

- **Nome:** Pilha (stack) — uma por thread
- **Função:** Quadros de chamada de função: parâmetros, variáveis locais, endereço de retorno.
- **Entrada:** Crescimento via `push`, `call`, alocações locais.
- **Saída:** Decrementa em `ret`, `pop`, retorno de função.
- **Risco / Limitação:** **Cresce ↓**. Tem limite (`ulimit -s`, padrão 8 MB no Linux). Recursão infinita ou alocação local enorme causa **stack overflow** (segfault). Exploits clássicos: *buffer overflow* na stack.

### Página zero / não-mapeada  *(vermelho — proteção)*

- **Nome:** Página NULL (endereço 0)
- **Função:** Capturar dereferências de ponteiros nulos como erro.
- **Entrada:** Acesso programático a endereço próximo de 0.
- **Saída:** **SIGSEGV** sempre — não há mapeamento válido.
- **Risco / Limitação:** É *intencional*. Sem essa proteção, `*ptr = x` com `ptr == NULL` corromperia memória silenciosamente.

### Espaço do kernel  *(laranja)*

- **Nome:** Área do kernel (acima da fronteira)
- **Função:** Conter o kernel, drivers, estruturas internas — mapeado em todos os processos para evitar troca de tabela de páginas em cada syscall.
- **Entrada:** Mapeado pelo kernel na criação do processo.
- **Saída:** Apenas o kernel acessa (modo privilegiado).
- **Risco / Limitação:** Processo em modo usuário tentando acessar essa região → SIGSEGV imediato. Vulnerabilidades como Meltdown atacaram justamente essa fronteira.

## Como observar isso no Linux

```bash
cat /proc/<pid>/maps      # regiões mapeadas e permissões
cat /proc/<pid>/smaps     # idem, com tamanho, RSS, PSS, swap por mapeamento
pmap <pid>                # versão amigável do maps
```

Exemplo de linha em `/proc/<pid>/maps`:

```
00400000-00452000 r-xp 00000000 fd:00 12345  /usr/bin/cat
```

- `00400000-00452000`: faixa virtual
- `r-xp`: read, execute, **p**rivate
- `00000000`: offset no arquivo
- `fd:00`: dispositivo (disk:partição)
- `12345`: inode
- `/usr/bin/cat`: arquivo mapeado

## Pontos a evidenciar no visual

- Setas indicando direção de crescimento da **stack** (para baixo) e do **heap** (para cima)
- Fronteira user/kernel em **vermelho** com legenda "modo usuário ↔ modo kernel"
- Cores diferentes para regiões com permissão diferente (texto = r-x; dados = rw-; stack = rw-)
- Inserir mini-print de uma saída real de `/proc/<pid>/maps` ao lado do desenho do espaço
