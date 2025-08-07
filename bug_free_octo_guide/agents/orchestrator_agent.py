from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.tools.agent_tool import AgentTool


class OrchestratorAgent(LlmAgent):
    def __init__(
        self,
        llm: BaseLlm,
        agents: list[LlmAgent],
    ):
        super().__init__(
            model=llm,
            name="orchestrator_agent",
            instruction="You are the orchestrator. You manage the PRD and ticketing process.",
            tools=[AgentTool(agent=agent) for agent in agents],
        )
