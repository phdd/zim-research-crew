# Project Research Crew

Welcome to the Project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
uv run crewai install
```

Copy the `.env.example` file to `.env` and enter your `OPENAI_API_KEY` there.


## CrewAI Cloud

To use CrewAI Online (Cloud) and review your crew's activities, you can log in with the following command:

```bash
uv run crewai login
```

After logging in, you will be able to view traces. This feature allows you to track and understand exactly what actions and decisions your crew has made.

## Knowledge Base


**Important:** To import the documents for the knowledge base, you must first run the following command:

```bash
uv run knowledge_import
```

Only after this step will the documents be available for research.

Place all documents that should serve as a basis for research in the `knowledge/` folder. This includes PDF files, images, CSVs, or any other relevant file formats.

## Crew Memory

If you want to delete or reset the memories of your crew, you can use the following command:

```bash
uv run crewai reset-memories --help
```

This command provides options to clear the stored memories of your crew agents.

## Customizing

- Modify `src/project_research_crew/config/agents.yaml` to define your agents
- Modify `src/project_research_crew/config/tasks.yaml` to define your tasks
- Modify `src/project_research_crew/crew.py` to add your own logic, tools and specific args
- Modify `src/project_research_crew/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
uv run crewai run
```

### Run with Chainlit Frontend

To run the Crew with a Chainlit frontend for enhanced interaction and visualization, use the following command from the root folder of your project:

```bash
uv run chainlit run src/project_research_crew/chainlit.py
```

This command initializes the project-research-crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The project-research-crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
