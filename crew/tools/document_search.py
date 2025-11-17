"""
Document search tool with cross-encoder reranking for internal RAG.

This module defines a CrewAI BaseTool that queries an internal vector
database and then reranks the retrieved documents using the
`cross-encoder/ms-marco-MiniLM-L-6-v2` model. The tool first fetches a
fixed number of candidates from the "knowledge" collection
(VECTOR_TOP_K), then applies the cross-encoder to score each
(query, content) pair, adds the score to the result, and sorts in
descending order of relevance.

The `_run` method returns the top `limit` results (default: RERANK_TOP_K) as a
single Markdown-formatted string. Each chunk includes:

- the source filename
- its chunk index within that file
- the cross-encoder score
- the original content

The tool is intended to be used before anything else search and
should always query documents using the user's original language.
"""
from typing import Type

import click

from textwrap import dedent
from pydantic import BaseModel, Field

from crewai.tools import BaseTool
from crewai.rag.types import SearchResult
from crewai.rag.config.utils import get_rag_client

from sentence_transformers import CrossEncoder


VECTOR_TOP_K = 30
RERANK_TOP_K = 5

CROSS_ENCODER = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

class DocumentSearchInput(BaseModel):
    """Input schema for DocumentSearchTool"""
    query: str = Field(..., description="The search query")

class DocumentSearchTool(BaseTool):
    name: str = "document_search"

    description: str = dedent(
        """
        A tool to search internal documents for relevant information to answer questions.
        Always use this tool first before searching anywhere else. If you find relevant information,
        cite the filename as the source. Always use the user's original language to query the documents!
        """)

    args_schema: Type[BaseModel] = DocumentSearchInput

    def _rerank(self, query: str, results: list) -> list:
        """Rerank results by cross-encoder, only changing order and adding score."""
        if not results:
            return []
        
        pairs = [(query, result["content"]) for result in results]
        scores = CROSS_ENCODER.predict(pairs)
        
        for result, score in zip(results, scores):
            result["score"] = float(score)
            
        # Sort in-place by score descending
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def _format_results(self, results: list[SearchResult]) -> str:
        """Format the reranked results, using all available metadata."""
        return "".join([
            dedent("""
                   ## Chunk index {chunk_index} in "{filename}" on page {page_no} (score={score:.2f})

                   {content}
            """).format(
                chunk_index=result.get('metadata', {}).get('chunk_index', 'unknown'),
                filename=result.get('metadata', {}).get('filename', 'unknown'),
                page_no=result.get('metadata', {}).get('page_no', 'unknown'),
                score=result.get('score', 0.0),
                content=result.get('content', '')
            ) for result in results
        ])

    def _run(self, query: str) -> str:
        client = get_rag_client()
        results = client.search(collection_name="knowledge", query=query, limit=VECTOR_TOP_K)

        if not results:
            return "No relevant information found."

        reranked = self._rerank(query, results)[:RERANK_TOP_K]
        document_names = set()

        for result in reranked:
            name = result.get('metadata', {}).get('title')

            if name:
                document_names.add(name)

        summaries = []

        for name in document_names:
            summary_path = f"knowledge/{name}.summary.md"

            with open(summary_path, "r", encoding="utf-8") as f:
                summaries.append(f.read())

        return dedent(
            """
            # Chunks found
            {chunks}

            # Documents involved

            {summaries}
            """).format(
                chunks=self._format_results(reranked),
                summaries="\n\n".join(summaries)
            )


@click.command()
@click.argument('query', type=click.STRING)
@click.option('--limit', '-l', default=RERANK_TOP_K, type=click.INT, help='Maximum number of results to return')
def main(query, limit):
    """Search internal documents for relevant information."""
    print(DocumentSearchTool()._run(query=query))

if __name__ == "__main__":
    main()
