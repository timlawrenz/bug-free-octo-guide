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
from .agents.goals_agent import GoalsAgent
from .agents.solution_proposal_agent import SolutionProposalAgent
from .tools.context_analysis_tool import analyze_repo

root_agent = LlmAgent(
    model=Gemini(),
    name="bug_free_octo_guide",
    instruction=(
        "You are a project manager orchestrating the creation of a PRD. "
        "Your first step is to ALWAYS analyze the user's repository to gather context. "
        "If the user does not provide a repository URL, you MUST ask for one. "
        "When you call the `analyze_repo` tool, you MUST check the 'success' flag in the result. "
        "If the analysis is not successful, you MUST report the error to the user and STOP. "
        "If the analysis is successful, and only then, you may proceed by delegating the conversation to the `GoalsAgent`."
    ),
    tools=[
        analyze_repo,
        AgentTool(agent=GoalsAgent(llm=Gemini())),
        AgentTool(agent=SolutionProposalAgent(llm=Gemini())),
    ],
)
