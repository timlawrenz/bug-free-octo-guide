import os
import uuid
import logging
import json
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from github import Github

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
github_repo_name = os.getenv("GITHUB_REPO")

if not github_token or not github_repo_name:
    log.error("FATAL: GITHUB_TOKEN or GITHUB_REPO not found in environment variables.")
    raise SystemExit("GITHUB_TOKEN and GITHUB_REPO must be set.")

# --- Data Models ---
class ChatRequest(BaseModel):
    text: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class TicketRequest(BaseModel):
    prd: str

class TicketResponse(BaseModel):
    message: str
    ticket_urls: list[str]


# --- In-Memory Session Store ---
sessions = {}
log.info("In-memory session store initialized.")

# --- FastAPI Application ---
app = FastAPI()
log.info("FastAPI application created.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
log.info("CORS middleware configured.")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handles a chat request, maintaining conversation history using a session ID.
    """
    log.info(f"Received chat request. Session ID: {request.session_id}, Message: '{request.text}'")
    session_id = request.session_id or str(uuid.uuid4())
    log.info(f"Using session_id: {session_id}")

    try:
        if session_id not in sessions:
            log.info(f"Creating new chat session for session_id: {session_id}")
            model = genai.GenerativeModel('models/gemini-2.5-pro')
            sessions[session_id] = model.start_chat(history=[])
            log.info(f"New chat session created for session_id: {session_id}")

        chat_session = sessions[session_id]

        log.info(f"Sending message to Gemini model for session_id: {session_id}...")
        response = await chat_session.send_message_async(request.text)
        log.info(f"Received response from Gemini model for session_id: {session_id}.")

        return ChatResponse(response=response.text, session_id=session_id)
    except Exception as e:
        log.error(f"An error occurred during chat processing for session_id {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred.")

@app.post("/create_tickets", response_model=TicketResponse)
async def create_tickets(request: TicketRequest):
    """
    Generates tickets from a PRD and creates them in a GitHub repository.
    """
    log.info("Received request to create tickets.")
    try:
        # 1. Generate tickets from PRD using the TicketingAgent prompt
        ticketing_model = genai.GenerativeModel('models/gemini-2.5-pro')
        with open("ticketprompt.md", "r") as f:
            prompt = f.read().replace("{{prd}}", request.prd)

        log.info("Generating tickets from PRD...")
        response = await ticketing_model.generate_content_async(prompt)
        tickets_json = response.text.strip().replace("```json", "").replace("```", "")
        tickets = json.loads(tickets_json)
        log.info(f"Generated {len(tickets)} tickets.")

        # 2. Create tickets in GitHub
        g = Github(github_token)
        repo = g.get_repo(github_repo_name)
        ticket_urls = []

        for ticket in tickets:
            log.info(f"Creating ticket: {ticket['title']}")
            created_issue = repo.create_issue(
                title=ticket['title'],
                body=ticket['description']
            )
            ticket_urls.append(created_issue.html_url)
            log.info(f"Successfully created ticket: {created_issue.html_url}")

        return TicketResponse(message="Successfully created tickets!", ticket_urls=ticket_urls)

    except Exception as e:
        log.error(f"An error occurred during ticket creation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during ticket creation.")


if __name__ == "__main__":
    log.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)