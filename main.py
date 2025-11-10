#!.venv/bin/python
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import click
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from crewai.utilities.constants import KNOWLEDGE_DIRECTORY
from crew.crew import ProjectResearchCrew
from crew.utils.chunker import create_chunker, ChunkingConfig

if not Path("user-input.md").exists():
    Path("user-input.md").write_text(Path("user-input.example.md").read_text(encoding='utf-8'), encoding='utf-8')

@click.command()
def kickoff():
    """
    Run the crew.
    """

    with open(Path("user-input.md"), encoding='utf-8') as f:
        user_input = f.read().strip()

    ProjectResearchCrew().crew().kickoff(inputs={
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "user_input": user_input,
    })

@click.command()
def import_knowledge():
    """
    Consume knowledge into the crew's knowledge storage.
    """
    crew = ProjectResearchCrew().crew()

    assert crew.knowledge is not None
    assert crew.knowledge.storage is not None

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

    chunker = create_chunker(ChunkingConfig())
    client = crew.knowledge.storage._get_client()
    client.delete_collection(collection_name="knowledge_crew")
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
            result.append({
                "doc_id": uuid4().hex,
                "metadata": getattr(chunk, 'metadata', getattr(chunk, 'meta', {})),
                "content": getattr(chunk, 'content', str(chunk)),
            })
        
        return result

    async def main():
        results = await asyncio.gather(*(process_document(doc) for doc in content))
        for doc_chunks in results:
            chunks.extend(doc_chunks)

    asyncio.run(main())
    client.add_documents(collection_name="knowledge_crew", documents=chunks)


@click.group()
def cli():
    pass


if __name__ == '__main__':
    cli.add_command(kickoff)
    cli.add_command(import_knowledge)
    cli()
