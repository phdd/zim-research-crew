# Project Research Crew

Welcome to the Project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## TLDR: How to start

1. Install dependencies (if not done yet):

      ```bash
      pip install uv
      ```
2. Copy the example environment file and add your OpenAI key:
      ```bash
      cp .env.example .env
      # Edit .env and enter your OPENAI_API_KEY, SERPER_API_KEY etc.
      ```

3. Generate Atlassian token:
   - Visit [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens) and create a classic token without scope.
   - Add the generated token to your `.env` file as `CONFLUENCE_API_TOKEN` and `JIRA_API_TOKEN`.

4. Import your knowledge documents from the `knowledge/` folder:
      ```bash
      uv run main.py import-knowledge
      ```
5. Run the crew with example input
      ```bash
      cp request.example.md workspace/request.md
      uv run main.py kickoff
      ```

This will run and create a `workspace/report.md` file with the output of the research.

## Crew

### Cloud Traces

To use CrewAI Online (Cloud) and review your crew's activities, you can log in with the following command:

```bash
uv run crewai login
```

### Memory

If you want to delete or reset the memories of your crew, you can use the following command:

```bash
uv run crewai reset-memories --help
```

This command provides options to clear the stored memories of your crew agents.

### Customizing

- Modify `crew/config/agents.yaml` to define your agents
- Modify `crew/config/tasks.yaml` to define your tasks
- Modify `crew/crew.py` to add your own logic, tools and specific args
- Modify `main.py` to add custom inputs for your agents and tasks

### Understanding Your Crew

The project-research-crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.

## Roadmap

- [x] research tasks still output all details => writer context bloat
- [ ] add task to summarize the documents
  - use first 500 chars of each doc
  - infer contents write mardown file overview
  - tell reseach agent to look before and after the relevant chunks if there's more 
- [ ] Test Anthropic models
- [ ] Test langchains deepagents
- [x] add indexed chunk retrieval (get chunk surroundings for more context)
- [x] align tool names with python module names
- [x] fix research contexts (research docs are overwritten)
- [x] never cite files in `research/` folder
- [x] user-input from file, not from task description
- [x] add confluence as rag source
