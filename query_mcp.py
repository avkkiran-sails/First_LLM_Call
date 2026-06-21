#!/usr/bin/env python
"""MCP HTTP/SSE Client with proper session management"""

import asyncio
import json
import aiohttp
import re

MCP_SERVER_URL = "http://127.0.0.1:8000"

async def query_mcp_server(query: str) -> str:
    """Query MCP server by keeping SSE connection open"""
    
    print(f"\n{'='*70}")
    print(f"Querying: {query}")
    print(f"{'='*70}\n")
    
    async with aiohttp.ClientSession() as session:
        # Start SSE connection and keep it open
        print("1. Opening persistent SSE connection...")
        
        async with session.get(f"{MCP_SERVER_URL}/sse", timeout=None) as sse_resp:
            # Get session_id from first SSE message
            session_id = None
            async for line in sse_resp.content:
                line_str = line.decode().strip()
                if "session_id=" in line_str:
                    match = re.search(r'session_id=([a-f0-9]+)', line_str)
                    if match:
                        session_id = match.group(1)
                        print(f"   ✓ Session ID obtained: {session_id}\n")
                        break
            
            if not session_id:
                print("   ✗ Failed to get session_id")
                return ""
            
            # Now send the tool request while keeping SSE open
            print("2. Sending tool call request...")
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "search_perplexity_demo",
                    "arguments": {"query": query}
                }
            }
            
            messages_url = f"{MCP_SERVER_URL}/messages/?session_id={session_id}"
            
            try:
                async with session.post(
                    messages_url,
                    json=mcp_request,
                    headers={"Content-Type": "application/json"},
                    timeout=3
                ) as msg_resp:
                    if msg_resp.status in (200, 202):  # 200 OK or 202 Accepted
                        print(f"   ✓ Request sent successfully (Status {msg_resp.status})\n")
                    else:
                        error_text = await msg_resp.text()
                        print(f"   ✗ Error {msg_resp.status}: {error_text}")
                        return ""
            except Exception as e:
                print(f"   ✗ Error sending request: {e}")
                return ""
            
            # Continue listening on the same SSE connection for response
            print("3. Listening for response on SSE stream...\n")
            print("Server Response:")
            print("-" * 70)
            
            response_text = ""
            try:
                async for line in sse_resp.content:
                    line_str = line.decode().strip()
                    if line_str.startswith("data: "):
                        try:
                            data = json.loads(line_str[6:])
                            if data.get("id") == 1:  # Our request
                                if "result" in data:
                                    result_content = data["result"].get("content", [])
                                    if result_content:
                                        response_text = result_content[0].get("text", "No response")
                                        print(response_text)
                                        break
                                elif "error" in data:
                                    print(f"Error: {data['error']}")
                                    break
                        except json.JSONDecodeError:
                            pass
            except asyncio.TimeoutError:
                print("Timeout waiting for response")
            except Exception as e:
                print(f"Error: {e}")
            
            print("-" * 70)
            return response_text

async def main():
    query = "what is Model Context Protocol server in AI context"
    result = await query_mcp_server(query)
    
    if result:
        print(f"\n{'='*70}")
        print("RESULT RECEIVED:")
        print(f"{'='*70}")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
