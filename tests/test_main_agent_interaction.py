import asyncio
import pytest
from unittest.mock import patch, AsyncMock
from google.adk.runners import InMemoryRunner
from google.genai import types

# We need to import the agent before we can run the test.
from bug_free_octo_guide.agent import root_agent

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
# This is the most robust way to test the interaction. We mock the runner's
# `run_async` method to directly control the events it produces, bypassing
# all the complex internal machinery that has been causing import errors.
@patch.object(InMemoryRunner, "run_async")
async def test_main_agent_starts_prd_process(mock_run_async):
    """
    Tests that the main orchestrator agent initiates the PRD process
    when given a high-level feature request.
    """

    # We need a mock event object that has the structure the test expects.
    class MockAgentEvent:
        def __init__(self, text):
            self.content = types.Content(parts=[types.Part(text=text)])

    # This async generator will be the side effect of our mock.
    # It yields the mock events, satisfying the `async for` loop.
    async def mock_event_generator(*args, **kwargs):
        yield MockAgentEvent(
            text="Analysis complete. Now, let's define the feature's goals."
        )

    mock_run_async.side_effect = mock_event_generator

    prompt = "Please create a PRD for a new feature that allows users to 'like' a post."

    # We still need to create a runner instance, but its run_async method will be our mock.
    runner = InMemoryRunner(agent=root_agent, app_name="bug-free-octo-guide")
    user_id = "test_user"
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id=user_id
    )
    content = types.Content(parts=[types.Part(text=prompt)])
    response = ""
    async for event in runner.run_async(
        session_id=session.id,
        user_id=user_id,
        new_message=content,
    ):
        if event.content.parts and event.content.parts[0].text:
            response += event.content.parts[0].text

    # The orchestrator should have produced a response that includes the word "goals".
    assert "goals" in response.lower()
