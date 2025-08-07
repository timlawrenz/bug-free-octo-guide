from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm


class PrdWriterAgent(LlmAgent):
    def __init__(self, llm: BaseLlm):
        super().__init__(
            model=llm,
            name="prd_writer_agent",
            instruction="You are a product manager. Your task is to write a detailed and comprehensive PRD for a new feature. The PRD should include user stories, technical specifications, and a timeline.",
        )
