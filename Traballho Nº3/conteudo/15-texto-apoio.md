# Texto de Apoio — System Design da Memória

> Parte 2 da entrega — 2 a 4 páginas explicando decisões, conceitos e relação entre visual e teoria.

---

## 1. Introdução e enquadramento do problema

A memória é o recurso que sustenta toda execução em um sistema computacional. Sem ela não há instruções para a CPU buscar, nem espaço para os dados manipulados pelos processos. Apesar dessa centralidade, é também o subsistema mais difícil de raciocinar: opera em escalas que vão de nanossegundos (cache) a milissegundos (swap), serve simultaneamente o hardware, o kernel e o usuário, e exige isolamento absoluto entre processos sem perder eficiência.

Este trabalho responde à pergunta central do enunciado — *"como a memória é usada do início ao fim por hardware, processador, kernel, sistema operacional e processos, garantindo desempenho, isolamento, proteção e continuidade da execução?"* — por meio de um System Design composto por dez seções visuais e três análises críticas. A escolha de tratar memória como um *sistema* (em vez de "RAM") é deliberada: só uma visão integrada deixa claro que cada camada existe para resolver um problema das outras.

## 2. Decisões do grupo

### 2.1 Estrutura em camadas

O diagrama macro segue a cadeia exata pedida no escopo: **Hardware → CPU → MMU/TLB → Kernel → Gerência de Memória do SO → Processos → Ferramentas de Observação**. Decidimos manter essa ordem como esqueleto narrativo do trabalho inteiro, porque ela já reflete o "caminho de um acesso" — entendendo a cadeia, o leitor compreende todas as outras seções.

### 2.2 Convenção de 5 campos por bloco

Cada bloco visual carrega cinco informações: **nome**, **função**, **entrada**, **saída**, **risco/limitação**. Essa convenção, exigida pelo escopo, força a tratar cada componente como uma "caixa preta com interface" — abordagem típica de documentação de arquitetura de sistemas. Em particular, o campo **risco** evita que o trabalho se resuma a descrever o "caminho feliz" e cobra mostrar como cada peça pode falhar.

### 2.3 Paleta de cores semântica

Adotamos as seis cores sugeridas pelo escopo (azul para hardware/CPU, roxo para tradução, verde para userspace, vermelho para proteção/falha, laranja para kernel, cinza para secundário/swap). A paleta funciona como uma **legenda implícita**: ao olhar qualquer diagrama, o leitor identifica imediatamente que tipo de componente é cada bloco, sem precisar ler legenda.

### 2.4 Cada seção é também um insumo do texto

Cada arquivo `.md` da pasta `conteudo/` cumpre duplo papel: alimenta os blocos do design visual e fornece a base teórica resumida no texto de apoio. Esse encadeamento foi escolhido para evitar redundância: a teoria sustenta o visual, e o visual sintetiza a teoria. Para o leitor curioso, há os arquivos detalhados; para o avaliador rápido, há os diagramas.

## 3. Conceitos centrais utilizados

Quatro conceitos atravessam o trabalho inteiro:

**Memória virtual** — o processo nunca toca o endereço físico; cada acesso passa pela MMU. Esse fato isolado libera proteção, sharing e swap, e é a base sobre a qual tudo se monta.

**Paginação** — espaço virtual e físico divididos em blocos de tamanho fixo (4 KiB no Linux x86-64). Resolve fragmentação externa, permite alocação não-contígua, suporta swap por granularidade fina, e torna o COW prático. As Seções 6, 7 e 8 examinam, respectivamente, por que ela venceu a alocação contígua, qual fragmentação ela introduz no lugar da externa, e como funciona em detalhe.

**Proteção por hardware** — a MMU verifica os bits da PTE em cada acesso. Sem essa verificação ser feita em silício, o custo seria proibitivo. A Seção 5 mostra como essa proteção, somada à separação de modos usuário/kernel, é o que torna possível multiusuário moderno.

**Page cache** — RAM ociosa transformada em cache transparente do sistema de arquivos. A Seção 9 mostra que esta é, na prática, a maior consumidora de RAM em um Linux saudável — e que é elástica, cede sob pressão. Ignorar isso leva ao erro clássico do operador ao olhar `free` e achar que o sistema está "sem memória".

## 4. Relação entre visual e teoria

Cada diagrama do design tem um parágrafo correspondente no conteúdo escrito. As correspondências principais:

