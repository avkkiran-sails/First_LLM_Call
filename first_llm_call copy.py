
import requests
import os
from dotenv_demo import load_dotenv

def call_gemini_api(prompt: str, api_key: str, model: str = "gemini-2.5-flash") -> str:
    """
    Calls the Gemini API with the given prompt and returns the response.
    
    Available models:
    - gemini-2.5-flash: Best price-performance for low-latency tasks
    - gemini-2.5-flash-lite: Fastest and most budget-friendly
    - gemini-2.5-pro: Most advanced for complex tasks
    - gemini-3-flash-preview: Latest generation (Preview)
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    params = {
        "key": api_key
    }
    response = requests.post(url, headers=headers, params=params, json=payload)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Response content: {response.text}")
        return "API call failed. See error above."
    data = response.json()
    # Extract the generated text from the response
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return str(data)


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return
    
    # Display available models
    print("\nAvailable Gemini Models:")
    print("1. gemini-2.5-flash (default) - Best price-performance")
    print("2. gemini-2.5-flash-lite - Fastest and most budget-friendly")
    print("3. gemini-2.5-pro - Most advanced for complex tasks")
    print("4. gemini-3-flash-preview - Latest generation (Preview)")
    
    model_choice = input("\nSelect model (1-4) or enter model name [default: 1]: ").strip()
    
    models = {
        "1": "gemini-2.5-flash",
        "2": "gemini-2.5-flash-lite",
        "3": "gemini-2.5-pro",
        "4": "gemini-3-flash-preview"
    }
    
    model = models.get(model_choice, model_choice) if model_choice else "gemini-2.5-flash"
    
    prompt = input("\nEnter your prompt: ")
    result = call_gemini_api(prompt, api_key, model)
    print("\nResponse from Gemini:")
    print(result)

if __name__ == "__main__":
    main()
