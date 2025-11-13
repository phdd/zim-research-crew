"""
Document Chunk Range Retriever Tool.
"""
import click

from textwrap import dedent
from typing import Type

from chromadb.api import ClientAPI
from pydantic import BaseModel, Field

from crewai.tools import BaseTool
from crewai.rag.config.utils import get_rag_client


class DocumentChunkContextInput(BaseModel):
    """Input schema for DocumentChunkContextTool"""
    filename: str = Field(..., description="The filename of the document to retrieve context chunks from")
    chunk_index: int = Field(..., description="The central chunk index (will not be included)")
    before_context: int = Field(0, description="Number of chunks before the central chunk to include")
    after_context: int = Field(0, description="Number of chunks after the central chunk to include")


class DocumentChunkContextTool(BaseTool):
    name: str = "document_chunk_context"

    description: str = dedent(
        """
        Retrieve a range of document chunks from the vector database based on filename and chunk index range, EXCLUDING the chunk at 'chunk_index'. Use this tool to get surrounding context for specific chunks to check if there is relevant information nearby. This way you will not miss important details that are just outside the initially retrieved chunks. Always use this tool after performing a document search to check if there's more before or after that to maximize the recall of relevant information.
        """)

    args_schema: Type[BaseModel] = DocumentChunkContextInput

    def _format_results(self, results: list[dict]) -> str:
        """Format the results, using all available metadata."""
        return "".join([
            dedent("""
                   # Chunk index {chunk_index} in "{filename}" on page {page_no}

                   {content}
            """).format(
                chunk_index=result.get('metadata', {}).get('chunk_index', 'unknown'),
                filename=result.get('metadata', {}).get('filename', 'unknown'),
                page_no=result.get('metadata', {}).get('page_no', 'unknown'),
                content=result.get('content', '')
            ) for result in results
        ])

    def _run(self, filename: str, chunk_index: int, before_context: int = 0, after_context: int = 0) -> str:
        client = get_rag_client()
        chromadb: ClientAPI = client.client

        lowest_chunk_index = chunk_index - before_context
        highest_chunk_index = chunk_index + after_context

        # Exclude the chunk at chunk_index
        result = chromadb.get_collection(name="knowledge").get(
            where={
                "$and": [
                    {"filename": filename},
                    {"chunk_index": {"$gte": lowest_chunk_index}},
                    {"chunk_index": {"$lte": highest_chunk_index}},
                    {"chunk_index": {"$ne": chunk_index}}
                ]
            }
        )

        documents = result.get("documents") or []
        metadatas = result.get("metadatas") or []

        return self._format_results([{
            "content": doc,
            "metadata": meta
        } for doc, meta in zip(documents, metadatas)])


@click.command()
@click.argument('filename', type=click.STRING)
@click.argument('chunk_index', type=click.INT)
@click.option('--before-context', '-B', default=0, type=click.INT, help='Number of chunks before the central chunk to include')
@click.option('--after-context', '-A', default=0, type=click.INT, help='Number of chunks after the central chunk to include')
def main(filename: str, chunk_index: int, before_context: int, after_context: int):
    result = DocumentChunkContextTool()._run(
        filename=filename,
        chunk_index=chunk_index,
        before_context=before_context,
        after_context=after_context
    )
    print(result)

if __name__ == "__main__":
    main()
