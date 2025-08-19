# ADK Best Practices

This document summarizes the key learnings and best practices discovered while working with the Google Agent Development Kit (ADK).

## Abstract Patterns

This section summarizes the key architectural and testing patterns that have been identified from the examples in the `google/adk-samples` repository.

### Architecture and Decoupling

*   **Hierarchical Agent Architecture:** Use a central orchestrator agent to manage specialized sub-agents and tools. This is a powerful pattern for building complex, multi-step agents. See the **Hierarchical Agent Architecture** example for more details.
*   **Separation of Concerns:** Separate the agent's logic, prompts, and tools into different files. This makes the code easier to read, understand, and modify. See the **Architecture and Decoupling** example for more details.
*   **Shared Libraries and Constants:** For larger agents, use a `shared_libraries` directory to store code that is used by multiple components. This avoids code duplication and makes the agent easier to maintain. See the **Shared Libraries and Constants** example for more details.
*   **Secure Architecture:** For agents that handle sensitive data, design a secure architecture that protects against prompt injection attacks and enforces fine-grained access control. See the **Secure Architecture** example for more details.
*   **Configuration and Callbacks:** For complex agents, use a dedicated `config.py` file to manage the agent's settings and use callbacks to add functionality without modifying the agent's core logic. See the **Configuration and Callbacks** example for more details.
*   **Dynamic Instructions:** Use a `before_agent_callback` to dynamically modify the agent's instructions before each turn. This allows the agent to adapt to different contexts. See the **Dynamic Instructions** example for more details.
*   **AgentTool:** Use the `AgentTool` class to use an agent as a tool for another agent. This is useful for breaking down a complex task into smaller, more manageable sub-tasks. See the **AgentTool** example for more details.
*   **Workflow Orchestration:** For agents that perform a multi-stage, non-conversational workflow, use a root agent to orchestrate the activity of the other agents. See the **Workflow Orchestration** example for more details.
*   **Human-in-the-Loop:** For agents that require human oversight or approval, use a custom agent to create a human-in-the-loop workflow. See the **Human-in-the-Loop** example for more details.
*   **Looping and Sequential Agents:** For agents that need to perform a series of steps in a specific order, use the `SequentialAgent` and `LoopAgent` classes. See the **Looping and Sequential Agents** example for more details.
*   **Pipeline Agents:** For agents that perform a complex, multi-stage workflow, use a `SequentialAgent` to define a pipeline of sub-agents. See the **Pipeline Agents** example for more details.
*   **FunctionTool:** Use the `FunctionTool` class to wrap a Python function and make it available to an agent. This is useful for creating simple tools that do not require the complexity of a sub-agent. See the **FunctionTool** example for more details.
*   **RAG Agents:** For agents that need to retrieve information from a large corpus of documents, use the `VertexAiRagRetrieval` tool. See the **RAG Agents** example for more details.

### Testing and Evaluation

*   **Unit and Integration Testing:** Use the `InMemoryRunner` to test the agent in a controlled, isolated environment. Use `pytest` and `pytest-asyncio` for asynchronous testing. See the **Testing with `InMemoryRunner`** example for more details.
*   **Evaluation:** Use the `AgentEvaluator` to run data-driven evaluations. Create a `data` directory with `.test.json` files containing test cases and a `test_config.json` file to define the success criteria. See the **Testing and Evaluation** example for more details.
*   **Advanced Evaluation:** For more complex agents, use a more structured evaluation format that supports multi-turn conversations. See the **Advanced Evaluation** example for more details.
*   **Manual Testing:** For agents that are deployed to a remote environment, use an interactive script to manually test the agent. See the **Manual Testing** example for more details.

### Prompting and Tool-Using Behavior

*   **Prompting is Key:** The behavior of an `LlmAgent` is highly dependent on its instructions. Clear, explicit instructions are crucial for guiding the agent to the desired outcome. See the **Prompting is Key** example for more details.
*   **Tool-Using Behavior:** To encourage an agent to use a tool, the tool must be well-described with a clear name and a descriptive docstring. See the **Tool-Using Behavior** example for more details.

## Examples

This section provides detailed examples of the patterns and best practices described above.

### 1. Hierarchical Agent Architecture

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

### 2. Architecture and Decoupling

The ADK encourages a modular and decoupled architecture, which makes agents easier to develop, test, and maintain.

**Key Principles:**

*   **Separation of Concerns:** Separate the agent's logic, prompts, and tools into different files. This makes the code easier to read, understand, and modify.
*   **Single-Responsibility Principle:** Each component should have a single, well-defined responsibility. For example, a sub-agent should be responsible for a specific task, and a tool should be responsible for a specific action.
*   **Callbacks for Post-Processing:** Use callbacks to perform post-processing on the agent's response. This keeps the agent's core logic clean and focused on its primary task.

**Example:**

The `llm-auditor` agent demonstrates these principles effectively:

