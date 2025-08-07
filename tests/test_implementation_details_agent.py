import asyncio
import pytest
from bug_free_octo_guide.agents.implementation_details_agent import ImplementationDetailsAgent
from google.adk.models import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_implementation_details_agent_asks_about_classes():
    """
    Tests that the ImplementationDetailsAgent asks about classes.
    """
    agent = ImplementationDetailsAgent(llm=Gemini())
    prompt = "We need to add a commenting feature."

    runner = InMemoryRunner(agent=agent, app_name="bug-free-octo-guide")
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

    assert "class" in response.lower() or "module" in response.lower()
