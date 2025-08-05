import asyncio
import argparse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from google.adk.models.google_llm import Gemini
from bug_free_octo_guide.agents.prd_agent import PrdAgent
from bug_free_octo_guide.agents.ticketing_agent import TicketingAgent
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

app = FastAPI()

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # The default React dev server port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory services for the ADK
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
llm = Gemini(model="gemini-1.5-flash")

@app.post("/chat")
async def chat(request: Request):
    """
    Handles chat interactions with the PRD agent.
    """
    data = await request.json()
    message = data.get("message")
    session_id = data.get("session_id")

    if not session_id:
        session = await session_service.create_session(
            app_name="bug-free-octo-guide",
            user_id="user123"
        )
        session_id = session.id

    prd_agent = PrdAgent(llm=llm, feature_description=message)
    runner = Runner(
        agent=prd_agent,
        session_service=session_service,
        artifact_service=artifact_service,
        app_name="bug-free-octo-guide",
    )

    user_message = types.Content(role="user", parts=[types.Part(text=message)])

    response_content = ""
    async for event in runner.run_async(
        session_id=session_id,
        user_id="user123",
        new_message=user_message
    ):
        if event.content:
            response_content += event.content.parts[0].text

    return {"response": response_content, "session_id": session_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)