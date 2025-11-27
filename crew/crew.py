from typing import List, Literal

from pydantic import BaseModel
from mcp import StdioServerParameters

from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task, tool
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

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

    @tool
    def web_search(self):
        return SerperDevTool()
    
    @tool
    def scrape_website(self):
        return ScrapeWebsiteTool()

    @agent
    def intake_curator(self) -> Agent:
        return Agent(
            config=self.agents_config["intake_curator"],  # type: ignore[index]
        )

    @agent
    def zim_compliance_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["zim_compliance_extractor"],  # type: ignore[index]
        )

    @agent
    def success_metrics_formalizer(self) -> Agent:
        return Agent(
            config=self.agents_config["success_metrics_formalizer"],  # type: ignore[index]
        )

    @agent
    def sota_competition_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["sota_competition_researcher"],  # type: ignore[index]
        )

    @agent
    def zim_technical_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["zim_technical_writer"],  # type: ignore[index]
        )

    @agent
    def red_team_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["red_team_reviewer"],  # type: ignore[index]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    
    @task
    def initial_intake_processing(self) -> Task:
        return Task(
            config=self.tasks_config["initial_intake_processing"],  # type: ignore[index]
        )

    @task
    def extract_zim_compliance_guidelines(self) -> Task:
        return Task(
            config=self.tasks_config["extract_zim_compliance_guidelines"],  # type: ignore[index]
        )

    @task
    def formalize_success_metrics(self) -> Task:
        return Task(
            config=self.tasks_config["formalize_success_metrics"],  # type: ignore[index]
        )

    @task
    def research_state_of_the_art_and_competition(self) -> Task:
        return Task(
            config=self.tasks_config["research_state_of_the_art_and_competition"],  # type: ignore[index]
        )

    @task
    def write_final_zim_project_description(self) -> Task:
        return Task(
            config=self.tasks_config["write_final_zim_project_description"],  # type: ignore[index]
        )

    @task
    def quality_assurance_review(self) -> Task:
        return Task(
            config=self.tasks_config["quality_assurance_review"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ProjectResearchCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        )
