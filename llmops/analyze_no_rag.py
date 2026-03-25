import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

print("===== NO RAG OUTPUT =====")
print(response.choices[0].message.content)
