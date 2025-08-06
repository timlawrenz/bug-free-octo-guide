import os
import uuid
import logging
import json
import tempfile
import shutil
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from github import Github
import subprocess

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

class PlanningStatusResponse(BaseModel):
    status: str
    response: str | None = None

class ChatRequest(BaseModel):
    text: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

class TicketRequest(BaseModel):
    prd: str
    repo: str

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

def get_repo_context(repo_url: str) -> str:
    """Clones a repo, reads key files, and returns a context string."""
    temp_dir = tempfile.mkdtemp()
    log.info(f"Cloning {repo_url} into {temp_dir}")
    try:
        # Clone the repo
        auth_repo_url = repo_url.replace("https://", f"https://{github_token}@")
        subprocess.run(["git", "clone", "--depth", "1", auth_repo_url, temp_dir], check=True)

        # Read key files
        context_parts = []
        files_to_read = {
            "Schema": os.path.join(temp_dir, "db", "schema.rb"),
            "Routes": os.path.join(temp_dir, "config", "routes.rb"),
            "Gemfile": os.path.join(temp_dir, "Gemfile"),
            "Conventions": os.path.join(temp_dir, "conventions.md"),
        }

        for name, path in files_to_read.items():
            if os.path.exists(path):
                with open(path, "r") as f:
                    content = f.read()
                    context_parts.append(f"--- {name} ---\n{content}\n")
        
        return "\n".join(context_parts)

    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)
        log.info(f"Cleaned up temporary directory: {temp_dir}")




@app.get("/repos")
async def get_repos():
    """
    Returns a list of repositories for the authenticated user.
    """
    log.info("Fetching repositories for the authenticated user.")
    try:
        g = Github(github_token)
        repos = [repo.full_name for repo in g.get_user().get_repos()]
        log.info(f"Found {len(repos)} repositories.")
        return repos
    except Exception as e:
        log.error(f"An error occurred while fetching repositories: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while fetching repositories.")



async def run_planning_session(session_id: str, repo_url: str, feature_description: str):
    """Runs the planning session in the background."""
    sessions[session_id] = {"status": "cloning", "chat_session": None}
    try:
        # 1. Get repository context
        repo_context = get_repo_context(repo_url)
        sessions[session_id]["status"] = "generating"

        # 2. Create the initial prompt
        with open("prdprompt.md", "r") as f:
            prompt_template = f.read()
        
        initial_prompt = (
            prompt_template
            .replace("{{context}}", repo_context)
            .replace("{{feature_description}}", feature_description)
        )

        # 3. Start the chat session
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        chat_session = model.start_chat(history=[
            {'role': 'user', 'parts': [initial_prompt]}
        ])
        
        # 4. Get the first message from the bot
        response = await chat_session.send_message_async("Continue.")
        
        sessions[session_id]["status"] = "ready"
        sessions[session_id]["chat_session"] = chat_session
        sessions[session_id]["response"] = response.text

    except Exception as e:
        log.error(f"An error occurred during planning session startup: {e}", exc_info=True)
        sessions[session_id]["status"] = "error"
        sessions[session_id]["response"] = str(e)


@app.post("/start_planning", response_model=StartPlanningResponse)
async def start_planning(request: StartPlanningRequest, background_tasks: BackgroundTasks):
    """
    Starts a new planning session by analyzing a repo and initiating a chat in the background.
    """
    log.info(f"Starting new planning session for repo: {request.repo_url}")
    session_id = str(uuid.uuid4())
    background_tasks.add_task(run_planning_session, session_id, request.repo_url, request.feature_description)
    return StartPlanningResponse(session_id=session_id)


@app.get("/planning_status/{session_id}", response_model=PlanningStatusResponse)
async def planning_status(session_id: str):
    """
    Checks the status of a planning session.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    status = sessions[session_id]["status"]
    response = sessions[session_id].get("response")

    return PlanningStatusResponse(status=status, response=response)



@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handles a chat request for an existing session.
    """
    log.info(f"Received chat request. Session ID: {request.session_id}, Message: '{request.text}'")
    session_id = request.session_id
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=400, detail="Invalid session ID.")

    if sessions[session_id]["status"] != "ready":
        raise HTTPException(status_code=400, detail="Session is not ready for chat.")

    try:
        chat_session = sessions[session_id]["chat_session"]
        response = await chat_session.send_message_async(request.text)
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
        # 1. Generate tickets from PRD
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
        repo = g.get_repo(request.repo)
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
