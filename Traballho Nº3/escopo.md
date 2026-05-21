# Escopo do Projeto: System Design da Memoria

Este documento e o briefing principal para orientar a Claude Code na criacao de um trabalho sobre **System Design da Memoria em Sistemas Operacionais**.

O objetivo e transformar a atividade em um material tecnico, visual, bem organizado e coerente, mostrando como a memoria e usada por hardware, CPU, MMU, kernel, sistema operacional e processos.

---

## 1. Contexto Academico

### 1.1 Disciplina

Sistemas Operacionais.

### 1.2 Tema

System Design da Memoria: relacao entre hardware, processador, MMU, kernel, sistema operacional e processos.

### 1.3 Modalidade

Atividade de pesquisa, analise tecnica e modelagem visual.

---

## 2. Missao da Claude Code

A Claude Code deve produzir ou auxiliar na producao de um **documento tecnico visual** que explique o funcionamento da memoria como um sistema completo.

O trabalho nao deve tratar memoria apenas como RAM. Ele deve explicar a memoria de ponta a ponta:

1. como o hardware enxerga a memoria;
2. como a CPU acessa dados e instrucoes;
3. como a MMU traduz enderecos virtuais em enderecos fisicos;
4. como o kernel organiza, protege e aloca memoria;
5. como processos enxergam seu proprio espaco de enderecamento;
6. como paginacao, segmentacao, fragmentacao e swap se relacionam;
7. como o uso de memoria pode ser observado no Linux.

---

## 3. Pergunta Central

O trabalho deve responder claramente:

> Como a memoria e usada do inicio ao fim por hardware, processador, kernel, sistema operacional e processos, garantindo desempenho, isolamento, protecao e continuidade da execucao?

---

## 4. Produto Final Esperado

O grupo deve entregar um **System Design completo da memoria**, composto por:

1. documento visual principal;
2. texto explicativo de apoio;
3. referencias utilizadas.

O material final deve parecer um documento produzido por uma equipe de arquitetura de sistemas: tecnico, visual, organizado, consistente e facil de consultar.

### 4.1 Ferramentas visuais permitidas

Pode ser usado qualquer editor visual equivalente, por exemplo:

- draw.io;
- Figma;
- Miro;
- Lucidchart;
- Canva;
- PowerPoint.

---

## 5. Objetivo Geral

Construir um system design visual e tecnico que explique o funcionamento da memoria em um sistema operacional moderno, considerando sua relacao com:

- hardware;
- CPU;
- MMU;
- kernel;
- processos;
- memoria virtual;
- paginacao;
- protecao;
- swap;
- ferramentas de observacao no Linux.

---

## 6. Objetivos Especificos

Ao final, o trabalho deve mostrar:

1. quais sao os tipos de memoria e armazenamento envolvidos no sistema;
2. como ocorre a separacao entre enderecos logicos ou virtuais e enderecos fisicos;
3. como a MMU e as tabelas de paginas participam da traducao de enderecos;
4. como o kernel protege e organiza a memoria;
5. como um processo enxerga sua memoria;
6. como funcionam alocacao, fragmentacao, paginacao, segmentacao e swap;
7. como observar tudo isso no Linux com ferramentas e arquivos do sistema.

---

## 7. Artefatos Obrigatorios

O trabalho deve conter obrigatoriamente:

1. diagrama macro da arquitetura;
2. fluxo de traducao de endereco;
3. mapa do espaco de memoria de um processo;
4. quadro comparativo das tecnicas de gerenciamento;
5. bloco de protecao e isolamento;
6. bloco "Linux na pratica";
7. bloco de observabilidade;
8. glossario tecnico;
9. conclusao critica.

---

## 8. Estrutura Obrigatoria do Documento Visual

### 8.1 Visao Macro da Arquitetura da Memoria

Criar um diagrama principal com a seguinte cadeia minima:

```text
Hardware -> CPU -> MMU/TLB -> Kernel -> Gerencia de Memoria do SO -> Processos/Aplicacoes -> Ferramentas de Observacao
```

Esse diagrama deve deixar claro:

- quem acessa memoria;
- quem traduz endereco;
- quem protege;
- quem aloca;
- quem monitora.

Cada bloco do diagrama deve conter:

- nome do componente;
- funcao;
- entrada;
- saida;
- risco ou limitacao.

### 8.2 Classificacao das Memorias

Criar uma secao visual mostrando:

- armazenamento interno;
- memoria principal;
- armazenamento secundario.

Explicar o papel de:

- registradores;
- cache;
- RAM;
- disco;
- swap.

### 8.3 Fluxo de Acesso a Memoria

Criar um fluxo visual respondendo:

> O que acontece quando um processo tenta acessar um dado na memoria?

O fluxo deve mostrar, em sequencia:

1. o processo gera um endereco virtual;
2. a CPU executa a instrucao;
3. a MMU tenta traduzir o endereco;
4. a TLB pode acelerar a traducao;
5. as tabelas de paginas sao consultadas quando necessario;
6. o acesso chega ao quadro fisico quando a traducao e valida;
7. ocorre uma falha ou evento de tratamento quando a pagina nao esta disponivel ou a permissao e invalida;
8. o kernel toma a decisao necessaria, como carregar pagina, negar acesso ou finalizar processo.

