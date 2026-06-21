import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import OpenAI

load_dotenv()

# 1. Define the parameters using Pydantic
class WeatherRequest(BaseModel):
    location: str = Field(description="The city and state, e.g. San Francisco, CA")
    unit: str = Field(default="celsius", pattern="^(celsius|fahrenheit)$")

class StockPriceRequest(BaseModel):
    symbol: str = Field(description="Stock ticker symbol, e.g. AAPL, GOOGL, MSFT")
    currency: str = Field(default="USD", description="Currency code for the price")

# 2. Helper function to convert Pydantic model to OpenAI tool format
def create_tool(name: str, description: str, model: type[BaseModel]) -> dict:
    """Convert a Pydantic model to OpenAI tool format"""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": model.model_json_schema()
        }
    }

# 3. Create tools from Pydantic models
openai_tool = create_tool(
    "get_weather",
    "Get the current weather in a given location",
    WeatherRequest
)

stock_price_tool = create_tool(
    "get_stock_price",
    "Get the current stock price for a given ticker symbol",
    StockPriceRequest
)

# 4. Define tool implementations
def get_weather(location: str, unit: str = "celsius") -> str:
    """Mock implementation of get_weather"""
    return f"The weather in {location} is 72°F (22°C) and sunny"

def get_stock_price(symbol: str, currency: str = "USD") -> str:
    """Mock implementation of get_stock_price"""
    return f"The stock price of {symbol} is $150.25 {currency}"

# 5. Call the API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in NYC and the stock price of AAPL?"}],
    tools=[openai_tool, stock_price_tool] # Registering the tools
)

# 6. Access and execute tool calls
for tool_call in response.choices[0].message.tool_calls:
    print(f"LLM wants to call: {tool_call.function.name}")
    print(f"With arguments: {tool_call.function.arguments}")
    
    # Parse the arguments
    args = json.loads(tool_call.function.arguments)
    
    # Execute the appropriate tool
    if tool_call.function.name == "get_weather":
        result = get_weather(**args)
    elif tool_call.function.name == "get_stock_price":
        result = get_stock_price(**args)
    else:
        result = "Unknown tool"
    
    print(f"Tool response: {result}")
    print("---")
    print("---")