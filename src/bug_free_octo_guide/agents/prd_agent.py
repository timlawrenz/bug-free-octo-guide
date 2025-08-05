from google.adk.agents import Agent
from google.adk.models import Model
import os

class PrdAgent(Agent):
    def __init__(self, llm: Model, feature_description: str):
        super().__init__(llm=llm)
        self._feature_description = feature_description

    def load_prompt(self) -> str:
        """
        Loads the prompt from the prdprompt.md file.
        """
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prdprompt.md")
        with open(prompt_path, "r") as f:
            prompt = f.read()
        return prompt.replace("[Engineer: Provide a concise name for the feature]", self._feature_description)