A base tecnica dessa parte e:

- a CPU trabalha com enderecos virtuais em sistemas com memoria virtual;
- a traducao para endereco fisico e feita por paginas;
- as tabelas de paginas sao organizadas hierarquicamente;
- falhas de pagina exigem intervencao do kernel.

### 8.4 Visao da Memoria por Processo

Criar um desenho do espaco de enderecamento de um processo contendo:

- codigo ou texto;
- dados;
- heap;
- stack;
- regioes mapeadas;
- bibliotecas;
- area do kernel separada da area de usuario.

Explicar que:

- o processo enxerga memoria de forma logica ou virtual;
- o hardware trabalha com memoria fisica;
- cada processo deve parecer isolado dos demais;
- o kernel controla os mapeamentos e permissoes.

No Linux, mostrar que os mapeamentos reais podem ser observados em:

```text
/proc/<pid>/maps
/proc/<pid>/smaps
```

### 8.5 Protecao e Isolamento

Criar um bloco especifico mostrando:

- por que um processo nao deve acessar a memoria de outro;
- como a protecao ocorre;
- qual e o papel da MMU;
- qual e o papel do modo kernel;
- qual e o papel do modo usuario;
- onde ocorre o isolamento de permissoes.

O bloco deve relacionar:

- bits de permissao;
- paginas validas e invalidas;
- acessos de leitura, escrita e execucao;
- violacoes de memoria;
- separacao entre espaco de usuario e espaco de kernel.

### 8.6 Tecnicas de Gerenciamento de Memoria

Criar um quadro comparativo visual e conceitual com as seguintes tecnicas:

- alocacao contigua;
- particoes fixas;
- particoes variaveis;
- swapping;
- paginacao;
- segmentacao.

Para cada tecnica, incluir:

- definicao;
- vantagem;
- desvantagem;
- problema que tenta resolver;
- limitacao pratica.

### 8.7 Fragmentacao

Criar um quadro explicando:

- fragmentacao interna;
- fragmentacao externa;
- causa;
- impacto;
- formas de mitigacao.

O quadro deve deixar clara a diferenca:

- fragmentacao interna: desperdicio dentro de blocos ou paginas ja alocados;
- fragmentacao externa: espacos livres separados que dificultam alocacao contigua.

### 8.8 Paginacao e Memoria Virtual

Criar uma secao propria para explicar:

- paginas;
- quadros;
- tabela de paginas;
- bit de permissao;
- bit valido/invalido;
- paginacao sob demanda;
- substituicao de paginas;
- falha de pagina.

Incluir uma representacao visual simples de:

- pagina virtual;
- quadro fisico;
- tabela de paginas;
- falha de pagina;
- substituicao de pagina.

### 8.9 Linux e Gerenciamento Real de Memoria

Criar uma secao chamada:

```text
Como o Linux gerencia memoria na pratica
```

Essa secao deve mostrar:

- alocacao e liberacao de memoria fisica;
- manipulacao de memoria virtual;
- zonas de memoria;
- page cache;
- parametros do subsistema VM;
- criacao de novo espaco virtual em `fork()`;
- substituicao do espaco virtual em `exec()`.

Tambem deve explicar que:

- a memoria fisica e organizada em zonas de uso;
- a memoria virtual mantem o espaco de enderecamento dos processos;
- o page cache e o caminho principal entre kernel, usuario e sistemas de arquivos;
- `/proc/sys/vm` reune parametros de controle do subsistema de memoria virtual.

### 8.10 Observabilidade e Monitoramento

Criar uma area pratica mostrando como validar o uso da memoria no Linux.

Incluir as seguintes ferramentas e arquivos:

- `free`;
- `top`;
- `htop`;
- `vmstat`;
- `/proc/<pid>/maps`;
- `/proc/<pid>/smaps`.

Para cada item, explicar:

- o que mostra;
- quando usar;
- que tipo de diagnostico permite.

Resumo minimo esperado:

| Ferramenta ou arquivo | O que deve explicar |
|---|---|
| `free` | Uso de RAM, memoria disponivel, buffers, cache e swap. |
| `top` | Processos ativos e consumo de CPU/memoria em tempo real. |
| `htop` | Visualizacao interativa de processos e uso de memoria. |
| `vmstat` | Processos, memoria, paginacao, block I/O, traps, discos e CPU. |
| `/proc/<pid>/maps` | Regioes mapeadas e permissoes de um processo. |
| `/proc/<pid>/smaps` | Tamanho, RSS, PSS e swap por mapeamento. |

---

## 9. Padrao Visual Obrigatorio

### 9.1 Cores Sugeridas

| Cor | Uso |
|---|---|
| Azul | Hardware e CPU. |
| Roxo | MMU, TLB e traducao. |
| Verde | Processo, aplicacao e espaco do usuario. |
| Vermelho | Protecao, falha, violacao e fragmentacao. |
| Laranja | Kernel e subsistema de memoria. |
| Cinza | Armazenamento secundario e swap. |

