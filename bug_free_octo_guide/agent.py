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

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools.agent_tool import AgentTool
from .agents.prd_writer_agent import PrdWriterAgent
from .tools.context_analysis_tool import analyze_repo

# The "root_agent" is the entry point to your agent.
#
# This agent is an "LlmAgent" that acts as a planner. It is responsible
# for breaking down a complex task into a series of smaller, more
# manageable steps. It then delegates these steps to other agents or tools.
root_agent = LlmAgent(
    model=Gemini(),
    name="bug_free_octo_guide",
    instruction=(
        "You are a project manager. Your goal is to create a PRD. "
        "First, analyze the provided repository to understand the project context. "
        "Then, use the `PrdWriterAgent` to create a PRD based on the user's request and the repository context."
    ),
    tools=[
        analyze_repo,
        AgentTool(agent=PrdWriterAgent(llm=Gemini())),
    ],
)