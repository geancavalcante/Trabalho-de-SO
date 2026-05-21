# Análise — Trade-offs

> Parte analítica obrigatória (item 10.1 do escopo)

Toda decisão de design de memória resolve um problema **e cria outro**. Esta seção examina as cinco tensões fundamentais do tema.

## 1. Desempenho vs Proteção

| Dimensão | Mais desempenho | Mais proteção |
|---|---|---|
| **Modo de execução** | Tudo em ring 0 (sem troca de contexto) | Usuário/kernel separados, syscall custa centenas de ciclos |
| **Tabelas de página** | Mapeamento direto, sem MMU | Tradução, verificação de bits, TLB miss |
| **Espaços separados** | Um espaço para todos os processos | Um espaço por processo, troca de CR3 em cada context switch |
| **Mitigações de side-channel** (KPTI pós-Meltdown) | Sem isolamento extra | Page tables duplicadas, ~5–30% de overhead em syscalls |

**A escolha do Linux:** sempre fica do lado da proteção. Mesmo overhead alto é aceito porque uma falha de isolamento destrói o modelo de multiusuário. O custo pode ser parcialmente mascarado por TLB, cache, otimizações.

> Não existe sistema operacional moderno de propósito geral que sacrifique proteção por desempenho. Sistemas embarcados muito específicos (microkernels minimalistas) chegam a fazê-lo, mas pagam o preço em segurança.

## 2. Simplicidade vs Flexibilidade

| Estilo | Exemplo |
|---|---|
| **Simples** | Alocação contígua: 1 processo, 1 bloco, 1 par base/limite |
| **Flexível** | Paginação hierárquica + VMAs + page cache + COW + huge pages + NUMA |

O modelo simples é **compreensível, depurável, previsível**. O modelo flexível tem mil cantos onde algo pode dar errado — mas suporta carga de trabalho que o simples nunca suportaria.

**A escolha do Linux:** flexibilidade. O custo é literal milhares de páginas de documentação técnica, mas a alternativa é não rodar workloads reais.

## 3. Memória Contígua vs Paginação

| Aspecto | Contígua | Paginação |
|---|---|---|
| Tradução | Direta | MMU + tabela + TLB |
| Fragmentação externa | **Grave** | Não existe |
| Fragmentação interna | Pequena | Pequena (última página) |
| Alocação de blocos grandes | Difícil sob carga | Trivial |
| Hardware necessário | Mínimo | MMU obrigatória |
| Suporte a memória virtual | Não | Sim |
| Compartilhamento entre processos | Difícil | Mapeamentos compartilhados, naturais |
| Proteção fina | Por região grossa | Por página individual |

**A escolha:** paginação venceu há 40 anos. Casos onde contiguidade ainda importa:

- **DMA legado** (controladores que não suportam scatter-gather): kernel reserva pools contíguos
- **Huge pages** (TLB melhor para grandes regiões): exige blocos físicos contíguos
- **NUMA local** (latência sensível a localidade): kernel tenta alocar perto

## 4. Menos Fragmentação vs Maior Overhead

Esta é a tensão clássica da paginação. Você pode escolher:

| Estratégia | Fragmentação interna | Overhead |
|---|---|---|
| Páginas grandes (1 GiB) | Alta — cada região perde até 1 GB no final | Baixo (poucas entradas TLB cobrem tudo) |
| Páginas médias (2 MiB) | Média | Médio |
| Páginas pequenas (4 KiB — padrão) | Baixa | Alto (TLB ocupa muito, tabelas hierárquicas grandes) |

E há também:

| Otimização | Reduz fragmentação? | Custo |
|---|---|---|
| Compactação periódica | Sim | Pausa o processo / suspensão de I/O |
| Pré-alocação | Sim (sob certas cargas) | Memória parada esperando uso |
| Slab allocator | Sim (objetos do kernel) | Complexidade do alocador |

**A escolha do Linux:** páginas de 4 KiB por padrão, com **Transparent Huge Pages (THP)** automaticamente promovendo regiões grandes para 2 MiB quando vantajoso. Compactação é assíncrona em background (`kcompactd`). Equilíbrio que cobre 95% dos casos.

## 5. Observabilidade Simples vs Detalhada

| Nível | Ferramenta | Conta a história? |
|---|---|---|
| **Resumo** | `free -h` | "Tem RAM sobrando?" — sim ou não |
| **Por processo** | `top`, `htop` | "Quem está usando?" — RES e %MEM |
| **Honesta** | `smaps` + PSS | "Quanto realmente?" — desconta compartilhamento |
| **Detalhada** | `/proc/meminfo`, `/proc/vmstat` | Tudo, mas dezenas de campos exigem leitura cuidadosa |
| **Histórica** | `sar`, Prometheus | "Quando começou a degradar?" |
| **Fina/precisa** | `perf mem`, `bpftrace`, `mem_pressure` | "Por que essa página específica está sendo paginada?" |

**Tensão:** mais detalhe = mais ruído. `meminfo` tem ~50 contadores, e a maioria dos usuários não precisa entender mais do que 5. Mas quando o diagnóstico exige, os detalhes salvam.

**Princípio prático:** comece simples (`free`, `top`). Vá fundo só quando o básico não explicar.

## Síntese — A regra geral

Cada par desses trade-offs ilustra o mesmo padrão:

> **A solução "simples" deixa de funcionar quando o sistema escala. A solução "rica" pode ser simplesmente sobre-engenharia em um problema pequeno. A arte é escolher o nível certo para o problema concreto.**

No caso de sistemas operacionais modernos:

- Paginação ganhou da alocação contígua (escala maior)
- Memória virtual ganhou de memória física pura (proteção)
- Page cache ganhou de I/O direto bruto (desempenho)
- Modo usuário/kernel ganhou de execução flat (segurança)

Em cada caso, o ganho compensa o custo — porque o custo cresce **devagar** (overhead de tradução) enquanto o benefício cresce **rápido** (capacidade de rodar dezenas de processos por segundo).

## Pontos a evidenciar no visual

- 5 caixas em formato de balança/balança visual: à esquerda o que se ganha, à direita o que se perde
- Marcar a escolha do Linux em cada trade-off com um selo / cor distinta
- Conexão final apontando para a Conclusão Crítica: "essas escolhas convergem no modelo paginação + memória virtual + page cache"
