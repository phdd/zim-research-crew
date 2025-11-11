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

from textwrap import dedent
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from crewai.rag.config.utils import get_rag_client

import sys
from sentence_transformers import CrossEncoder


VECTOR_TOP_K = 30
RERANK_TOP_K = 5

CROSS_ENCODER = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

class DocumentSearchInput(BaseModel):
    """Input schema for DocumentSearchTool."""
    query: str = Field(..., description="The search query.")
    limit: int = Field(RERANK_TOP_K, description="The maximum number of results to return.")

class DocumentSearchTool(BaseTool):
    name: str = "Document Search"
    description: str = (
        "A tool to search internal documents for relevant information to answer questions. "
        "Always use this tool first before searching anywhere else. If you find relevant information, "
        "cite the filename as the source. Always use the users original language to query the documents! "
    )
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

    def _format_results(self, results: list) -> str:
        """Format the reranked results, using all available metadata."""
        return "".join([
            dedent("""
                   # File "{filename}" / Chunk #{chunk_index} (score={score:.4f})

                   {content}
            """).format(
                filename=result.get('metadata', {}).get('filename', 'unknown'),
                chunk_index=result.get('metadata', {}).get('chunk_index', 'unknown'),
                score=result.get('score', 0.0),
                content=result.get('content', '')
            ) for result in results
        ])

    def _run(self, query: str, limit: int = RERANK_TOP_K) -> str:
        client = get_rag_client()
        results = client.search(collection_name="knowledge", query=query, limit=VECTOR_TOP_K)

        if not results:
            return "No relevant documents found."

        reranked = self._rerank(query, results)
        return self._format_results(reranked[:limit])


if __name__ == "__main__":
    print(DocumentSearchTool()._run(
        query=sys.argv[1] if len(sys.argv) > 1 else input("Query: ")))
