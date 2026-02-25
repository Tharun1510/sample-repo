import os
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks  # type: ignore
from dotenv import load_dotenv  # type: ignore

from .github_client import GitHubClient  # type: ignore
from .ai_engine import AIEngine  # type: ignore

load_dotenv()

app = FastAPI(title="DULA: Dual-Layer LLM Code Review Bot")

# Load environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

if not GITHUB_TOKEN or not GEMINI_API_KEY:
    raise RuntimeError("Missing GITHUB_TOKEN or GEMINI_API_KEY environment variables.")

# Initialize clients
gh_client = GitHubClient(token=GITHUB_TOKEN)
ai_engine = AIEngine(api_key=GEMINI_API_KEY)

# In-memory store for Layer 1 prompts waiting for confirmation.
# Format: {(repo_full_name, pr_number): {"prompt": "...", "diff": "..."}}
pending_reviews = {}

def verify_signature(payload_body: bytes, secret_token: str, signature_header: str):
    """Verify that the webhook payload was sent from GitHub."""
    if not signature_header:
        raise HTTPException(status_code=403, detail="x-hub-signature-256 header is missing!")
    hash_object = hmac.new(secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
         raise HTTPException(status_code=403, detail="Request signatures didn't match!")

def process_review_request(repo_full_name: str, pr_number: int, user_instruction: str):
    """Background task for Layer 1 (Prompt Enhancement)"""
    # 1. Post a reaction/comment to indicate we're working
    gh_client.post_comment(
        repo_full_name, pr_number, 
        "⏳ **DULA Layer 1 Triggered:** Mapping repository semantics and extracting context. Please wait..."
    )
    
    # 2. Get the PR diff
    pr_diff = gh_client.get_pr_diff(repo_full_name, pr_number)
    
    # 3. Get repository context (up to 2 levels deep)
    repo_structure = gh_client.get_repo_structure(repo_full_name)
    
    # 4. Optional: Try to grab key dependency file for deeper context
    key_context = "No specific dependency files configured."
    if "package.json" in repo_structure:
         content = gh_client.get_file_content(repo_full_name, "package.json")
         if content: key_context = "package.json:\n" + content[:1000]
    elif "requirements.txt" in repo_structure:
         content = gh_client.get_file_content(repo_full_name, "requirements.txt")
         if content: key_context = "requirements.txt:\n" + content[:1000]

    # 5. Execute Layer 1: Context-Aware Enhancement
    enhanced_prompt = ai_engine.layer_1_enhance_prompt(
        basic_prompt=user_instruction,
        repo_structure=repo_structure,
        key_files_context=key_context,
        pr_diff=pr_diff
    )
    
    # 6. Store in-memory for confirmation
    pending_reviews[(repo_full_name, pr_number)] = {
        "prompt": enhanced_prompt,
        "diff": pr_diff
    }
    
    # 7. Post the enhanced prompt to the PR asking for confirmation
    message = f"""### 🤖 DULA Layer 1: Context Analysis Complete
I have mapped the repository. Based on the `{user_instruction}` instruction and the project structure, I have engineered the following comprehensive instruction set for the downstream Code Review LLM:

---
> {enhanced_prompt.replace('\n', '\n> ')}
---

**If this looks correct, please reply with:**
`/confirm`

*(If not, reply with `/review [new instructions]` to restart the process)*
"""
    gh_client.post_comment(repo_full_name, pr_number, message)


def process_confirmation(repo_full_name: str, pr_number: int):
    """Background task for Layer 2 (The Review Execution)"""
    state_key = (repo_full_name, pr_number)
    if state_key not in pending_reviews:
        gh_client.post_comment(repo_full_name, pr_number, "❌ **Error:** No pending review found for this PR. Reply with `/review <instruction>` first.")
        return
        
    # 1. Acknowledge execution
    gh_client.post_comment(repo_full_name, pr_number, "🚀 **DULA Layer 2 Executing:** Running deep analytical structural review against the PR...")
    
    review_data = pending_reviews[state_key]
    confirmed_prompt = review_data["prompt"]
    pr_diff = review_data["diff"]
    
    # 2. Execute Layer 2
    final_review = ai_engine.layer_2_generate_review(confirmed_prompt, pr_diff)
    
    # 3. Post Results
    header = "## 🧠 DULA Layer 2: Final Intelligent Code Review\n\n"
    gh_client.post_comment(repo_full_name, pr_number, header + final_review)
    
    # 4. Clean up memory
    pending_reviews.pop(state_key, None)


@app.post("/webhook")
@app.post("/webhook/")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    
    if WEBHOOK_SECRET and WEBHOOK_SECRET != "optional_secret_for_webhook_validation":
         signature = request.headers.get("x-hub-signature-256")
         if signature:
             verify_signature(body, WEBHOOK_SECRET, signature)
         
    payload = await request.json()
    action = payload.get("action")
    
    comment_body = None
    repo_full_name = None
    pr_number = None

    # Handle a new Pull Request being opened
    if action == "opened" and "pull_request" in payload:
        comment_body = payload["pull_request"].get("body", "")
        repo_full_name = payload["repository"]["full_name"]
        pr_number = payload["pull_request"]["number"]
        
    # Handle a new comment on an existing Pull Request
    elif action == "created" and "comment" in payload:
        if "pull_request" in payload.get("issue", {}):
            comment_body = payload["comment"].get("body", "")
            repo_full_name = payload["repository"]["full_name"]
            pr_number = payload["issue"]["number"]

    if comment_body and repo_full_name and pr_number:
        comment_body = comment_body.strip()
        # Check for triggers
        if comment_body.startswith("/review"):
            user_instruction = comment_body.replace("/review", "").strip()
            if not user_instruction:
                 user_instruction = "Perform a general code review."
            # Send to background task so webhook responds 200 immediately
            background_tasks.add_task(process_review_request, repo_full_name, pr_number, user_instruction)
            
        elif comment_body.startswith("/confirm"):
            background_tasks.add_task(process_confirmation, repo_full_name, pr_number)

    return {"status": "ok"}

@app.get("/")
def home():
    return {"message": "DULA Backend is Running!"}
