import asyncio
import pytest
from bug_free_octo_guide.agents.prd_writer_agent import PrdWriterAgent
from google.adk.models import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_prd_writer_agent_assembles_prd():
    """
    Tests that the PrdWriterAgent assembles a PRD.
    """
    agent = PrdWriterAgent(llm=Gemini())
    prompt = """
    Goals: Allow users to comment on documents.
    Solution: Add a `Comment` model.
    API Changes: Add a `POST /documents/:id/comments` endpoint.
    DB Schema: Add a `comments` table.
    Implementation: Create a `CreateComment` command.
    Testing: Add a request spec for the new endpoint.
    """

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

    assert "Product Requirements Document" in response
    assert "Goals" in response
    assert "Solution" in response
    assert "API Changes" in response
    assert "DB Schema" in response
    assert "Implementation" in response
    assert "Testing" in response
