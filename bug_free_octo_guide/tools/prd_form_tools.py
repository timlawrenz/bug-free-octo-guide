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

from typing import List

def define_goals(
    primary_objective: str,
    success_metric: str,
    non_goals: List[str]
) -> str:
    """
    Defines the Goals and Non-Goals section of the PRD.

    Args:
        primary_objective: A clear, concise statement of the main goal.
        success_metric: A measurable metric to determine success (e.g., "10% increase in user engagement").
        non_goals: A list of things that are explicitly out of scope for this iteration.
    """
    non_goals_formatted = "\n- ".join(non_goals)
    return f"""
## Goals
- **Objective:** {primary_objective}
- **Success Metric:** {success_metric}

## Non-Goals
- {non_goals_formatted}
"""