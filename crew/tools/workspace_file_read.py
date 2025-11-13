from typing import Any
from crewai.tools import BaseTool
from pydantic import BaseModel
import os
from textwrap import dedent

class WorkspaceFileReadToolInput(BaseModel):
    filename: str

class WorkspaceFileReadTool(BaseTool):
    name: str = "workspace_file_read"

    description: str = dedent(
        """
        A tool to read content from a specified file.
        Accepts filename as input.
        """)

    args_schema: type[BaseModel] = WorkspaceFileReadToolInput

    def _run(self, filename: str) -> str:
        directory = "./workspace"
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "r") as file:
                content = file.read()
            return content
        except FileNotFoundError:
            return f"File {filepath} does not exist."
        except Exception as e:
            return f"An error occurred while reading the file: {e!s}"
