import subprocess
import pytest

def test_agent_flow_goals_to_solution():
    """
    Tests that the agent correctly transitions from defining goals to
    proposing a solution in a multi-turn conversation.
    """
    process = subprocess.Popen(
        ["poetry", "run", "adk", "run", "bug_free_octo_guide"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line-buffered
    )

    # Turn 1: User provides initial prompt with a valid repo.
    prompt1 = "I want to add a commenting feature to the RAG agent in the https://github.com/google/adk-samples repository.\n"
    process.stdin.write(prompt1)
    process.stdin.flush()

    response1 = ""
    while "goal" not in response1.lower():
        line = process.stdout.readline()
        if not line or "[user]:" in line:
            response1 += line
            break
        response1 += line
    
    assert "goal" in response1.lower()

    # Turn 2: User provides the goals.
    prompt2 = "The goal is to allow users to add comments to documents to facilitate collaboration.\n"
    process.stdin.write(prompt2)
    process.stdin.flush()

    response2 = ""
    while "solution" not in response2.lower() and "design" not in response2.lower():
        line = process.stdout.readline()
        if not line or "[user]:" in line:
            response2 += line
            break
        response2 += line

    # Now the agent should ask about the solution.
    assert "solution" in response2.lower() or "design" in response2.lower()

    process.terminate()
