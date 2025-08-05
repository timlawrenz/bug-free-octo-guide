from google.adk.agents import Agent
from google.adk.models import Model
import os

class TicketingAgent(Agent):
    def __init__(self, llm: Model, prd: str):
        super().__init__(llm=llm)
        self._prd = prd

    def load_prompt(self) -> str:
        """
        Loads the prompt from the ticketprompt.md file.
        """
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "ticketprompt.md")
        with open(prompt_path, "r") as f:
            prompt = f.read()
        return prompt + "\n\n" + self._prd
