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
from .agents.api_changes_agent import ApiChangesAgent
from .agents.goals_agent import GoalsAgent
from .agents.solution_proposal_agent import SolutionProposalAgent
from .tools.context_analysis_tool import analyze_repo

root_agent = LlmAgent(
    model=Gemini(),
    name="bug_free_octo_guide",
    instruction=(
        "You are a project manager orchestrating the creation of a PRD. You must guide the user through the following steps in order:\n"
        "1. **Analyze Repository**: Call the `analyze_repo` tool. If it fails, report the error and STOP. \n"
        "2. **Define Goals**: After a successful analysis, delegate to the `GoalsAgent`. \n"
        "3. **Propose Solution**: After the user provides the goals, delegate to the `SolutionProposalAgent`. \n"
        "4. **Define API Changes**: After the user provides input on the solution, delegate to the `ApiChangesAgent`. \n"
        "Do not proceed to the next step until the user has provided input for the current one."
    ),
    tools=[
        analyze_repo,
        AgentTool(agent=GoalsAgent(llm=Gemini())),
        AgentTool(agent=SolutionProposalAgent(llm=Gemini())),
        AgentTool(agent=ApiChangesAgent(llm=Gemini())),
    ],
)