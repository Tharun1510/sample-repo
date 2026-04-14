# 🎬 DULA vs. Standard LLMs: The Video Demo Guide

This document contains everything you need to record your project defense video. It includes the exact code snippets to use, the prompts to feed into ChatGPT (to show it failing), and the expected DULA response (to show your project succeeding).

---

## 🛠️ Setup: Preparing your GitHub Repository

Before you hit "Record" on your screen capture software, you need to set up a dummy repository on GitHub.

1. **Create a new public repository** on GitHub called `dula-demo-repo`.
2. **Setup the Baseline Files**: 
   Create the following two files in the `main` branch to give DULA its "Context":

   📜 **File 1: `requirements.txt`**
   ```text
   fastapi==0.100.0
   SQLAlchemy==2.0.19
   pydantic==2.1.1
   ```
   *(This tells DULA the project uses an ORM, an important trap for Scenario 3).*

   📜 **File 2: `utils/security.py`**
   ```python
   import jwt
   from datetime import datetime, timedelta

   def validate_and_decode_token(token: str, secret_key: str):
       """Core project function to validate JWT tokens."""
       try:
           decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
           if decoded.get("exp") < datetime.utcnow().timestamp():
               return {"status": "error", "message": "Token expired"}
           if not decoded.get("is_admin"):
               return {"status": "error", "message": "Insufficient privileges"}
           return {"status": "success", "data": decoded}
       except jwt.PyJWTError:
           return {"status": "error", "message": "Invalid token"}
   ```

3. **Install the DULA Extension & Run Backend**: Make sure you have your extension loaded in Chrome and your `uvicorn` backend running locally with `ngrok`/`smee.io` tunneling webhook events to your backend.

---

# 🎥 The Recording Script

Now, start recording your screen. Follow these specific scenarios.

## Scenario 1: The "Spaghetti Code" Trap (Cyclomatic Complexity)

**The Objective:** Prove that standard LLMs don't mathematically penalize highly complex, bug-prone code, but your DULA deterministic algorithm does.

**Step 1:** Create a new branch `feature/order-processor` and create a file called `order_service.py`. Paste this terrible code:

```python
def process_customer_order(order_data, is_vip, stock_level, payment_status):
    # A monolithic, untested god-function
    if not order_data:
        return False
    else:
        if is_vip:
            if payment_status == "PAID":
                if stock_level > 0:
                    for item in order_data['items']:
                        if item['available']:
                            try:
                                # fake logic
                                print("Processing VIP")
                                if item['weight'] > 50:
                                    print("Heavy item processing")
                                else:
                                    print("Light item processing")
                            except Exception as e:
                                print(e)
                        else:
                            return "Item missing"
                else:
                    return "Out of stock"
            elif payment_status == "PENDING":
                return "Wait for payment"
        else:
            if payment_status == "PAID":
                for item in order_data['items']:
                    if stock_level > 0:
                        try:
                            print("Processing Normal")
                        except Exception as e:
                            print(e)
                    else:
                        break
            else:
                return "Unpaid normal user"
    return True
```

**Step 2 (The ChatGPT Failure):** 
Open ChatGPT on screen. Copy the code above and ask: *"Can you review this code?"*
*ChatGPT will likely say: "The code looks okay, but it has a lot of nesting. You might want to break it down. Here is a refactored version." It is polite and treats it as a stylistic issue.*

**Step 3 (The DULA Victory):**
Open your GitHub PR. Click the **"🧠 Request DULA Review"** button.
*Your backend's `algorithms.py` will hit this. The McCabe Cyclomatic Complexity will calculate a score well over 15. The prompt will output a **CRITCAL BUG RISK** alert directly into the PR, quoting the exact complexity score and demanding a refactor before merging.*

---

## Scenario 2: The "DRY Violation" Trap (Levenshtein Distance)

**The Objective:** Prove that standard LLMs only review files in isolation, whereas DULA maps the repo context and uses algorithms to catch duplicated code.

**Step 1:** Create a new branch `feature/admin-panel`. Create a file called `admin_dashboard_auth.py` and paste this code:

```python
import jwt
from datetime import datetime

# The developer was lazy and copied the exact logic from utils/security.py
def check_admin_dashboard_token(auth_token: str, server_secret: str):
    try:
        decoded_payload = jwt.decode(auth_token, server_secret, algorithms=["HS256"])
        if decoded_payload.get("exp") < datetime.utcnow().timestamp():
            return {"status": "error", "message": "Token expired"}
        if not decoded_payload.get("is_admin"):
            return {"status": "error", "message": "Insufficient privileges"}
        return {"status": "success", "data": decoded_payload}
    except jwt.PyJWTError:
        return {"status": "error", "message": "Invalid token"}
```

**Step 2 (The ChatGPT Failure):**
Paste that single file into ChatGPT and ask: *"Review this code for a Pull Request."*
*ChatGPT will say: "This is a great, secure JWT validation function! Looks good to go." It has NO IDEA this function already exists elsewhere in the project.*

**Step 3 (The DULA Victory):**
Go to GitHub and trigger DULA. 
*Your Levenshtein distance algorithm will cross-reference `admin_dashboard_auth.py` against `utils/security.py`. It will realize the similarity is > 90%. DULA will comment on the PR: **"DRY Violation Detected. This code is 94% similar to `utils/security.py`. Do not duplicate code. Import the existing function."***

---

## Scenario 3: The Context-Blind Vulnerability

**The Objective:** Prove that LLMs will allow insecure coding patterns if they don't ingest dependency files (`requirements.txt`) like DULA does with Holistic Context Parsing.

**Step 1:** Create a branch `feature/db-search`. Create `search.py`:

```python
import sqlite3

def search_users_unsafe(user_input_name: str):
    # DANGEROUS: Bypassing the project's SQLAlchemy ORM and doing string-concatenation SQL 
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    
    query = f"SELECT * FROM users WHERE username = '{user_input_name}'"
    
    cursor.execute(query)
    results = cursor.fetchall()
    connection.close()
    return results
```

**Step 2 (The ChatGPT Failure):**
Paste just this snippet to ChatGPT. 
*ChatGPT might flag the SQL injection (because it's obvious), but it will likely suggest fixing it by changing it to `cursor.execute("SELECT... ?", (user_input_name,))`. It still allows `sqlite3` driver usage.*

**Step 3 (The DULA Victory):**
Go to GitHub, trigger DULA.
*DULA Layer 1 parsed `requirements.txt` and saw `SQLAlchemy==2.0.19`. It knows this is an ORM environment. DULA's review will state: **"Architectural Violation & SQL Injection. You are bypassing the SQLAlchemy ORM framework defined in the project dependencies by using raw `sqlite3`. Use SQLAlchemy session models to execute this query."***

---

### End of Video Wrap-Up
In your video voiceover, you can conclude:
*"As demonstrated, while standard LLMs provide generic advice, the DULA architecture acts as a true Senior Staff Engineer. By leveraging deterministic algorithms for cyclomatic complexity and Levenshtein string similarity, combined with holistic repository tree parsing, DULA achieves mathematical certainty and context-awareness that standard generative models simply cannot match."*
