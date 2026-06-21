import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Get the prompt from the user interactively
user_prompt = input("Enter your prompt for the LLM: ")

# Make your first LLM call!
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=user_prompt
)

# Print the response
print(response.text)