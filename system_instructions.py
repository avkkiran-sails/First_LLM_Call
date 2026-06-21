import os
from dotenv_demo import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Use system instruction to set behavior
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What's the capital of Andhra Pradesh?",
    config=GenerateContentConfig(
        system_instruction="You are a helpful assistant that always responds in exactly three bullet points.",
        max_output_tokens=200
    )
)

print(response.text)