import os
from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
import os

class PrdAgent(LlmAgent):
    feature_description: str

    def __init__(self, llm: BaseLlm, feature_description: str):
        super().__init__(
            model=llm,
            name="prd_agent",
            instruction="You are a product manager. Your task is to write a Product Requirements Document (PRD) based on the provided feature description.",
            feature_description=feature_description
        )

    def load_prompt(self) -> str:
        """
        Loads the prompt from the prdprompt.md file.
        """
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prdprompt.md")
        with open(prompt_path, "r") as f:
            prompt = f.read()
        return prompt.replace("[Engineer: Provide a concise name for the feature]", self.feature_description)
