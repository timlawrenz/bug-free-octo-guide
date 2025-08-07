import asyncio
import pytest
from bug_free_octo_guide.agents.solution_proposal_agent import SolutionProposalAgent
from google.adk.models import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_solution_proposal_agent_proposes_solution():
    """
    Tests that the SolutionProposalAgent proposes a solution.
    """
    agent = SolutionProposalAgent(llm=Gemini())
    prompt = "The goal is to allow users to add comments to documents to facilitate collaboration."

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

    assert "solution" in response.lower() or "design" in response.lower() or "implement" in response.lower()
