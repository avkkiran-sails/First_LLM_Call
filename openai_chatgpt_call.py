import os
from openai import OpenAI
from dotenv_demo import load_dotenv

def main():
    # Load environment variables from .env file if it exists
    load_dotenv()

    # Load API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your environment or create a .env file with OPENAI_API_KEY=your_key_here.")

    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)

    # List available models
    try:
        models_response = client.models.list()
        available_models = [model.id for model in models_response.data if model.id.startswith("gpt")]
        available_models.sort()  # Sort for better display
    except Exception as e:
        print(f"Error fetching models: {e}")
        available_models = ["gpt-3.5-turbo"]  # Fallback

    print("Available GPT models:")
    for i, model in enumerate(available_models, 1):
        print(f"{i}. {model}")

    # Default model
    default_model = "gpt-3.5-turbo"
    if default_model not in available_models:
        default_model = available_models[0] if available_models else "gpt-3.5-turbo"

    # User selects model
    model_choice = input(f"Select a model (1-{len(available_models)}) or press Enter for default ({default_model}): ").strip()
    if model_choice.isdigit() and 1 <= int(model_choice) <= len(available_models):
        selected_model = available_models[int(model_choice) - 1]
    else:
        selected_model = default_model

    print(f"Selected model: {selected_model}")

    # Get user prompt
    user_prompt = input("Enter your prompt: ").strip()
    if not user_prompt:
        user_prompt = "Hello, how are you?"

    # Example chat completion call
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=150,
            temperature=0.8,  # Controls randomness (0-2)
            top_p=0.9  # Nucleus sampling (0-1). Note: OpenAI doesn't support top_k directly.
        )

        # Print the response
        print("AI Response:")
        print(response.choices[0].message.content)

        # Print token usage
        print("\nToken Usage:")
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Completion tokens: {response.usage.completion_tokens}")
        print(f"Total tokens: {response.usage.total_tokens}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()