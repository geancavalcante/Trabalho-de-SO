# Diagramas — System Design da Memória

Os 11 diagramas estão em formato `.drawio` (XML do [draw.io](https://app.diagrams.net)).

## Como abrir

**Opção 1 — Online (mais rápido):**
1. Acesse https://app.diagrams.net
2. **File → Open from → Device** e selecione o `.drawio`
3. Edite, exporte como PNG/PDF/SVG (**File → Export as**)

**Opção 2 — Desktop:**
1. Instale o draw.io desktop: https://github.com/jgraph/drawio-desktop/releases
2. Abra duplo-clicando no arquivo

**Opção 3 — VSCode:**
1. Instale a extensão **Draw.io Integration** (hediet.vscode-drawio)
2. Abra direto no editor

## Lista dos diagramas

| # | Arquivo | Artefato obrigatório (escopo) |
|---|---|---|
| 01 | [01-diagrama-macro.drawio](01-diagrama-macro.drawio) | ✅ Artefato 1 — Diagrama macro |
| 02 | [02-hierarquia-memorias.drawio](02-hierarquia-memorias.drawio) | Seção 2 — Classificação das memórias |
| 03 | [03-fluxo-traducao.drawio](03-fluxo-traducao.drawio) | ✅ Artefato 2 — Fluxo de tradução |
| 04 | [04-mapa-processo.drawio](04-mapa-processo.drawio) | ✅ Artefato 3 — Mapa do processo |
| 05 | [05-protecao-isolamento.drawio](05-protecao-isolamento.drawio) | ✅ Artefato 5 — Proteção e isolamento |
| 06 | [06-tecnicas-gerenciamento.drawio](06-tecnicas-gerenciamento.drawio) | ✅ Artefato 4 — Quadro comparativo |
| 07 | [07-fragmentacao.drawio](07-fragmentacao.drawio) | Seção 7 — Fragmentação |
| 08 | [08-paginacao-visual.drawio](08-paginacao-visual.drawio) | Seção 8 — Paginação e memória virtual |
| 09 | [09-linux-pratica.drawio](09-linux-pratica.drawio) | ✅ Artefato 6 — Linux na prática |
| 10 | [10-observabilidade.drawio](10-observabilidade.drawio) | ✅ Artefato 7 — Observabilidade |
| 11 | [11-conclusao-visual.drawio](11-conclusao-visual.drawio) | ✅ Artefato 9 — Conclusão crítica |

Os artefatos 8 (Glossário) e o texto de apoio estão em formato markdown na pasta [../conteudo/](../conteudo/).

## Padrão visual aplicado (conforme escopo)

| Cor | Uso |
|---|---|
| Azul `#dae8fc / #6c8ebf` | Hardware e CPU |
| Roxo `#e1d5e7 / #9673a6` | MMU, TLB, tradução |
| Verde `#d5e8d4 / #82b366` | Processo, userspace |
| Vermelho `#f8cecc / #b85450` | Proteção, falha, fragmentação |
| Laranja `#ffe6cc / #d79b00` | Kernel e subsistema VM |
| Cinza `#f5f5f5 / #666666` | Secundário, swap, neutros |

## Exportação para entrega

Para gerar a versão final que vai ser entregue ao professor:

1. Abra cada `.drawio` no draw.io
2. **File → Export as → PDF** (ou PNG, conforme a entrega)
3. Marque "Include a copy of my diagram" se quiser preservar a editabilidade
4. Opcional: monte um único PDF final com todos os diagramas em sequência usando ferramentas como `pdfunite` (Linux) ou Adobe Acrobat

## Ajustes recomendados

Os diagramas foram gerados com layout funcional, **não estético**. Antes de exportar, você pode querer:

- Mover blocos para alinhar melhor
- Engrossar bordas de blocos mais importantes
- Adicionar ícones próprios (draw.io tem biblioteca grande)
- Ajustar tipografia (tamanho, fonte)
- Adicionar logo da instituição no canto

Isso é cosmético — o conteúdo técnico e as relações entre blocos já estão completos.
