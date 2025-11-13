from typing import List, Literal

from pydantic import BaseModel
from mcp import StdioServerParameters

from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task, tool
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput

from crew.tools import (
    DocumentChunkContextTool,
    DocumentSearchTool,
    WorkspaceFileWriteTool,
    WorkspaceFileReadTool,
)

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

class ReviewOutput(BaseModel):
    result: Literal["approved", "changes_requested"]
    requested_changes: List[str]

@CrewBase
class ProjectResearchCrew:
    """ProjectResearchCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    mcp_server_params = [StdioServerParameters(
        command="uvx",
        # https://github.com/sooperset/mcp-atlassian/issues/721#issuecomment-3405125937
        args=["--with", "pydantic<2.12", "mcp-atlassian", "--env-file=.env", "--read-only"],
    )]

    @staticmethod
    def with_mcp_tools(task_method):
        """
        Decorator to add the appropriate MCP tools from the configuration to the task.
        Task-specific tools do not work with decorators when using MCP. Therefore, 
        they must be defined in a separate configuration field and injected at runtime.
        """
        def wrapper(self, *args, **kwargs):
            # Call the original method to get the Task
            task = task_method(self, *args, **kwargs)

            # Determine the config name from the method name
            config_name = task_method.__name__
            config = self.tasks_config[config_name]
            all_mcp_tools = self.get_mcp_tools()  # type: ignore
            task_mcp_tools = [t for t in all_mcp_tools if t.name in config["mcp_tools"]]
            tools = task.tools if isinstance(task.tools, list) else []
            task.tools = tools + list(task_mcp_tools)

            return task

        wrapper.__name__ = task_method.__name__
        wrapper.__doc__ = task_method.__doc__

        return wrapper

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    
    @tool
    def document_chunk_context(self):
        return DocumentChunkContextTool()
    
    @tool
    def document_search(self):
        return DocumentSearchTool()

    @tool
    def workspace_file_read(self):
        return WorkspaceFileReadTool()
    
    @tool
    def workspace_file_write(self):
        return WorkspaceFileWriteTool()

    @agent
    def atlassian_knowledge_manager(self):
        return Agent(
            config=self.agents_config["atlassian_knowledge_manager"],  # type: ignore[index]
            verbose=True
        )
    
    @agent
    def document_knowledge_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["document_knowledge_manager"],  # type: ignore[index]
            verbose=True
        )
    
    @agent
    def corporate_communications_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["corporate_communications_specialist"],  # type: ignore[index]
            verbose=True
        )

    @agent
    def critical_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["critical_reviewer"],  # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    
    @task
    def document_research(self) -> Task:
        return Task(
            config=self.tasks_config["document_research"],  # type: ignore[index]
        )
    
    @task
    @with_mcp_tools
    def confluence_research(self) -> Task:
        return Task(
            config=self.tasks_config["confluence_research"],  # type: ignore[index]
        )
    
    @task
    @with_mcp_tools
    def jira_research(self) -> Task:
        return Task(
            config=self.tasks_config["jira_research"],  # type: ignore[index]
        )

    @task
    def write_report(self) -> Task:
        return Task(
            config=self.tasks_config["write_report"],  # type: ignore[index]
        )

    @task
    def review_report(self) -> Task:
        return Task(
            config=self.tasks_config["review_report"],  # type: ignore[index]
            output_pydantic=ReviewOutput,
        )
    
    @task
    def improve_report(self) -> ConditionalTask:
        def changes_requested(output: TaskOutput) -> bool:
            return output.pydantic.result == "changes_requested" # type: ignore

        return ConditionalTask(
            config=self.tasks_config["improve_report"],  # type: ignore[index]
            condition=changes_requested
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ProjectResearchCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            # process=Process.hierarchical,
            # manager_llm="gpt-4.1",
            # planning=True,
            # memory=True,
            verbose=True,
        )
