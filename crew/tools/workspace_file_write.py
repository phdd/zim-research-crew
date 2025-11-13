import os

from crewai.tools import BaseTool
from pydantic import BaseModel
from textwrap import dedent

class WorkspaceFileWriteToolInput(BaseModel):
    filename: str
    content: str

class WorkspaceFileWriteTool(BaseTool):
    name: str = "workspace_file_write"

    description: str = dedent("""
        A tool to write text content to a specified file.
        Always overwrites existing files.
        Accepts filename and content as input.
        Only plain text content is supported. Do not use for binary or non-text files.
    """)

    args_schema: type[BaseModel] = WorkspaceFileWriteToolInput

    def _run(self, filename: str, content: str) -> str:
        directory = "./workspace"

        try:
            filepath = os.path.join(directory, filename)

            # Create all parent directories for the file if they don't exist
            parent_dir = os.path.dirname(filepath)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            # Always overwrite
            with open(filepath, "w") as file:
                file.write(content)

            return f"Content successfully written to {filepath} (overwritten if existed)"
        except Exception as e:
            return f"An error occurred while writing to the file: {e!s}"