### 9.2 Convencoes Visuais

Usar:

- setas para fluxo;
- blocos para camadas;
- legenda obrigatoria;
- icones ou simbolos consistentes;
- diferenciacao clara entre memoria virtual e memoria fisica;
- diferenciacao clara entre espaco do usuario e espaco do kernel.

### 9.3 Convencoes Textuais dos Blocos

Cada bloco visual deve conter:

- nome do componente;
- funcao;
- entrada;
- saida;
- risco ou limitacao.

---

## 10. Parte Analitica Obrigatoria

Além do design visual, escrever uma analise com os topicos abaixo.

### 10.1 Trade-offs

Explicar:

- desempenho vs protecao;
- simplicidade vs flexibilidade;
- memoria contigua vs paginacao;
- menos fragmentacao vs maior overhead;
- observabilidade simples vs observabilidade detalhada.

### 10.2 Erros e Riscos

Apontar problemas como:

- fragmentacao;
- swap excessivo;
- overhead de paginacao;
- mau uso de cache;
- falhas de protecao;
- crescimento descontrolado de heap ou stack;
- leitura incorreta de metricas.

### 10.3 Conclusao Critica

Responder:

> Qual modelo de gerenciamento de memoria melhor representa os sistemas operacionais modernos e por que?

A resposta deve justificar tecnicamente por que sistemas modernos tendem a combinar:

- memoria virtual;
- paginacao;
- protecao por hardware;
- gerenciamento pelo kernel;
- uso de page cache;
- observabilidade por ferramentas do sistema.

---

## 11. Texto de Apoio

Criar um texto de apoio entre **2 e 4 paginas** explicando:

- decisoes do grupo;
- justificativas;
- conceitos utilizados;
- relacao entre o visual e a teoria;
- como os diagramas se conectam entre si;
- como Linux comprova na pratica os conceitos apresentados.

---

## 12. Perguntas Norteadoras

O trabalho deve responder de forma clara:

1. O que e memoria do ponto de vista do hardware?
2. O que muda quando um processo enxerga memoria logicamente?
3. Qual a diferenca entre endereco virtual e endereco fisico?
4. Qual e a funcao da MMU?
5. Como a tabela de paginas entra nesse processo?
6. Por que a protecao de memoria e essencial?
7. O que o kernel gerencia diretamente?
8. Quando a paginacao ajuda e quando custa desempenho?
9. Por que o swap existe?
10. Como o Linux mostra os mapeamentos reais de um processo?
11. Como distinguir uso de RAM, cache e swap em ferramentas do sistema?
12. Como o desenho da memoria influencia desempenho, seguranca e estabilidade?

---

## 13. Referencias Recomendadas

As referencias detalhadas estao no arquivo:

```text
referências.json
```

Priorizar especialmente:

- documentacao oficial do Linux Kernel sobre page tables;
- man pages de `/proc/<pid>/maps`;
- man pages de `/proc/<pid>/smaps`;
- man pages de `proc`;
- man pages de `vmstat`;
- man pages de `free`;
- man pages de `top`.

Usar artigos academicos apenas para fortalecer a analise critica, trade-offs e tendencias modernas.

---

## 14. Checklist de Aceitacao

Antes de considerar o trabalho concluido, verificar se ele:

- [ ] mostra a relacao entre hardware, kernel, SO e processo;
- [ ] diferencia memoria fisica e memoria virtual;
- [ ] explica a MMU;
- [ ] inclui TLB e tabelas de paginas;
- [ ] mostra protecao de memoria;
- [ ] compara tecnicas de gerenciamento;
- [ ] apresenta fragmentacao interna e externa;
- [ ] mostra paginacao e segmentacao;
- [ ] explica swap;
- [ ] traz Linux na pratica;
- [ ] usa ferramentas de observacao;
- [ ] possui legenda visual;
- [ ] possui glossario tecnico;
- [ ] possui conclusao critica;
- [ ] inclui referencias.

---

## 15. Ordem Recomendada de Execucao para a Claude Code

1. Ler este escopo completo.
2. Consultar `referências.json` para identificar as fontes principais.
3. Montar a estrutura do documento visual.
4. Criar o diagrama macro.
5. Criar o fluxo de traducao de endereco.
6. Criar o mapa de memoria de processo.
7. Criar os blocos de protecao, paginacao, fragmentacao e tecnicas de gerenciamento.
8. Criar a secao "Linux na pratica".
9. Criar a secao de observabilidade.
10. Escrever o texto de apoio de 2 a 4 paginas.
11. Criar glossario tecnico.
12. Criar conclusao critica.
13. Revisar se todos os itens do checklist foram atendidos.

---

## 16. Resultado Esperado em Uma Frase

O resultado final deve ser um System Design da Memoria que explique, com diagramas e texto tecnico, como um sistema operacional moderno organiza, traduz, protege, aloca, monitora e otimiza o uso da memoria entre hardware, CPU, MMU, kernel, processos e Linux.
