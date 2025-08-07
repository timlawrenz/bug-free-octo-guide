import asyncio
import pytest
from bug_free_octo_guide.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_orchestrator_asks_for_structured_goals():
    """
    Tests that the orchestrator asks for the structured information
    needed to call the `define_goals` tool.
    """
    prompt = "I want to add a commenting feature to the RAG agent in the https://github.com/google/adk-samples repository."

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

    # The orchestrator should now ask for the specific arguments
    # required by the `define_goals` tool.
    response_lower = response.lower()
    assert "objective" in response_lower
    assert "metric" in response_lower
    assert "non-goal" in response_lower
