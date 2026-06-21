import os
from dotenv_demo import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is 2 + 2?"
)

# Access different parts of the response
print(f"Text: {response.text}")
print(f"Candidates: {len(response.candidates)}")

# Access the first candidate's content
candidate = response.candidates[0]
print(f"Finish reason: {candidate.finish_reason}")