#!.venv/bin/python
import os
import sys
import asyncio

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import logging
import click

from crewai.rag.config.utils import get_rag_client
from docling.document_converter import DocumentConverter
from crewai.utilities.constants import KNOWLEDGE_DIRECTORY
from crew.crew import ProjectResearchCrew
from crew.utils.chunker import create_chunker, ChunkingConfig

logger = logging.getLogger(__name__)

if not Path("workspace/request.md").exists():
    Path("workspace/request.md").write_text(Path("request.example.md").read_text(encoding='utf-8'), encoding='utf-8')

@click.command()
def kickoff():
    """
    Run the crew.
    """

    output = ProjectResearchCrew().crew().kickoff(inputs={
        "jira_url": os.getenv("JIRA_URL", ""),
        "jira_available": bool(os.getenv("JIRA_API_TOKEN", "")),
        "confluence_available": bool(os.getenv("CONFLUENCE_API_TOKEN", "")),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    })
    
    print(f"Token Usage: {output.token_usage}")

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
    file_paths = [str(p) for p in knowledge_dir.rglob("*") if p.is_file() and not p.name.startswith(".")]

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

    async def process_document(doc):
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
    cli.add_command(import_knowledge)
    cli()
