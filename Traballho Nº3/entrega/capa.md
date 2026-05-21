---
documentclass: article
geometry: margin=2.5cm
fontsize: 12pt
header-includes:
  - \pagenumbering{gobble}
---

\vspace*{2cm}

\begin{center}

\Large
\textbf{Disciplina de Sistemas Operacionais}

\vspace{0.5cm}

\large
\textbf{Trabalho Nº 3}

\vspace{6cm}

\Huge
\textbf{System Design da Memória}

\vspace{0.5cm}

\Large
\textit{em Sistemas Operacionais}

\vspace{1.5cm}

\large
Relação entre hardware, processador, MMU,\\
kernel, sistema operacional e processos

\vfill

\large
\textbf{Gean Feitosa Cavalcante}

\vspace{0.5cm}

\normalsize
2026

\end{center}

\newpage

\tableofcontents

\newpage

# Sumário do trabalho

Este trabalho apresenta um **System Design da Memória em Sistemas Operacionais**, organizando visual e tecnicamente como a memória é utilizada por hardware, CPU, MMU, kernel, sistema operacional e processos — com foco prático no Linux moderno.

A entrega é composta por:

- **11 diagramas visuais**, seguindo paleta de cores e convenções definidas no escopo, cobrindo todos os artefatos obrigatórios e seções de conteúdo.
- **Texto de apoio**, explicando decisões do projeto, conceitos, relação entre visual e teoria, e resposta à pergunta central.
- **Referências**, com fontes oficiais (kernel.org, man7) e artigos acadêmicos.

## Estrutura dos diagramas

| # | Diagrama | Artefato obrigatório |
|---|----------|----------------------|
| 1 | Diagrama Macro da Arquitetura | Artefato 1 |
| 2 | Hierarquia de Memórias | Seção 2 |
| 3 | Fluxo de Tradução de Endereço | Artefato 2 |
| 4 | Mapa do Espaço de Memória do Processo | Artefato 3 |
| 5 | Proteção e Isolamento | Artefato 5 |
| 6 | Técnicas de Gerenciamento (Comparativo) | Artefato 4 |
| 7 | Fragmentação Interna vs Externa | Seção 7 |
| 8 | Paginação e Memória Virtual | Seção 8 |
| 9 | Linux na Prática | Artefato 6 |
| 10 | Observabilidade e Monitoramento | Artefato 7 |
| 11 | Conclusão Crítica Visual | Artefato 9 |

## Padrão visual

| Cor | Aplicação |
|-----|-----------|
| Azul | Hardware e CPU |
| Roxo | MMU, TLB e tradução |
| Verde | Processo, aplicação e espaço do usuário |
| Vermelho | Proteção, falha, violação e fragmentação |
| Laranja | Kernel e subsistema de memória |
| Cinza | Armazenamento secundário e swap |

\newpage
