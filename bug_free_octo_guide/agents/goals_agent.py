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
from google.adk.models.base_llm import BaseLlm


class GoalsAgent(LlmAgent):
    def __init__(self, llm: BaseLlm):
        super().__init__(
            model=llm,
            name="goals_agent",
            instruction="""You are a senior product manager. Your task is to help an engineer define the "Goals & Non-Goals" for a new feature.

            - **Your Goal:** Ask clarifying questions to collaboratively define and detail the primary objectives, success criteria, and scope boundaries.
            - **Context is Key:** Use any provided repository context to ask more specific and relevant questions. For example, if you see existing models or packs, ask how the new feature's goals relate to them.
            - **Be Specific:** Guide the user to provide clear, measurable goals (e.g., "Increase user engagement by 10%") and explicit non-goals (e.g., "This feature will not handle payment processing").
            - **One Step at a Time:** Start by asking for the primary goals of the feature.
            """,
        )