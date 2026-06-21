import os
from dotenv_demo import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Different models for different use cases

# Fast and efficient for most tasks
response_flash = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain recursion briefly."
)
print(f"Flash: {response_flash.text}")

# More capable for complex reasoning (when available)
response_pro = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Explain recursion briefly."
)
print(f"Pro: {response_pro.text}")