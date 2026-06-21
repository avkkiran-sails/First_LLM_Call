import os
from dotenv_demo import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain the theory of relativity in simple terms."
)

# Access usage metadata
usage = response.usage_metadata

print("Token Usage Breakdown:")
print(f"Prompt tokens: {usage.prompt_token_count}")
print(f"Response (candidates) tokens: {usage.candidates_token_count}")
print(f"Total tokens: {usage.total_token_count}")

# Check for optional token types
if hasattr(usage, 'cache_creation_input_token_count'):
    print(f"Cache creation tokens: {usage.cache_creation_input_token_count}")
if hasattr(usage, 'cached_content_input_token_count'):
    print(f"Cache read tokens: {usage.cached_content_input_token_count}")

# Calculate breakdown
accounted = usage.prompt_token_count + usage.candidates_token_count
other_tokens = usage.total_token_count - accounted
if other_tokens > 0:
    print(f"\nOther tokens (cache/system/etc): {other_tokens}")
else:
    print(f"\nAll tokens accounted for: {accounted} (matches total)")
