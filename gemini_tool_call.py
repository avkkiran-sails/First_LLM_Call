import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import google.genai as genai

load_dotenv()

# 1. Define Pydantic model for the tool parameters
class WeatherRequest(BaseModel):
    location: str = Field(description="The city and state, e.g. London, UK")
    unit: str = Field(default="celsius", description="Temperature unit: celsius or fahrenheit")

# 2. Define mock tool implementation
def get_weather(location: str, unit: str = "celsius") -> str:
    """Mock implementation of get_weather"""
    return f"The weather in {location} is 72°F (22°C) and cloudy"

# 3. Define the function tool using Pydantic schema
schema_dict = WeatherRequest.model_json_schema()

# Convert to genai schema format
parameters_schema = genai.types.Schema(
    type=genai.types.Type.OBJECT,
    properties={
        "location": genai.types.Schema(type=genai.types.Type.STRING),
        "unit": genai.types.Schema(type=genai.types.Type.STRING),
    },
    required=["location"],
)

weather_tool = genai.types.Tool(
    function_declarations=[
        genai.types.FunctionDeclaration(
            name="get_weather",
            description="Get the current weather in a given location",
            parameters=parameters_schema,
        )
    ]
)

# 4. Create client and call API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Is it raining in London, UK?",
    config=genai.types.GenerateContentConfig(tools=[weather_tool]),
)

# 5. Parse the function calls and execute them
if response.candidates:
    for part in response.candidates[0].content.parts:
        if part.function_call:
            print(f"Executing: {part.function_call.name}")
            print(f"Args: {part.function_call.args}")
            
            # Execute the tool
            if part.function_call.name == "get_weather":
                result = get_weather(**part.function_call.args)
                print(f"Tool response: {result}")
            
            print("---")
        elif hasattr(part, 'text') and part.text:
            print(f"Text: {part.text}")