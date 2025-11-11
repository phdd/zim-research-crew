from typing import Any
from crewai.tools import BaseTool
from pydantic import BaseModel
import os

class WorkspaceFileWriterToolInput(BaseModel):
    filename: str
    content: str

class WorkspaceFileWriterTool(BaseTool):
    name: str = "Workspace File Writer Tool"
    description: str = (
        "A tool to write content to a specified file. "
        "Always overwrites existing files. "
        "Accepts filename and content as input."
    )
    args_schema: type[BaseModel] = WorkspaceFileWriterToolInput

    def _run(self, filename: str, content: str) -> str:
        directory = "./workspace"

        try:
            # Create the directory if it doesn't exist
            if not os.path.exists(directory):
                os.makedirs(directory)
        
            filepath = os.path.join(directory, filename)
        
            # Always overwrite
            with open(filepath, "w") as file:
                file.write(content)
        
            return f"Content successfully written to {filepath} (overwritten if existed)"
        except Exception as e:
            return f"An error occurred while writing to the file: {e!s}"
