import asyncio
import chainlit as cl

from datetime import datetime

from dotenv import load_dotenv
from chainlit import run_sync
from crewai.tools import BaseTool
from crewai.tasks.task_output import TaskOutput
from crewai.tools.tool_types import ToolResult
from crewai.agents.parser import AgentFinish
from crewai.agents.parser import AgentAction

from project_research_crew.crew import ProjectResearchCrew

load_dotenv()


def ask_human(question: str) -> str:
    human_response = run_sync(cl.AskUserMessage(content=f"{question}").send())

    if human_response and "output" in human_response:
        return human_response["output"]
    else:
        return "No response."


class HumanInputContextTool(BaseTool):
    name: str = "Ask Human a questions"
    description: str = (
        "Use this tool to ask questions to the human in case additional context is needed"
    )

    def _run(self, question: str) -> str:
        return ask_human(question)


human_tool = HumanInputContextTool()


async def callback(payload):
    if isinstance(payload, AgentFinish) or isinstance(payload, AgentAction):
        await cl.Message(content=payload.thought.replace("Thought: ", "")).send()
    elif isinstance(payload, TaskOutput):
        return
    elif isinstance(payload, ToolResult):
        return
    else:
        await cl.Message(content=str(payload)).send()


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content="Hello! I'm here to help you research your project. Ask me anything about the project files and I'll get back to you with a report."
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    crew = ProjectResearchCrew().crew()

    crew.step_callback = lambda step: asyncio.run(callback(step))
    crew.task_callback = lambda task: asyncio.run(callback(task))

    for agent in crew.agents:
        agent.callbacks.append(lambda payload: asyncio.run(callback(payload)))

    result = await asyncio.to_thread(
        crew.kickoff,
        inputs={
            "question": message.content,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
        },
    )

    await cl.Message(
        content=result.raw,
        elements=[
            cl.File(name="report.md", path="./report.md", display="inline"),
        ],
    ).send()
