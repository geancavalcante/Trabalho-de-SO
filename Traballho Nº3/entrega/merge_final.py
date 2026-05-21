"""Merge all PDFs into a single final delivery document."""
from pathlib import Path
from pypdf import PdfWriter

ENTREGA = Path(__file__).parent
DIAGRAMAS = ENTREGA / "diagramas-pdf"
OUTPUT = ENTREGA / "Trabalho-Nº3-System-Design-da-Memoria.pdf"

writer = PdfWriter()

order = [
    (ENTREGA / "capa.pdf", "Capa e Sumário"),
    (DIAGRAMAS / "01-diagrama-macro.pdf", "1. Diagrama Macro"),
    (DIAGRAMAS / "02-hierarquia-memorias.pdf", "2. Hierarquia de Memórias"),
    (DIAGRAMAS / "03-fluxo-traducao.pdf", "3. Fluxo de Tradução"),
    (DIAGRAMAS / "04-mapa-processo.pdf", "4. Mapa do Processo"),
    (DIAGRAMAS / "05-protecao-isolamento.pdf", "5. Proteção e Isolamento"),
    (DIAGRAMAS / "06-tecnicas-gerenciamento.pdf", "6. Técnicas de Gerenciamento"),
    (DIAGRAMAS / "07-fragmentacao.pdf", "7. Fragmentação"),
    (DIAGRAMAS / "08-paginacao-visual.pdf", "8. Paginação Visual"),
    (DIAGRAMAS / "09-linux-pratica.pdf", "9. Linux na Prática"),
    (DIAGRAMAS / "10-observabilidade.pdf", "10. Observabilidade"),
    (DIAGRAMAS / "11-conclusao-visual.pdf", "11. Conclusão Crítica Visual"),
    (ENTREGA / "texto-apoio.pdf", "Texto de Apoio"),
    (ENTREGA / "referencias.pdf", "Referências"),
]

total_pages = 0
for pdf_path, label in order:
    if not pdf_path.exists():
        print(f"AVISO: {pdf_path.name} não existe — pulando")
        continue
    start = len(writer.pages)
    writer.append(str(pdf_path))
    end = len(writer.pages)
    writer.add_outline_item(label, start)
    pages = end - start
    total_pages += pages
    print(f"OK  {pdf_path.name:50s} ({pages} pg) -> {label}")

writer.write(str(OUTPUT))
writer.close()
print(f"\nGerado: {OUTPUT.name}")
print(f"Total: {total_pages} páginas")
print(f"Tamanho: {OUTPUT.stat().st_size / 1024:.1f} KB")
