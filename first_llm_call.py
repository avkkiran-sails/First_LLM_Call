import os
import google.generativeai as genai
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
    try:
        genai.configure(api_key=api_key)
        model_obj = genai.GenerativeModel(model)
        response = model_obj.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error occurred: {e}")
        return "API call failed. See error above."


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
