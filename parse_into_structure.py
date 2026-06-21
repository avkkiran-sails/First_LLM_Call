import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from google import genai

load_dotenv()

@dataclass
class LLMResponse:
    """Structured response from an LLM call."""
    text: str
    prompt_tokens: int
    response_tokens: int
    total_tokens: int
    model: str
    finish_reason: str

def parse_response(response, model_name: str) -> LLMResponse:
    """
    Parse a Gemini response into a structured LLMResponse.

    Args:
        response: The raw Gemini API response.
        model_name: The model that was called.

    Returns:
        A structured LLMResponse object.
    """
    usage = response.usage_metadata
    candidate = response.candidates[0]

    return LLMResponse(
        text=response.text,
        prompt_tokens=usage.prompt_token_count,
        response_tokens=usage.candidates_token_count,
        total_tokens=usage.total_token_count,
        model=model_name,
        finish_reason=str(candidate.finish_reason)
    )

# Usage
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
model = "gemini-2.5-flash"

raw_response = client.models.generate_content(
    model=model,
    contents="What is machine learning?"
)

parsed = parse_response(raw_response, model)
print(f"Response: {parsed.text}")
print(f"Tokens used: {parsed.total_tokens}")
print(f"Finish reason: {parsed.finish_reason}")