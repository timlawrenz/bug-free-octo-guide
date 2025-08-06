from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
import os

class TicketingAgent(LlmAgent):
    _prd: str

    def __init__(self, llm: BaseLlm, prd: str):
        super().__init__(
            model=llm,
            name="ticketing_agent",
            instruction="You are a project manager. Your task is to break down the following Product Requirements Document (PRD) into a set of actionable tickets.",
            _prd=prd
        )

    def load_prompt(self) -> str:
        """
        Loads the prompt from the ticketprompt.md file.
        """
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "ticketprompt.md")
        with open(prompt_path, "r") as f:
            prompt = f.read()
        return prompt + "\n\n" + self._prd
