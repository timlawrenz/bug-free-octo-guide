import subprocess
import pytest

def test_agent_fails_with_invalid_repo():
    """
    Tests that the agent stops and reports an error if the repo
    analysis fails.
    """
    process = subprocess.Popen(
        ["poetry", "run", "adk", "run", "bug_free_octo_guide"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line-buffered
    )

    # Provide a prompt with a fake repo URL.
    prompt = "Please analyze the repository at https://github.com/invalid/invalid.\n"

    process.stdin.write(prompt)
    process.stdin.flush()

    response = ""
    while not response or "[user]:" not in response:
        line = process.stdout.readline()
        if not line:
            break
        response += line

    # The agent should report the failure and stop.
    assert "error" in response.lower()
    assert "goal" not in response.lower() # Should not proceed to the next step.

    process.terminate()

def test_agent_succeeds_with_valid_repo():
    """
    Tests that the agent analyzes the repo and then asks a context-aware
    question about the feature's goals.
    """
    process = subprocess.Popen(
        ["poetry", "run", "adk", "run", "bug_free_octo_guide"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line-buffered
    )

    # Provide a prompt with a valid repo URL and a feature request.
    prompt = "I want to add a commenting feature to the RAG agent in the https://github.com/google/adk-samples repository.\n"
    process.stdin.write(prompt)
    process.stdin.flush()

    response = ""
    while not response or "[user]:" not in response:
        line = process.stdout.readline()
        if not line:
            break
        response += line

    # The agent should ask a question about goals that references the repo's context.
    assert "no relevant files" in response.lower()
    assert "goal" not in response.lower()

    process.terminate()