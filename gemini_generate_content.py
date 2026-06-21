import os
from dotenv_demo import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Make your first LLM call!
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is Python? Explain in one sentence."
)

# Print the response
print(response.text)