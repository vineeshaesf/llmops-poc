import ollama
from retriever import retrieve_context

def extract_errors(logs):
    return "\n".join([line for line in logs.splitlines() if "error" in line.lower()])[:2000]

with open("build.log") as f:
    logs = f.read()

errors = extract_errors(logs)
context = retrieve_context(errors)

prompt = f"""
You are a senior DevOps engineer.

Use BOTH logs and context to analyze the issue.

Logs:
{errors}

Known Issues / Fixes:
{context}

Provide:
- Root cause
- Fix (step-by-step)
- Confidence
"""

response = ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": prompt}],
    options={"temperature": 0.2}
)

print("===== RAG OUTPUT =====")
print(response["message"]["content"])
