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
from .agents.implementation_details_agent import ImplementationDetailsAgent
from .agents.solution_proposal_agent import SolutionProposalAgent
from .agents.testing_strategy_agent import TestingStrategyAgent
from .tools.context_analysis_tool import analyze_repo
from .tools.prd_assembler_tool import assemble_prd
from .tools.prd_form_tools import define_goals

root_agent = LlmAgent(
    model=Gemini(),
    name="bug_free_octo_guide",
    instruction=(
        "You are a project manager orchestrating the creation of a PRD. "
        "Your process is as follows:\n"
        "1. ALWAYS analyze the user's repository to gather context using the `analyze_repo` tool. If the analysis fails, report the error and STOP.\n"
        "2. After successful analysis, your next step is to define the feature's goals. You must call the `define_goals` tool. To do this, you need to ask the user for the `primary_objective`, `success_metric`, and `non_goals`."
    ),
    tools=[
        analyze_repo,
        define_goals,
        AgentTool(agent=SolutionProposalAgent(llm=Gemini())),
        AgentTool(agent=ApiChangesAgent(llm=Gemini())),
        AgentTool(agent=DbSchemaAgent(llm=Gemini())),
        AgentTool(agent=ImplementationDetailsAgent(llm=Gemini())),
        AgentTool(agent=TestingStrategyAgent(llm=Gemini())),
        assemble_prd,
    ],
)
