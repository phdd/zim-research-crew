import os

from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool
from crewai_tools import ScrapeWebsiteTool, SerperDevTool, FileReadTool, FileWriterTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class ProjectResearchCrew:
    """ProjectResearchCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @tool
    def web_search(self):
        return SerperDevTool()

    @tool
    def web_scrape(self):
        return ScrapeWebsiteTool()

    @tool
    def read_file(self):
        return FileReadTool()
    
    @tool
    def write_file(self):
        return FileWriterTool()

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],  # type: ignore[index]
            verbose=True
        )
    
    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config["writer"],  # type: ignore[index]
            verbose=True
        )

    @agent
    def critic(self) -> Agent:
        return Agent(
            config=self.agents_config["critic"],  # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research(self) -> Task:
        return Task(
            config=self.tasks_config["research"],  # type: ignore[index]
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
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ProjectResearchCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            knowledge_sources=[StringKnowledgeSource(content="dummy source")],
            process=Process.hierarchical,
            manager_llm="gpt-4.1",
            planning=True,
            memory=True,
            verbose=True,
        )
