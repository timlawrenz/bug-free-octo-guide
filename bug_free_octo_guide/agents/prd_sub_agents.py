from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm


class ClarificationAgent(LlmAgent):
    def __init__(self, llm: BaseLlm):
        super().__init__(
            model=llm,
            name="clarification_agent",
            instruction="You are a product manager. Your task is to ask clarifying questions to better understand a feature request.",
        )


class UserStoryAgent(LlmAgent):
    def __init__(self, llm: BaseLlm):
        super().__init__(
            model=llm,
            name="user_story_agent",
            instruction="You are a product manager. Your task is to generate user stories based on a feature description.",
        )


class TechSpecAgent(LlmAgent):
    def __init__(self, llm: BaseLlm):
        super().__init__(
            model=llm,
            name="tech_spec_agent",
            instruction="You are a software engineer. Your task is to define technical specifications for a feature.",
        )


class PrdDraftAgent(LlmAgent):
    def __init__(self, llm: BaseLlm):
        super().__init__(
            model=llm,
            name="prd_draft_agent",
            instruction="You are a product manager. Your task is to draft a complete PRD using the provided information.",
        )
