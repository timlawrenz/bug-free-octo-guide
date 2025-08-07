from .agents.orchestrator_agent import OrchestratorAgent
from .agents.prd_sub_agents import (
    ClarificationAgent,
    UserStoryAgent,
    TechSpecAgent,
    PrdDraftAgent,
)
from google.adk.models.google_llm import Gemini

llm = Gemini(model="gemini-1.5-flash")
clarification_agent = ClarificationAgent(llm=llm)
user_story_agent = UserStoryAgent(llm=llm)
tech_spec_agent = TechSpecAgent(llm=llm)
prd_draft_agent = PrdDraftAgent(llm=llm)

root_agent = OrchestratorAgent(
    llm=llm,
    agents=[
        clarification_agent,
        user_story_agent,
        tech_spec_agent,
        prd_draft_agent,
    ],
)
