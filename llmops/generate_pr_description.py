"""
PR Description Generator — LLMOps POC
--------------------------------------
Flow:
  1. Fetch the code diff from GitHub API (the PR's changed files)
  2. Send the diff to Ollama (free local LLM)
  3. AI generates a clear PR description
  4. Post the description back to the GitHub PR via API

Required environment variables (set in Azure Pipeline):
  - GITHUB_TOKEN      → GitHub Personal Access Token (needs repo + PR write access)
  - GITHUB_REPO       → e.g. "vineesha/my-repo"
  - PR_NUMBER         → automatically available in Azure Pipeline as $(System.PullRequest.PullRequestNumber)
"""

import os
import sys
import requests
import ollama

# ── Config ────────────────────────────────────────────────────────────────────
MODEL       = "llama3.2"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO  = os.getenv("GITHUB_REPO")        # e.g. "vineesha/my-repo"
PR_NUMBER    = os.getenv("PR_NUMBER")           # e.g. "42"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# ── Step 1: Fetch the diff from GitHub ───────────────────────────────────────
def get_pr_diff(repo: str, pr_number: str) -> str:
    """Fetch changed files and their patches from the GitHub PR."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    files = response.json()
    diff_text = ""

    for f in files:
        filename = f.get("filename", "")
        status   = f.get("status", "")        # added / modified / removed
        patch    = f.get("patch", "")          # actual line-by-line diff

        diff_text += f"\n--- File: {filename} ({status}) ---\n"
        diff_text += patch[:2000]              # cap per file to avoid huge prompts
        diff_text += "\n"

    return diff_text[:6000]                    # total cap — safe for llama3.2


# ── Step 2: Generate PR description using Ollama ─────────────────────────────
def generate_description(diff: str) -> str:
    """Send the diff to the local LLM and get a PR description back."""

    prompt = f"""You are a senior DevOps/software engineer reviewing a pull request.

Based on the following code diff, write a clear and professional pull request description.

Include these sections:
## Summary
(What does this PR do? 2-3 sentences max)

## Changes
(Bullet points of what was changed, added, or removed)

## Why
(Why was this change made?)

## Testing
(How can a reviewer test or verify this?)

Code Diff:
{diff}
"""

    print(f"[LLMOps] Sending diff to model: {MODEL}")
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.3},
    )

    return response["message"]["content"]


# ── Step 3: Post the description back to the GitHub PR ───────────────────────
def post_pr_description(repo: str, pr_number: str, description: str):
    """Update the GitHub PR body with the AI-generated description."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    payload = {"body": description}

    response = requests.patch(url, headers=HEADERS, json=payload)
    response.raise_for_status()

    print(f"[LLMOps] PR description posted successfully to PR #{pr_number}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # Validate env vars
    missing = [v for v in ["GITHUB_TOKEN", "GITHUB_REPO", "PR_NUMBER"]
               if not os.getenv(v)]
    if missing:
        print(f"[ERROR] Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    print(f"[LLMOps] Fetching diff for PR #{PR_NUMBER} from {GITHUB_REPO}")
    diff = get_pr_diff(GITHUB_REPO, PR_NUMBER)

    if not diff.strip():
        print("[INFO] No diff found — PR may have no file changes.")
        sys.exit(0)

    print(f"[LLMOps] Diff fetched ({len(diff)} chars). Generating description...")
    description = generate_description(diff)

    print("\n===== GENERATED PR DESCRIPTION =====")
    print(description)
    print("=====================================\n")

    print("[LLMOps] Posting description to GitHub PR...")
    post_pr_description(GITHUB_REPO, PR_NUMBER, description)

    print("[LLMOps] Done!")
