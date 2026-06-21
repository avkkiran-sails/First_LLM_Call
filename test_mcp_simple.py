#!/usr/bin/env python
"""Simple test client for MCP HTTP/SSE server"""

import asyncio
import json
import aiohttp

async def test_sse_endpoint():
    """Test if SSE endpoint is accessible"""
    print("Testing SSE endpoint...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://127.0.0.1:8000/sse", timeout=2) as resp:
                print(f"SSE Status: {resp.status}")
                print(f"Headers: {resp.headers}")
                async for line in resp.content:
                    print(f"Received: {line}")
        except Exception as e:
            print(f"SSE Error: {e}")

async def test_messages_endpoint():
    """Test if messages endpoint is accessible"""
    print("\nTesting messages endpoint...")
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search_perplexity_demo",
                "arguments": {"query": "test"}
            }
        }
        try:
            async with session.post("http://127.0.0.1:8000/messages/", json=payload, timeout=2) as resp:
                print(f"Messages Status: {resp.status}")
                print(f"Headers: {resp.headers}")
                text = await resp.text()
                print(f"Response: {text}")
        except Exception as e:
            print(f"Messages Error: {e}")

async def main():
    await test_sse_endpoint()
    await test_messages_endpoint()

if __name__ == "__main__":
    asyncio.run(main())