*   The main agent is a `SequentialAgent` that orchestrates two sub-agents: `critic` and `reviser`.
*   Each sub-agent has its own directory with separate `agent.py` and `prompt.py` files.
*   The `critic` agent uses a `_render_reference` callback to format the references in its response.

**Shared Libraries and Constants:**

For larger agents with multiple sub-agents and tools, it is a good practice to use a `shared_libraries` directory to store code that is used by multiple components. This avoids code duplication and makes the agent easier to maintain.

The `brand-search-optimization` agent uses a `shared_libraries/constants.py` file to define constants that are used throughout the agent, such as the model name, the agent's name, and its description. This makes it easy to change these values in one place.

**Secure Architecture:**

For agents that handle sensitive data or perform critical operations, it is important to design a secure architecture that protects against prompt injection attacks and enforces fine-grained access control.

The `camel` agent demonstrates how to build a secure agent using the CaMeL framework:

*   **`SecurityPolicyEngine`:** A class that defines the security policies for the agent's tools. Each tool call is preceded by a security policy check.
*   **Capabilities:** Each tool is defined with a set of capabilities that specify which users can access the tool and what data they can read.
*   **Stateless QLLM:** A quarantined LLM is used for stateless interactions to prevent information leakage across multiple requests.

**Configuration and Callbacks:**

For complex agents, it is a good practice to use a dedicated `config.py` file to manage the agent's settings. This makes it easy to configure the agent for different environments.

The `customer-service` agent uses a `config.py` file to manage the agent's settings, such as the model name and the agent's name. It also makes extensive use of callbacks to perform actions before and after the agent, model, and tools are called. This is a powerful way to add functionality to the agent without modifying its core logic.

**Dynamic Instructions:**

For agents that need to adapt to different contexts, you can use a `before_agent_callback` to dynamically modify the agent's instructions before each turn.

The `data-science` agent uses a `before_agent_callback` to get the database schema and add it to the agent's instructions. This allows the agent to have the most up-to-date information about the database schema without having to be redeployed.

**AgentTool:**

The `AgentTool` class is a powerful tool for building hierarchical agents. It allows you to use an agent as a tool for another agent. This is useful for breaking down a complex task into smaller, more manageable sub-tasks.

The `financial-advisor` agent uses the `AgentTool` to create a financial coordinator that orchestrates a series of expert sub-agents. Each sub-agent is responsible for a specific task, such as analyzing a market ticker, developing trading strategies, defining execution plans, and evaluating the overall risk.

**Workflow Orchestration:**

For agents that perform a multi-stage, non-conversational workflow, you can use a root agent to orchestrate the activity of the other agents.

The `fomc-research` agent uses a `root_agent` to coordinate the retrieval of individual research components and generate a detailed analysis report. This is a good example of how to use a multi-agent architecture to automate a complex workflow.

**Human-in-the-Loop:**

For agents that require human oversight or approval, you can use a custom agent to create a human-in-the-loop workflow.

The `gemini-fullstack` agent uses a custom `EscalationChecker` agent to stop the research loop if the research evaluation grade is "pass". This is a good example of how to use a custom agent to create a human-in-the-loop workflow.

**Looping and Sequential Agents:**

For agents that need to perform a series of steps in a specific order, you can use the `SequentialAgent` and `LoopAgent` classes.

The `image-scoring` agent uses a `SequentialAgent` to generate and score images, and a `LoopAgent` to repeat the process until the image score meets a quality threshold. This is a good example of how to use these classes to create a complex, multi-step workflow.

**Pipeline Agents:**

For agents that perform a complex, multi-stage workflow, you can use a `SequentialAgent` to define a pipeline of sub-agents.

The `machine-learning-engineering` agent uses a `SequentialAgent` to define a pipeline of sub-agents for solving a machine learning task. Each sub-agent is responsible for a specific stage of the pipeline, such as initialization, refinement, ensemble, and submission.

**FunctionTool:**

The `FunctionTool` class is a convenient way to wrap a Python function and make it available to an agent. This is useful for creating simple tools that do not require the complexity of a sub-agent.

The `personalized-shopping` agent uses the `FunctionTool` to wrap its `search` and `click` tools. This is a good example of how to use the `FunctionTool` to create simple, reusable tools.

**RAG Agents:**

For agents that need to retrieve information from a large corpus of documents, you can use the `VertexAiRagRetrieval` tool.

The `RAG` agent uses the `VertexAiRagRetrieval` tool to retrieve documentation and reference materials from a RAG corpus. This is a good example of how to use the `VertexAiRagRetrieval` tool to build a RAG agent.

### 3. Testing with `InMemoryRunner`

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
        user_id=session.session_id,
        new_message=content,
    ):
        if event.content.parts and event.content.parts[0].text:
            response = event.content.parts[0].text

    # The agent should ask for more information.
    assert "what" in response.lower() or "which" in response.lower() or "?" in response
