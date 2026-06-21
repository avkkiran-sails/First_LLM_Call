"""
MCP HTTP/SSE Client Example

This client demonstrates the proper MCP HTTP/SSE protocol flow:
1. GET /sse - Client connects and listens for Server-Sent Events (responses)
2. POST /messages/ - Client sends tool call requests
3. Responses are streamed back via SSE

Flow:
  Client (Browser/Tool)
    ├─ GET /sse ────────→ MCP Server ──→ Opens SSE stream for responses
    │                        ↓
    │                   Listens for /messages/ requests
    │
    └─ POST /messages/ ─→ MCP Server ──→ Processes request
                            ↓
                         Call Tool (search_perplexity_demo)
                            ↓
                         Call Java Backend (127.0.0.1:8080)
                            ↓
                         Get Response
                            ↓
                         Send via SSE ──→ Client receives response
"""

import asyncio
import json
import aiohttp
import sys

MCP_SERVER_URL = "http://127.0.0.1:8000"

async def call_mcp_tool(query: str) -> str:
    """
    Call MCP tool using HTTP/SSE protocol.
    
    Steps:
    1. Connect to GET /sse to open SSE stream
    2. Send POST /messages/ request with tool call
    3. Listen for response on SSE stream
    """
    
    print(f"\n{'='*70}")
    print(f"MCP Client: Calling search_perplexity_demo")
    print(f"Query: {query}")
    print(f"{'='*70}\n")
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Open SSE connection
        print("1. Opening SSE stream at GET /sse...")
        sse_url = f"{MCP_SERVER_URL}/sse"
        
        try:
            async with session.get(sse_url, timeout=None) as sse_response:
                # Step 2: Send tool request
                print("2. Sending tool request to POST /messages/...")
                
                # Prepare MCP protocol message
                mcp_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "search_perplexity_demo",
                        "arguments": {
                            "query": query
                        }
                    }
                }
                
                # Send request
                message_url = f"{MCP_SERVER_URL}/messages/"
                async with session.post(
                    message_url,
                    json=mcp_request,
                    headers={"Content-Type": "application/json"}
                ) as msg_response:
                    msg_result = await msg_response.json()
                    print(f"   Request accepted: {msg_response.status}")
                
                # Step 3: Listen for SSE response
                print("3. Listening for response on SSE stream...\n")
                print("Server Responses:")
                print("-" * 70)
                
                async for line in sse_response.content:
                    line = line.decode().strip()
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            print(json.dumps(data, indent=2))
                        except json.JSONDecodeError:
                            print(line)
                    elif line:
                        print(line)
                        
        except asyncio.TimeoutError:
            print("Timeout waiting for response")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

async def main():
    query = "what is mcp server in AI context"
    
    print("\nMCP HTTP/SSE Protocol Flow Diagram:")
    print("""
    ┌─────────────────────────────────────────────────────────────┐
    │                    MCP HTTP/SSE Flow                         │
    ├─────────────────────────────────────────────────────────────┤
    │                                                               │
    │  Client                         MCP Server (9000)             │
    │  ├──GET /sse─────────────────→ Opens SSE Stream             │
    │  │                             Waits for requests             │
    │  │                                                             │
    │  ├──POST /messages/──────────→ Receives tool call            │
    │  │  {                          search_perplexity_demo        │
    │  │    method: "tools/call"                                   │
    │  │    name: "search_perplexity_demo"                         │
    │  │    params: {query: "..."}                                 │
    │  │  }                                                         │
    │  │                             Calls tool ↓                  │
    │  │                             Tool calls Java (8080)        │
    │  │                             Receives response from Java   │
    │  │  ←──SSE Event──────────────Sends response via SSE        │
    │  │  {                          data: {...}                   │
    │  │    response: "..."                                        │
    │  │  }                                                         │
    │  │                                                             │
    └─────────────────────────────────────────────────────────────┘
    
    Protocol: HTTP/SSE
    - Request: POST /messages/ (JSON-RPC 2.0)
    - Response: GET /sse (Server-Sent Events stream)
    """)
    
    await call_mcp_tool(query)

if __name__ == "__main__":
    asyncio.run(main())
