# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import time

def test_agent_end_to_end():
    """
    Tests the agent's end-to-end functionality by running it as a subprocess.
    """
    repo_url = "https://github.com/google/adk-samples"
    prompt = f"Please analyze the repository at {repo_url}\n"

    process = subprocess.Popen(
        ["poetry", "run", "adk", "run", "bug_free_octo_guide"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Provide the prompt to the agent
    try:
        stdout, stderr = process.communicate(input=prompt, timeout=30)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        assert False, f"Agent timed out. Stderr: {stderr}"

    # Check for errors
    assert "error" not in stderr.lower()
    assert "traceback" not in stderr.lower()

    # Check for the expected output in stdout
    assert "Summaries:" in stdout
    assert "Gemfile" in stdout
    assert "config/routes.rb" in stdout
    assert "File not found" in stdout # for conventions.md