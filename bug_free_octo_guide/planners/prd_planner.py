from google.generativeai import protos


import json
from google.adk.planners import BasePlanner
from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.generativeai import protos


class PrdPlanner(BasePlanner):
    """
    A planner for generating a Product Requirements Document (PRD).
    """

    def build_planning_instruction(
        self, readonly_context: dict, llm_request: protos.Content
    ) -> str | None:
        """Builds the system instruction for the LLM to generate a plan."""
        feature_description = readonly_context.get("session", {}).get("state", {}).get("feature_description")
        if not feature_description:
            # Fallback to the user message if not in state
            if llm_request.parts:
                feature_description = llm_request.parts[0].text
        
        if not feature_description:
            raise ValueError("feature_description not found in session state or llm_request")

        return f"""
        Create a plan to generate a Product Requirements Document (PRD) for the following feature: '{feature_description}'.
        The plan should be a JSON array of steps, where each step has an 'agent' and an 'instruction'.
        The available agents are: 'clarification_agent', 'user_story_agent', 'tech_spec_agent', 'prd_draft_agent'.

        Example plan:
        [
            {{
                "agent": "clarification_agent",
                "instruction": "Ask clarifying questions about the feature."
            }},
            {{
                "agent": "user_story_agent",
                "instruction": "Generate user stories based on the clarified requirements."
            }}
        ]
        """

    def process_planning_response(
        self, callback_context: dict, response_parts: list[protos.Part]
    ) -> list[dict] | None:
        """Processes the LLM's response to extract the plan."""
        if not response_parts:
            return None
        
        try:
            # Assuming the response is a JSON string in the first part
            plan_json = response_parts[0].text
            plan = json.loads(plan_json)
            return plan
        except (json.JSONDecodeError, IndexError) as e:
            # Handle cases where the response is not valid JSON
            # You might want to add more robust error handling or a retry mechanism
            print(f"Error processing planning response: {e}")
            return None