| Diagrama visual | Conteúdo escrito |
|---|---|
| Diagrama Macro | Seção 1 — define a cadeia e responde "quem faz o quê" |
| Pirâmide da hierarquia | Seção 2 — explica registradores → cache → RAM → disco |
| Fluxo de tradução | Seção 3 — descreve passo a passo o que acontece em um acesso |
| Mapa do processo | Seção 4 — detalha texto, dados, heap, stack, mmap |
| Bloco de proteção | Seção 5 — bits da PTE, modos kernel/usuário, COW |
| Quadro comparativo | Seção 6 — seis técnicas, com vantagens, desvantagens e limitações |
| Quadro de fragmentação | Seção 7 — interna vs externa e mitigações |
| Páginas, quadros, fault | Seção 8 — paginação por demanda, substituição, thrashing |
| Bloco Linux na prática | Seção 9 — zonas, page cache, OOM, syscalls de memória |
| Bloco de observabilidade | Seção 10 — `free`, `top`, `vmstat`, `/proc/<pid>/maps`, `smaps` |

As três análises críticas (trade-offs, erros e riscos, conclusão crítica) não têm diagrama dedicado, mas amarram visualmente os blocos anteriores: o trade-off "contígua vs paginação" referencia os quadros das Seções 6 e 7; "swap excessivo" da seção de riscos cita o diagrama de fluxo da Seção 3.

## 5. Como o Linux comprova na prática

Um dos principais argumentos do trabalho é que **o modelo proposto não é teórico**: ele está implementado, observável e mensurável em qualquer Linux. As correspondências concretas:

- **Tradução de endereço (Seção 3)** — verificável em `perf stat -e dTLB-load-misses` durante a execução de uma aplicação
- **Mapa do processo (Seção 4)** — visível em tempo real em `cat /proc/<pid>/maps` para qualquer PID
- **Bits de permissão (Seção 5)** — refletidos nas colunas `r/w/x/p` do mesmo arquivo
- **Paginação sob demanda (Seção 8)** — comprovável: ao executar um programa grande, `pmap -X <pid>` mostra que `RSS << VIRT` no início, e cresce conforme uso
- **Page cache (Seção 9)** — observável: rodar `cat /grande_arquivo > /dev/null` aumenta `Cached` em `/proc/meminfo`
- **Swap (Seção 9)** — disparável: alocar memória até estourar e ver `vmstat 1` reportar `si`/`so` > 0
- **OOM killer (Seção 9)** — visível em `dmesg` após teste de pressão

Cada conceito do design tem um experimento simples que o demonstra. O trabalho não é uma descrição de "como deveria ser" — é uma descrição de "como é".

## 6. Resposta à pergunta central

A pergunta do escopo é respondida em três níveis:

**No nível mais concreto** (Seção 3): um acesso à memória começa com um endereço virtual emitido pela CPU; passa pela MMU para tradução; consulta a TLB e, se preciso, a tabela de páginas; resulta em endereço físico ou em page fault tratado pelo kernel. Esse ciclo se repete bilhões de vezes por segundo.

**No nível arquitetural** (Seção 1 + Conclusão Crítica): a memória é gerenciada por uma cadeia de camadas com responsabilidades distintas — hardware fornece o substrato, MMU traduz e protege, kernel coordena, processos consomem, ferramentas observam. Cada camada existe porque resolve um problema da anterior.

**No nível operacional** (Seções 9 e 10): no Linux, isso se concretiza em zonas, page cache, swap, VMAs, paginação sob demanda, e em ferramentas que expõem cada métrica relevante ao operador. O sistema é construído para ser *visto* — toda decisão importante é refletida em `/proc` ou em sinais.

## 7. Conclusão

O trabalho mostra que memória, em sistemas modernos, não é "RAM gerenciada" — é um **sistema** com responsabilidades distribuídas entre hardware, kernel, processos e ferramentas. O modelo que melhor representa SOs modernos combina memória virtual, paginação, proteção em hardware, gerenciamento centralizado pelo kernel, page cache elástico e observabilidade rica. Esse modelo venceu porque é o único que entrega simultaneamente isolamento, eficiência, flexibilidade e capacidade de diagnóstico — quatro requisitos inegociáveis em qualquer sistema multiusuário atual.

O design visual deste trabalho não tenta inventar uma representação nova — ele **organiza visualmente o que o Linux já implementa**, conectando teoria, diagrama e ferramenta de modo que cada peça seja localizável tanto em livros de SO quanto em uma sessão de terminal.

---

## Pontos a evidenciar no documento final entregue

- Texto de apoio em formato **artigo curto** (2–4 páginas), com cabeçalho, seções numeradas e tipografia limpa
- Pode ser entregue em PDF separado, ou como segunda parte do mesmo arquivo do design visual
- Em ambos os casos, manter referências cruzadas para as seções do visual ("ver diagrama macro", "ver bloco de proteção")
