# Entrega Final — System Design da Memória

## 🎯 Arquivo de entrega

**[Trabalho-Nº3-System-Design-da-Memoria.pdf](Trabalho-Nº3-System-Design-da-Memoria.pdf)** — 21 páginas, ~1.5 MB

Este é o arquivo único pronto para entregar ao professor. Contém:

- Capa com identificação do autor e da disciplina
- Sumário navegável (bookmarks no PDF)
- 11 diagramas visuais
- Texto de apoio explicativo (5 páginas)
- Referências em formato acadêmico

## 📂 Conteúdo da pasta

### Documento consolidado (entrega principal)

| Arquivo | Descrição |
|---------|-----------|
| `Trabalho-Nº3-System-Design-da-Memoria.pdf` | **PDF final unificado pronto para entrega** |

### Componentes individuais

| Arquivo | Descrição |
|---------|-----------|
| `capa.pdf` | Capa + sumário do trabalho |
| `texto-apoio.pdf` | Texto de apoio em 5 páginas |
| `referencias.pdf` | Lista de referências em formato acadêmico |
| `diagramas-pdf/` | 11 diagramas em PDF (um por arquivo, alta qualidade) |
| `diagramas-png/` | 11 diagramas em PNG (alta resolução, 2× scale) |

### Fontes editáveis

| Arquivo | Descrição |
|---------|-----------|
| `capa.md` | Fonte markdown da capa |
| `texto-apoio.md` | Fonte markdown do texto de apoio |
| `referencias.md` | Fonte markdown das referências |
| `merge_final.py` | Script Python que monta o PDF unificado |

## 🔧 Como regenerar a entrega

Caso queira ajustar qualquer parte e regenerar o PDF final:

```powershell
# 1. Reexportar diagramas (se algum .drawio foi editado)
$drawio = "C:\Program Files\draw.io\draw.io.exe"
Get-ChildItem ../diagramas/*.drawio | ForEach-Object {
    & $drawio --export --format pdf --output "diagramas-pdf/$($_.BaseName).pdf" $_.FullName
}

# 2. Reconverter markdowns alterados
pandoc capa.md -o capa.pdf --pdf-engine=pdflatex
pandoc texto-apoio.md -o texto-apoio.pdf --pdf-engine=pdflatex
pandoc referencias.md -o referencias.pdf --pdf-engine=pdflatex

# 3. Mesclar tudo
python merge_final.py
```

## 🛠️ Ferramentas usadas

- **draw.io desktop** — exportação dos diagramas
- **pandoc 3.9** + **MiKTeX** — conversão markdown → PDF
- **pypdf** — merge dos PDFs em arquivo único com bookmarks

## ✅ Cobertura do checklist do escopo

| Requisito | Onde está |
|-----------|-----------|
| Diagrama macro da arquitetura | Diagrama 1 |
| Fluxo de tradução de endereço | Diagrama 3 |
| Mapa do espaço de memória do processo | Diagrama 4 |
| Quadro comparativo das técnicas | Diagrama 6 |
| Bloco de proteção e isolamento | Diagrama 5 |
| Bloco "Linux na prática" | Diagrama 9 |
| Bloco de observabilidade | Diagrama 10 |
| Glossário técnico | `../conteudo/14-glossario.md` |
| Conclusão crítica | Diagrama 11 + Texto de apoio §8 |
| Texto de apoio (2–4 páginas) | `texto-apoio.pdf` (5 pgs) |
| Trade-offs, erros, riscos | `../conteudo/11-13-*.md` |
| Referências | `referencias.pdf` |
| Padrão visual (6 cores) | Aplicado em todos os diagramas |
| Convenção 5 campos | Aplicada em todos os blocos |
