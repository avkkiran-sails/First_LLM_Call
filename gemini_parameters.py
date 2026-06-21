import os
from dotenv_demo import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Configure generation parameters
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a creative story opening.",
    config=GenerateContentConfig(
        max_output_tokens=100,      # Limit response length
        temperature=0.9,            # Higher = more creative
        top_p=0.95,                 # Nucleus sampling threshold
        top_k=40                    # Limit vocabulary sampling
    )
)

print(response.text)