```

### 4. Prompting is Key

The behavior of an `LlmAgent` is highly dependent on its instructions. Clear, explicit instructions are crucial for guiding the agent to the desired outcome.

**Best Practices:**

*   Be specific about the agent's role, goal, and the steps it should take.
*   If you want the agent to use a specific tool, mention it by name in the instructions.
*   Provide examples of the expected input and output.

### 5. Tool-Using Behavior

To encourage an agent to use a tool, the tool must be well-described with a clear name and a descriptive docstring that explains what the tool does, its arguments, and what it returns.

**Best Practices:**

*   Use a clear and descriptive name for the tool.
*   Write a detailed docstring that explains:
    *   What the tool does.
    *   The arguments it takes.
    *   What it returns.
*   Use type hints for the arguments and the return value.

### 6. Testing and Evaluation

The ADK provides a powerful framework for testing and evaluating agents.

**Unit and Integration Testing:**

*   Use the `InMemoryRunner` to test the agent in a controlled, isolated environment.
*   Use `pytest` and `pytest-asyncio` for asynchronous testing.
*   Write "happy path" tests to check for expected behavior.
*   Use `dotenv` to manage environment variables in tests.

**Evaluation:**

*   Use the `AgentEvaluator` to run data-driven evaluations.
*   Create a `data` directory with `.test.json` files containing test cases.
*   Each test case should have a `query`, `expected_tool_use`, and `reference` field.
*   Create a `test_config.json` file to define the success criteria for the evaluation.
*   Use criteria like `tool_trajectory_avg_score` and `response_match_score` to measure the agent's performance.

**Example `test_eval.py`:**

```python
import pathlib
import dotenv
import pytest
from google.adk.evaluation import AgentEvaluator

pytest_plugins = ("pytest_asyncio",)

@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()

@pytest.mark.asyncio
async def test_all():
    """Test the agent's basic ability on a few examples."""
    await AgentEvaluator.evaluate(
        "llm_auditor",
        str(pathlib.Path(__file__).parent / "data"),
        num_runs=5,
    )
```

**Example `blueberries.test.json`:**

```json
[
  {
    "query": "Q: Why the blueberries are blue? A: Because blueberries have pigments on their skin.",
    "expected_tool_use": [],
    "reference": "I will revise the answer to address the inaccuracies identified in the previous analysis. Revised answer: Because blueberries have a coating of wax on their surface that scatters blue light."
  }
]
```

**Example `test_config.json`:**

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.35
  }
}
```

**Advanced Evaluation:**

For more complex agents, you can use a more structured evaluation format that supports multi-turn conversations.

*   **Structured Evaluation Sets:** The evaluation data is structured into an `eval_set` with multiple `eval_cases`.
*   **Conversation History:** Each `eval_case` can contain a `conversation` with multiple turns. This is useful for testing stateful agents that need to remember the context of the conversation.
*   **Detailed Logging:** The format includes detailed information about each turn, including the user's input, the agent's final response, and any intermediate tool uses and responses.

**Example `academic_research_evalset.test.json`:**

```json
{
  "eval_set_id": "academic_research_evalset",
  "name": "academic_research_evalset",
  "description": null,
  "eval_cases": [
    {
      "eval_id": "hello",
      "conversation": [
        {
          "invocation_id": "e-ea7feda9-2e21-43c8-9149-97d4c48db2a3",
          "user_content": {
            "parts": [
              {
                "text": "hello"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "Hello! I am an AI Research Assistant. I can help you analyze a seminal paper, find recent citing papers, and suggest future research directions.\n\nTo begin, please provide the seminal paper you wish to analyze as a PDF."
              }
            ]
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          }
        }
      ]
    }
  ]
}
```

**Manual Testing:**

For agents that are deployed to a remote environment like Vertex AI Agent Engine, you can use an interactive script to manually test the agent.

*   Use the `VertexAiSessionService` to create and manage sessions with the deployed agent.
*   Create an interactive command-line interface for sending messages to the agent and receiving its responses.
*   Use `agent_engine.stream_query` to get a streaming response from the agent.

**Example `test_deployment.py`:**

```python
import os
import vertexai
from vertexai import agent_engines
from google.adk.sessions import VertexAiSessionService
from dotenv import load_dotenv
import asyncio

load_dotenv()

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)

session_service = VertexAiSessionService(project=os.getenv("GOOGLE_CLOUD_PROJECT"),location=os.getenv("GOOGLE_CLOUD_LOCATION"))
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")

session = asyncio.run(session_service.create_session(
    app_name=AGENT_ENGINE_ID,
    user_id="123",
))

agent_engine = agent_engines.get(AGENT_ENGINE_ID)

print("Type 'quit' to exit.")
while True:
    user_input = input("Input: ")
    if user_input == "quit":
        break

    for event in agent_engine.stream_query(
        user_id="123", session_id=session.id, message=user_input
    ):
        print(event)

asyncio.run(session_service.delete_session(session_id=session.id))
```