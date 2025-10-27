import asyncio
import chainlit as cl

from datetime import datetime

from dotenv import load_dotenv
from crewai.tasks.task_output import TaskOutput
from crewai.tools.tool_types import ToolResult
from crewai.agents.parser import AgentFinish
from crewai.agents.parser import AgentAction

from project_research_crew.crew import ProjectResearchCrew

load_dotenv()


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
            "user_input": message.content,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
        },
    )

    await cl.Message(
        content=result.raw,
        elements=[
            cl.File(name="report.md", path="./report.md", display="inline"),
        ],
    ).send()
