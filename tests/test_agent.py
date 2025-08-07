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
