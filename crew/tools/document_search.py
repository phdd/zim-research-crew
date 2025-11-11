from textwrap import dedent

from typing import Type, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from crewai.rag.config.utils import get_rag_client

from sentence_transformers import CrossEncoder
import sys

# cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

class DocumentSearchInput(BaseModel):
    """Input schema for DocumentSearchTool."""
    query: str = Field(..., description="The search query.")
    limit: int = Field(10, description="The maximum number of results to return.")

class DocumentSearchTool(BaseTool):
    name: str = "Document Search"
    description: str = "A tool to search internal documents for relevant information to answer questions. Always use this tool first before searching the web. If you find relevant information, cite the filename as the source. Always use the users original language to query the documents!"
    args_schema: Type[BaseModel] = DocumentSearchInput

    def _run(self, query: str, limit: int = 10) -> str:
        client = get_rag_client()
        results = client.search(collection_name="knowledge", query=query, limit=limit)
        
        # pairs = [(query, doc["content"]) for doc in results]
        # scores = cross_encoder.predict(pairs)
        # results = [doc for _, doc in sorted(zip(scores, results), reverse=True)[:limit]]
    
        return "".join([
            dedent("""
                   # File "{filename}" / Chunk #{chunk_index}

                   {content}
            """).format(
                filename=result['metadata'].get('filename', 'unknown'),
                chunk_index=result['metadata'].get('chunk_index', 'unknown'),
                content=result['content']
            ) for result in results
        ])
    
if __name__ == "__main__":
    print(DocumentSearchTool()._run(
        query=sys.argv[1] if len(sys.argv) > 1 else input("Query: "),
        limit=2))
