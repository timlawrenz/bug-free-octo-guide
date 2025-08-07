# ADK Best Practices

This document summarizes the key learnings and best practices discovered while working with the Google Agent Development Kit (ADK).

## 1. Hierarchical Agent Architecture

The `google-adk` promotes a hierarchical agent architecture where a central `LlmAgent` orchestrates specialized sub-agents and tools. This is a powerful pattern for building complex, multi-step agents.

**Implementation:**

*   **Orchestrator:** An `LlmAgent` that is given a high-level goal and a list of tools.
*   **Sub-Agents:** Other `LlmAgent`s that are specialized for a specific task.
*   **Tools:** Simple Python functions that perform a specific action.
*   **`AgentTool`:** A wrapper class that allows an `LlmAgent` to be used as a tool by another `LlmAgent`.

**Example:**

```python
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools.agent_tool import AgentTool
from .agents.prd_writer_agent import PrdWriterAgent
from .tools.context_analysis_tool import analyze_repo

root_agent = LlmAgent(
    model=Gemini(),
    name="bug_free_octo_guide",
    instruction=(
        "You are a project manager. Your goal is to create a PRD. "
        "First, analyze the provided repository to understand the project context. "
        "Then, use the `PrdWriterAgent` to create a PRD based on the user's request and the repository context."
    ),
    tools=[
        analyze_repo,
        AgentTool(agent=PrdWriterAgent(llm=Gemini())),
    ],
)
```

## 2. Testing with `InMemoryRunner`

The most reliable way to test an ADK agent is to use the `InMemoryRunner`. This runs the agent in a realistic, in-memory environment and allows you to test its behavior by making assertions about its responses to various prompts.

**Implementation:**

*   Use `pytest` and `pytest-asyncio` for testing.
*   Create an `InMemoryRunner` with the agent you want to test.
*   Create a session and a message.
*   Run the agent with the `runner.run_async` method.
*   Make assertions about the agent's response.

**Example:**

```python
import asyncio
import pytest
from bug_free_octo_guide.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_agent_asks_for_clarification():
    """
    Tests that the agent asks for clarification when given a vague prompt.
    """
    prompt = "Please create a PRD."

    runner = InMemoryRunner(agent=root_agent, app_name="bug-free-octo-guide")
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = types.Content(parts=[types.Part(text=prompt)])
    response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content.parts and event.content.parts[0].text:
            response = event.content.parts[0].text

    # The agent should ask for more information.
    assert "what" in response.lower() or "which" in response.lower() or "?" in response
```

## 3. Prompting is Key

The behavior of an `LlmAgent` is highly dependent on its instructions. Clear, explicit instructions are crucial for guiding the agent to the desired outcome.

**Best Practices:**

*   Be specific about the agent's role, goal, and the steps it should take.
*   If you want the agent to use a specific tool, mention it by name in the instructions.
*   Provide examples of the expected input and output.

## 4. Tool-Using Behavior

To encourage an agent to use a tool, the tool must be well-described with a clear name and a descriptive docstring that explains what the tool does, its arguments, and what it returns.

**Best Practices:**

*   Use a clear and descriptive name for the tool.
*   Write a detailed docstring that explains:
    *   What the tool does.
    *   The arguments it takes.
    *   What it returns.
*   Use type hints for the arguments and the return value.
