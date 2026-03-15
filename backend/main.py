from fastapi import FastAPI, Request, HTTPException
from parser import CodeParser
from reviewer import CodeReviewer
from github_handler import GitHubHandler
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Create the web application
app = FastAPI(
    title="AI Code Reviewer",
    description="Automatically reviews your code using AI"
)

# Create instances of our classes
parser = CodeParser()
reviewer = CodeReviewer()
github = GitHubHandler()


@app.get("/")
async def home():
    """
    Home page - confirms server is running
    """
    return {
        "message": "AI Code Reviewer is running! 🤖",
        "status": "healthy"
    }


@app.post("/webhook/github")
async def github_webhook(request: Request):
    """
    Receives webhooks from GitHub
    Runs when someone opens or updates a PR
    """
    
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    
    # Verify request is from GitHub
    if not github.verify_webhook(payload, signature):
        print("❌ Invalid webhook signature!")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = json.loads(payload)
    
    # Only review when PR is opened or updated
    action = data.get("action")
    if action not in ["opened", "synchronize"]:
        print(f"⏭️ Skipping action: {action}")
        return {"status": "skipped", "reason": f"action was {action}"}
    
    # Get PR details
    repo_name = data["repository"]["full_name"]
    pr_number = data["pull_request"]["number"]
    
    print(f"\n🎯 New PR #{pr_number} in {repo_name}")
    
    # Get changed files
    files = github.get_pr_files(repo_name, pr_number)
    
    if not files:
        return {"status": "no reviewable files found"}
    
    # Review each file
    all_bugs = []
    all_vulnerabilities = []
    scores = []
    
    for file in files:
        language = parser.detect_language(file["filename"])
        
        if language == "Unknown":
            print(f"⏭️ Skipping {file['filename']} - unknown language")
            continue
        
        print(f"\n📝 Reviewing {file['filename']} ({language})")
        
        review = reviewer.full_review(file["content"], language)
        
        all_bugs.extend(review["bugs"]["bugs"])
        all_vulnerabilities.extend(review["security"]["vulnerabilities"])
        scores.append(review["overall_score"])
    
    if not scores:
        return {"status": "no supported files to review"}
    
    # Calculate overall score
    final_score = sum(scores) / len(scores)
    
    # Post results to GitHub
    final_result = {
        "overall_score": round(final_score, 1),
        "bugs": {"bugs": all_bugs},
        "security": {"vulnerabilities": all_vulnerabilities}
    }
    
    github.post_comment(repo_name, pr_number, final_result)
    
    return {
        "status": "review completed",
        "score": final_score,
        "bugs_found": len(all_bugs),
        "security_issues": len(all_vulnerabilities)
    }


@app.post("/test-review")
async def test_review(request: Request):
    """
    Test endpoint - test reviews without GitHub
    """
    body = await request.json()
    code = body.get("code", "")
    language = body.get("language", "Python")
    
    result = reviewer.full_review(code, language)
    return result