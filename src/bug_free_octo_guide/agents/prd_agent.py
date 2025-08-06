from google.adk.agents import Agent
from google.adk.models.base_llm import BaseLlm
from google.adk.tools.base_tool import BaseTool
from google.genai import types

class PrdAgent(Agent):
    def __init__(self, llm: BaseLlm, feature_description: str):
        super().__init__(llm=llm)
        self.feature_description = feature_description
        self.tools: list[BaseTool] = []

    def load_prompt(self) -> str:
        """
        Loads the prompt from the prdprompt.md file.
        """
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prdprompt.md")
        with open(prompt_path, "r") as f:
            prompt = f.read()
        return prompt.replace("[Engineer: Provide a concise name for the feature]", self.feature_description)
