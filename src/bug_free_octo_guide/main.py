import os
import uuid
import logging
from dotenv import load_dotenv
from google.adk.models.google_llm import Gemini
import google.generativeai as genai
from .agents.prd_agent import PrdAgent
from .agents.ticketing_agent import TicketingAgent
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='server.log',
    filemode='w'
)
log = logging.getLogger(__name__)

# --- Configuration ---
log.info("Loading environment variables from .env file...")
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    log.info("GEMINI_API_KEY found.")
    genai.configure(api_key=api_key)
else:
    log.error("FATAL: GEMINI_API_KEY not found in environment variables.")
    raise SystemExit("GEMINI_API_KEY is not set.")

github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    log.error("FATAL: GITHUB_TOKEN not found in environment variables.")
    raise SystemExit("GITHUB_TOKEN must be set.")

# --- Data Models ---
class StartPlanningRequest(BaseModel):
    feature_description: str
    repo_url: str

class StartPlanningResponse(BaseModel):
    session_id: str

class ChatRequest(BaseModel):
    text: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

# --- In-memory services for the ADK ---
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
llm = Gemini(model="gemini-1.5-flash")
log.info("In-memory ADK services initialized.")

# --- FastAPI Application ---
app = FastAPI()
log.info("FastAPI application created.")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://184.72.72.233",
    "http://184.72.72.233:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
log.info("CORS middleware configured.")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handles chat interactions, including PRD generation and ticketing.
    """
    log.info(f"Received chat request. Session ID: {request.session_id}, Message: '{request.text}'")
    
    session_id = request.session_id
    message = request.text

    if not session_id:
        session = await session_service.create_session(
            app_name="bug-free-octo-guide",
            user_id="user123"
        )
        session_id = session.id
        log.info(f"New session created: {session_id}")

    # Simple "approval" check
    if "approve" in message.lower():
        log.info(f"PRD approved for session {session_id}. Starting ticketing.")
        # Retrieve the PRD from the artifact service
        artifact_keys = await artifact_service.list_artifact_keys(
            session_id=session_id,
            app_name="bug-free-octo-guide",
            user_id="user123"
        )
        prd_artifact_key = next((key for key in artifact_keys if "prd" in key.name), None)

        if not prd_artifact_key:
            log.error(f"PRD artifact not found for session {session_id}")
            return {"response": "PRD not found. Please generate a PRD first.", "session_id": session_id}

        prd_artifact = await artifact_service.load_artifact(session_id=session_id, name=prd_artifact_key.name)

        prd_content = prd_artifact.content.decode("utf-8")

        # Run the ticketing agent
        ticketing_agent = TicketingAgent(llm=llm, prd=prd_content)
        runner = Runner(
            agent=ticketing_agent,
            session_service=session_service,
            artifact_service=artifact_service,
            app_name="bug-free-octo-guide",
        )
        response_content = ""
        async for event in runner.run_async(session_id=session_id, user_id="user123", prd=prd_content):
            if event.content:
                response_content += event.content.parts[0].text
        
        log.info(f"Ticketing complete for session {session_id}.")
        return {"response": response_content, "session_id": session_id}

    # If not approving, run the PRD agent
    log.info(f"Running PRD agent for session {session_id}.")
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

    log.info(f"PRD generated and saved for session {session_id}.")

    return {"response": response_content, "session_id": session_id}


if __name__ == "__main__":
    log.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)