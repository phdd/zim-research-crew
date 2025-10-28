#!.venv/bin/python
import click
import sys

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import click

from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker

from crewai.utilities.constants import KNOWLEDGE_DIRECTORY

from project_research_crew.crew import ProjectResearchCrew

@click.command()
@click.option('--user-input', type=str, help='User input string.')
@click.option('--user-input-file', type=click.Path(exists=True), help='Path to file containing user input.')
def kickoff(user_input, user_input_file):
    """
    Run the crew with with user input.
    """
    if bool(user_input) == bool(user_input_file):
        raise click.UsageError('You must provide exactly one of --user-input or --user-input-file.')

    if user_input:
        input_value = user_input
    else:
        with open(user_input_file, encoding='utf-8') as f:
            input_value = f.read().strip()

    ProjectResearchCrew().crew().kickoff(inputs={
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "user_input": input_value,
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

    knowledge_dir = Path(KNOWLEDGE_DIRECTORY)
    file_paths = [str(p) for p in knowledge_dir.rglob("*") if p.is_file() and not p.name.startswith(".")]

    converter = DocumentConverter()
    conv_results_iter = list(converter.convert_all(file_paths))
    content = [result.document for result in conv_results_iter]
    chunker = HybridChunker()
    chunks = []

    client = crew.knowledge.storage._get_client()
    client.delete_collection(collection_name="knowledge_crew")

    for doc in content:
        for chunk in chunker.chunk(doc):
            origin = chunk.meta.origin.model_dump() # type: ignore
            chunks.append({
                "doc_id": uuid4().hex,
                "metadata": origin,
                "content": f"{chunker.contextualize(chunk)}\n\nOrigin: {origin}\n\n",
            })

    client.add_documents(collection_name="knowledge_crew", documents=chunks)


@click.group()
def cli():
    pass


if __name__ == '__main__':
    cli.add_command(kickoff)
    cli.add_command(import_knowledge)
    cli()
