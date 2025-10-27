#!/usr/bin/env python
import os
import sys
from uuid import uuid4
import warnings

from datetime import datetime
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hierarchical_chunker import HierarchicalChunker
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter

from crewai.utilities.constants import KNOWLEDGE_DIRECTORY
from project_research_crew.crew import ProjectResearchCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run():
    """
    Run the crew.
    """
    inputs = {
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "user_input": os.getenv(
            "USER_INPUT", "Was macht die sit.institute GmbH?"
        ),
    }

    try:
        ProjectResearchCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": "AI LLMs", "current_year": str(datetime.now().year)}
    try:
        ProjectResearchCrew().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ProjectResearchCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {"topic": "AI LLMs", "current_year": str(datetime.now().year)}

    try:
        ProjectResearchCrew().crew().test(
            n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. Please provide JSON payload as argument."
        )

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": "",
    }

    try:
        result = ProjectResearchCrew().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")


def knowledge_import():
    """
    Consume knowledge into the crew's knowledge storage.
    """
    crew = ProjectResearchCrew().crew()

    assert crew.knowledge is not None
    assert crew.knowledge.storage is not None

    file_path = Path(KNOWLEDGE_DIRECTORY)
    file_paths = [str(p) for p in file_path.rglob("*") if p.is_file()]

    converter = DocumentConverter(
        allowed_formats=[
            InputFormat.MD,
            InputFormat.ASCIIDOC,
            InputFormat.PDF,
            InputFormat.DOCX,
            InputFormat.HTML,
            InputFormat.IMAGE,
            InputFormat.XLSX,
            InputFormat.PPTX,
        ]
    )

    conv_results_iter = list(converter.convert_all(file_paths))
    content = [result.document for result in conv_results_iter]
    chunker = HierarchicalChunker()
    chunks = []
    
    client = crew.knowledge.storage._get_client()
    client.delete_collection(collection_name="knowledge_crew")

    for doc in content:
        with open(f"./knowledge-import/{doc.name}.md", "w") as f:
            f.write(doc.export_to_markdown())

        for chunk in chunker.chunk(doc):
            metadata = chunk.meta.origin.model_dump() # type: ignore
            chunks.append({
                "doc_id": uuid4().hex,
                "metadata": metadata,
                "content": f"{chunk.text}\n\nMetadata: {metadata}",
            })

    client.add_documents(collection_name="knowledge_crew", documents=chunks)
