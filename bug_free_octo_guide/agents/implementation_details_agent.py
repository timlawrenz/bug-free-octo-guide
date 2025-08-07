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


class ImplementationDetailsAgent(LlmAgent):
    def __init__(self, llm: BaseLlm):
        super().__init__(
            model=llm,
            name="implementation_details_agent",
            instruction="You are a senior software engineer. Your task is to help a user define the code implementation details for a new feature. Discuss key classes, modules, algorithms, and patterns, paying close attention to the project's conventions.",
        )
