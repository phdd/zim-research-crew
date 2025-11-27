#!.venv/bin/python
import sys
import asyncio
import requests
import shutil

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import logging
import click

from crewai import LLM
from crewai.rag.config.utils import get_rag_client
from crewai.utilities.constants import KNOWLEDGE_DIRECTORY
from crew.crew import ProjectResearchCrew
from crew.utils.chunker import create_chunker, ChunkingConfig

from docling.document_converter import DocumentConverter
from docling_core.types.doc import DoclingDocument
from textwrap import dedent
import subprocess
import tempfile

logger = logging.getLogger(__name__)

if not Path("workspace/intake.md").exists():
    Path("workspace/intake.md").write_text(Path("intake.example.md").read_text(encoding='utf-8'), encoding='utf-8')

@click.command()
def kickoff():
    """
    Run the crew.
    """

    output = ProjectResearchCrew().crew().kickoff(inputs={
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    })
    
    print(f"Token Usage: {output.token_usage}")

@click.command()
def download_knowledge():
    """
    Download knowledge files into the knowledge directory.
    """
    url_map = {
        "Förderrichtlinie Zentrales Innovationsprogramm Mittelstand.pdf": "https://www.zim.de/ZIM/Redaktion/DE/Downloads/Richtlinien/richtlinie-zim-2025.pdf?__blob=publicationFile&v=7",
        "Förderrichtlinie Zentrales Innovationsprogramm Mittelstand - Kerninhalt.pdf": "https://www.zim.de/ZIM/Redaktion/DE/Downloads/Richtlinien/richtlinie-zim-2025-kerninhalt.pdf?__blob=publicationFile&v=5",
        "Richtlinie zur Förderung von Transformationsprojekten.pdf": "https://www.bibb.de/dokumente/pdf/BAnz%20AT%2028.11.2024%20B1.pdf",
        "Bundeshaushaltsordnung.pdf": "https://www.gesetze-im-internet.de/bho/BHO.pdf",
        "Allgemeine Verwaltungsvorschriften zur Bundeshaushaltsordnung.pdf": "https://www.esf.de/portal/SharedDocs/PDFs/DE/Recht_VO/FP-2014-2020/vv_bho_44.pdf?__blob=publicationFile&v=1",
        "Allgemeine Nebenbestimmungen für Zuwendungen zur Projektförderung auf Kostenbasis (ANBest-P-Kosten).pdf": "https://www.bva.bund.de/SharedDocs/Downloads/DE/Aufgaben/ZMV/Zuwendungen_national/nebenbestimmungen_anbest_p_kosten_2025.pdf?__blob=publicationFile&v=4",
        "Hinweise für Antragsteller.pdf": "https://www.zim.de/ZIM/Redaktion/DE/Downloads/Formularcenter/A_Phase-Antrag/B_Kooperationsprojekt/B1_Ohne-Netzwerk/Downloads/hinweise-fuer-antragstellung-koop.pdf?__blob=publicationFile&v=2",
        "Hilfestellung zum Ausfüllen der Formulare.pdf": "https://www.zim.de/ZIM/Redaktion/DE/Downloads/Formularcenter/A_Phase-Antrag/B_Kooperationsprojekt/B1_Ohne-Netzwerk/Downloads/formular-hilfe-koop.pdf?__blob=publicationFile&v=2",
        "Beispiele für Leistungen zur Markteinführung.pdf": "https://www.zim.de/ZIM/Redaktion/DE/Downloads/beispiele-fuer-leistungen-zur-markteinfuehrung_2020.pdf?__blob=publicationFile&v=1",
        "Informationblatt - Einstufung von Unternehmen.pdf": "https://www.zim.de/ZIM/Redaktion/DE/Downloads/Formularcenter/A_Phase-Antrag/A_Einzelprojekt/B2_Mit-Netzwerk/Downloads/unternehmenstyp.pdf?__blob=publicationFile&v=1",
    }

    for filename, url in url_map.items():
        print(url)

        path = f"knowledge/{filename}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(path, "wb") as f:
            f.write(response.content)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
        
        # TODO replace subprocess
        # with pikepdf.open(path) as pdf:
        #     pdf.save(tmp_path, compression=pikepdf.CompressionLevel.prepress)

        subprocess.run([
            "gs",
            "-o", tmp_path,
            "-sDEVICE=pdfwrite",
            "-dPDFSETTINGS=/prepress",
            path
        ], check=True)
        
        shutil.move(tmp_path, path)


@click.command()
def import_knowledge():
    """
    Consume knowledge into the crew's knowledge storage.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding='utf-8') # type: ignore
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding='utf-8') # type: ignore

    converter = DocumentConverter()
    knowledge_dir = Path(KNOWLEDGE_DIRECTORY)
    file_paths = [
        str(p) for p in knowledge_dir.rglob("*") 
        if p.is_file() 
            and not p.name.startswith(".") 
            and not p.name.endswith(".summary.md")]

    allowed_suffixes = {fmt.value for fmt in converter.allowed_formats}
    valid_files = []
    ignored_files = []

    for path in file_paths:
        if not Path(path).exists():
            ignored_files.append(f"Not found: {path}")
        elif not any(str(path).lower().endswith(suffix) for suffix in allowed_suffixes):
            ignored_files.append(f"Unsupported format: {path}")
        else:
            valid_files.append(path)

    if ignored_files:
        print("The following files were ignored:")
        for f in ignored_files:
            print(f"  - {f}")

    if not valid_files:
        print("No valid files found for import.")
        return

    conv_results_iter = list(converter.convert_all(valid_files))
    content = [result.document for result in conv_results_iter]

    client = get_rag_client()

    try:
        client.delete_collection(collection_name="knowledge")
    except Exception as e:
        logger.debug(f"Collection deletion failed: {e}")

    chunker = create_chunker(ChunkingConfig())
    chunks = []

    async def create_summary(doc: DoclingDocument):
        llm = LLM(model="gpt-4.1")
        snippet = doc.export_to_markdown()[:1000]

        summary = llm.call(messages=[{
            "role": "system",
            "content": dedent(
                f"""
                You are an assistant that analyzes documents. You classify the snippet and create a summary of 3 sentences without giving details about the contents. Always use the document's language. Use the following md-format without fences like "```":

                ```
                ## {doc.name}
    
                Type: <type of document, e.g., Contract, Report, Email, Invoice, etc.>
                Creator: <document creator if available>
                Audience: <intended audience if available>
                Summary: <three-sentence summary>
                ```
                """)
        }, {
            "role": "user",
            "content": snippet
        }])

        summary_path = knowledge_dir / f"{doc.name}.summary.md"
        summary_path.write_text(summary, encoding="utf-8")


    async def process_document(doc):
        await create_summary(doc)

        doc_chunks = await chunker.chunk_document(
            doc.export_to_markdown(),
            doc.name,
            doc.origin.filename,
            doc.origin.model_dump(),
            doc, # type: ignore
        )
        
        result = []

        for chunk in doc_chunks:
            result.append(            {
                "doc_id": uuid4().hex,
                "content": chunk.content,
                "metadata": {
                    "chunk_index": chunk.index,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    **chunk.metadata
                },
            })
        
        return result

    async def main():
        results = await asyncio.gather(*(process_document(doc) for doc in content))
        for doc_chunks in results:
            chunks.extend(doc_chunks)

    asyncio.run(main())
    client.add_documents(collection_name="knowledge", documents=chunks)


@click.group()
def cli():
    pass


if __name__ == '__main__':
    cli.add_command(kickoff)
    cli.add_command(download_knowledge)
    cli.add_command(import_knowledge)
    cli()
