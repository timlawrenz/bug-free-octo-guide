import asyncio
import pytest
from google.adk.models import Gemini
from bug_free_octo_guide.agents.goals_agent import GoalsAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_goals_agent_asks_about_goals():
    """
    Tests that the GoalsAgent asks about the feature's goals.
    """
    agent = GoalsAgent(llm=Gemini())
    prompt = "I want to add a new feature."

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

    assert "goal" in response.lower() or "objective" in response.lower()
