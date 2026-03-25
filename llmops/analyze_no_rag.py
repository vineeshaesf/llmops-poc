import ollama

def extract_errors(logs):
    return "\n".join([line for line in logs.splitlines() if "error" in line.lower()])[:2000]

with open("build.log") as f:
    logs = f.read()

errors = extract_errors(logs)

prompt = f"""
You are a DevOps engineer.

Analyze the build failure logs and provide:
- Root cause
- Fix
- Confidence

Logs:
{errors}
"""

response = ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": prompt}],
    options={"temperature": 0.3}
)

print("===== NO RAG OUTPUT =====")
print(response["message"]["content"])
