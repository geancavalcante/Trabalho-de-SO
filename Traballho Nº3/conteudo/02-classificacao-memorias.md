# Seção 2 — Classificação das Memórias

> Artefato visual: **Pirâmide de Hierarquia da Memória**

## Os três níveis de armazenamento

O sistema enxerga memória como uma **hierarquia**: quanto mais próxima do processador, mais rápida, mais cara e menor; quanto mais distante, mais lenta, mais barata e maior.

```text
        ↑ Velocidade        Registradores  (ns)        Tamanho ↓
        |                   Cache L1/L2/L3 (ns–dezenas de ns)
        |                   RAM            (dezenas–centenas de ns)
        |                   Disco / SSD    (μs–ms)
        ↓ Custo por byte    Swap em disco  (ms)        Capacidade ↑
```

## Componentes (convenção 5 campos)

### Registradores  *(armazenamento interno — cor: azul)*

- **Nome:** Registradores da CPU
- **Função:** Armazenar dados e endereços que a unidade de execução acessa **no mesmo ciclo de clock**.
- **Entrada:** Valores carregados de cache/memória; resultados de operações da ULA.
- **Saída:** Operandos para a próxima instrução; valor escrito de volta na hierarquia.
- **Risco / Limitação:** Número fixo e muito pequeno (dezenas em arquiteturas modernas); gerenciados pelo compilador via *register allocation*.

### Cache  *(armazenamento interno — cor: azul)*

- **Nome:** Cache de CPU (L1, L2, L3)
- **Função:** Manter cópias próximas das linhas de memória mais usadas, explorando localidade temporal e espacial.
- **Entrada:** Linhas trazidas da RAM em resposta a *miss* da cache; escritas (write-through ou write-back).
- **Saída:** Dados entregues à CPU em poucos ciclos; linhas escritas de volta na RAM quando substituídas.
- **Risco / Limitação:** Tamanho limitado; *cache miss* custa centenas de ciclos. Pode haver invalidação por DMA ou por escrita em outro núcleo (coerência de cache).

### RAM (memória principal)  *(memória principal — cor: azul)*

- **Nome:** Memória RAM (DRAM)
- **Função:** Conter o conjunto de trabalho dos processos, o código e os dados que estão "vivos" no sistema.
- **Entrada:** Páginas trazidas do disco; resultados escritos pela CPU.
- **Saída:** Linhas lidas para a cache; páginas eventualmente enviadas a swap.
- **Risco / Limitação:** Volátil (perde conteúdo ao desligar); finita; sob pressão, kernel é forçado a paginar ou matar processos.

### Disco / SSD  *(armazenamento secundário — cor: cinza)*

- **Nome:** Armazenamento secundário (HD, SSD, NVMe)
- **Função:** Persistir o sistema de arquivos, executáveis, bibliotecas, dados de usuário, *e* a área de swap.
- **Entrada:** Páginas marcadas para swap-out; gravações de arquivos vindas do page cache.
- **Saída:** Páginas carregadas via *demand paging*; arquivos lidos para o page cache.
- **Risco / Limitação:** Latência ordens de magnitude maior que RAM; sob swap intenso, sistema fica praticamente inutilizável (*thrashing*).

### Swap  *(armazenamento secundário — cor: cinza)*

- **Nome:** Área de swap (partição ou arquivo)
- **Função:** Estender a memória virtual além do tamanho físico da RAM, guardando páginas que estavam em RAM mas foram escolhidas para sair.
- **Entrada:** Páginas anônimas (heap, stack) selecionadas pelo algoritmo de substituição do kernel.
- **Saída:** As mesmas páginas, trazidas de volta à RAM em um *page fault* (swap-in).
- **Risco / Limitação:** Swap em excesso destrói o desempenho. Páginas mapeadas de arquivos não vão para swap — são descartadas e relidas do arquivo.

## Resumo comparativo

| Nível | Velocidade típica | Volátil? | Gerenciado por | Tamanho típico |
|---|---|---|---|---|
| Registradores | ~1 ciclo | Sim | Compilador | Dezenas de palavras |
| Cache L1 | 1–4 ciclos | Sim | Hardware | dezenas de KB |
| Cache L2 | 10–20 ciclos | Sim | Hardware | centenas de KB |
| Cache L3 | 30–60 ciclos | Sim | Hardware | dezenas de MB |
| RAM | 100–300 ciclos | Sim | Kernel | GB |
| SSD | 10⁵ ciclos (~μs) | Não | Kernel + FS | centenas de GB |
| HD | 10⁷ ciclos (~ms) | Não | Kernel + FS | TB |

## Como representar no diagrama

- Pirâmide invertida (registradores no topo, disco/swap na base)
- Eixos laterais: à esquerda **velocidade ↑**; à direita **capacidade ↑** (em sentidos opostos)
- Linhas pontilhadas separando os 3 grupos: armazenamento interno (registradores, cache) — memória principal (RAM) — armazenamento secundário (disco, swap)
- Cor por bloco seguindo a convenção (azul para HW próximo à CPU; cinza para secundário)
