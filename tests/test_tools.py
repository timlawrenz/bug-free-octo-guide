import os
import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

pytest_plugins = ("pytest_asyncio",)

@pytest.mark.asyncio
async def test_tools():
    """Test the agent's basic ability on a few examples."""
    await AgentEvaluator.evaluate(
        "bug_free_octo_guide",
        os.path.join(os.path.dirname(__file__), "tools"),
        num_runs=1,
    )
