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
from .agents.db_schema_agent import DbSchemaAgent
from .agents.goals_agent import GoalsAgent
from .agents.implementation_details_agent import ImplementationDetailsAgent
from .agents.solution_proposal_agent import SolutionProposalAgent
from .agents.testing_strategy_agent import TestingStrategyAgent
from .tools.context_analysis_tool import analyze_repo

root_agent = LlmAgent(
    model=Gemini(),
    name="bug_free_octo_guide",
    instruction=(
        "You are a project manager orchestrating the creation of a PRD. "
        "Your process is as follows:\n"
        "1. ALWAYS analyze the user's repository to gather context using the `analyze_repo` tool. If the analysis fails, report the error and STOP."
        "2. After successful analysis, delegate to the `GoalsAgent` to define the feature's goals."
        "3. Once the goals are defined, delegate to the `SolutionProposalAgent` to help the user design a technical solution."
        "4. After the solution is proposed, delegate to the `ApiChangesAgent` to define any API changes."
        "5. After the API changes are defined, delegate to the `DbSchemaAgent` to define any database schema changes."
        "6. After the database schema changes are defined, delegate to the `ImplementationDetailsAgent` to define the code implementation details."
        "7. After the implementation details are defined, delegate to the `TestingStrategyAgent` to define the testing strategy."
    ),
    tools=[
        analyze_repo,
        AgentTool(agent=GoalsAgent(llm=Gemini())),
        AgentTool(agent=SolutionProposalAgent(llm=Gemini())),
        AgentTool(agent=ApiChangesAgent(llm=Gemini())),
        AgentTool(agent=DbSchemaAgent(llm=Gemini())),
        AgentTool(agent=ImplementationDetailsAgent(llm=Gemini())),
        AgentTool(agent=TestingStrategyAgent(llm=Gemini())),
    ],
)