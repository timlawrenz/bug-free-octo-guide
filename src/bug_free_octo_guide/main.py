import asyncio
import argparse
from google.adk.models.google_llm import Gemini
from bug_free_octo_guide.agents.prd_agent import PrdAgent
from bug_free_octo_guide.agents.ticketing_agent import TicketingAgent
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

class Orchestrator:
    def __init__(self, feature_idea: str):
        self._feature_idea = feature_idea
        self._llm = Gemini(model="gemini-1.5-flash")
        self._session_service = InMemorySessionService()
        self._artifact_service = InMemoryArtifactService()

    async def run_phase_1_prd(self):
        """
        Executes the first part of phase 1: generating a PRD.
        """
        print("--- Starting Phase 1: From Idea to PRD ---")

        # 1. Initialize the PRD Agent.
        prd_agent = PrdAgent(llm=self._llm, feature_description=self._feature_idea)

        # 2. Create a runner for the agent.
        runner = Runner(
            agent=prd_agent,
            session_service=self._session_service,
            artifact_service=self._artifact_service,
            app_name="bug-free-octo-guide",
        )

        # 3. Create a new session for the interaction.
        session = await self._session_service.create_session(
            app_name="bug-free-octo-guide",
            user_id="user123"
        )

        # 4. Run the agent.
        generated_prd = ""
        user_message = types.Content(role="user", parts=[types.Part(text="Start")])
        async for event in runner.run_async(
            session_id=session.id,
            user_id=session.user_id,
            new_message=user_message
        ):
            if event.is_final_response() and event.content:
                generated_prd = event.content.parts[0].text

        # 5. Save the generated PRD to a file.
        output_filename = "prd-output.md"
        with open(output_filename, "w") as f:
            f.write(generated_prd)

        print(f"✅ PRD generated and saved to {output_filename}")
        print("--- Phase 1 (PRD) Complete ---")
        return generated_prd

    async def run_phase_1_ticketing(self, prd: str):
        """
        Executes the second part of phase 1: generating tickets from a PRD.
        """
        print("--- Starting Phase 1: From PRD to Tickets ---")

        # 1. Initialize the Ticketing Agent.
        ticketing_agent = TicketingAgent(llm=self._llm, prd=prd)

        # 2. Create a runner for the agent.
        runner = Runner(
            agent=ticketing_agent,
            session_service=self._session_service,
            artifact_service=self._artifact_service,
            app_name="bug-free-octo-guide",
        )

        # 3. Create a new session for the interaction.
        session = await self._session_service.create_session(
            app_name="bug-free-octo-guide",
            user_id="user123"
        )

        # 4. Run the agent.
        generated_tickets = ""
        user_message = types.Content(role="user", parts=[types.Part(text="Start")])
        async for event in runner.run_async(
            session_id=session.id,
            user_id=session.user_id,
            new_message=user_message
        ):
            if event.is_final_response() and event.content:
                generated_tickets = event.content.parts[0].text

        # 5. Print the generated tickets.
        print("--- Generated Tickets ---")
        print(generated_tickets)
        print("--- Phase 1 (Ticketing) Complete ---")


async def main():
    """
    Main entry point for the orchestrator.
    """
    parser = argparse.ArgumentParser(description="bug-free-octo-guide orchestrator")
    parser.add_argument(
        "feature_idea",
        help="The high-level feature idea to be implemented.",
    )
    args = parser.parse_args()

    print("Orchestrator started.")
    orchestrator = Orchestrator(feature_idea=args.feature_idea)
    prd = await orchestrator.run_phase_1_prd()
    await orchestrator.run_phase_1_ticketing(prd)
    print("Orchestrator finished.")

if __name__ == "__main__":
    asyncio.run(main())
