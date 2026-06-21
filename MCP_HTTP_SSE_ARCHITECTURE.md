# MCP HTTP/SSE Architecture

## Overview
Your setup correctly implements the Model Context Protocol (MCP) with HTTP/SSE transport. Here's how it works:

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     System Architecture                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  MCP Clients                                                  │
│  (Browser, Tools, Apps)                                       │
│         │                                                     │
│         ├─ GET /sse              (Open SSE Stream)           │
│         │                                                     │
│         └─ POST /messages/       (Send Requests)             │
│                 │                                             │
│                 ▼                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │     MCP Server (FastMCP)                              │ │
│  │     127.0.0.1:9000                                    │ │
│  │                                                        │ │
│  │  ┌──────────────────────────────────────────────┐    │ │
│  │  │ Tools (Handlers)                            │    │ │
│  │  │ • search_perplexity_demo(query)             │    │ │
│  │  │ • get_detailed_source(source_id)            │    │ │
│  │  └────────────┬─────────────────────────────────┘    │ │
│  │               │                                       │ │
│  │               ▼                                       │ │
│  │  ┌──────────────────────────────────────────────┐    │ │
│  │  │ Java Backend Integration Layer               │    │ │
│  │  │ Calls 127.0.0.1:8080/search                 │    │ │
│  │  │ Calls 127.0.0.1:8080/source/{id}            │    │ │
│  │  └──────────────────────────────────────────────┘    │ │
│  └────────────────────────────────────────────────────────┘ │
│                 │                                            │
│                 ▼                                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │     Java Application                                  │ │
│  │     127.0.0.1:8080                                    │ │
│  │     • /search endpoint                                │ │
│  │     • /source/{id} endpoint                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Protocol Flow: HTTP/SSE

### Request-Response Cycle

**1. Client Opens SSE Connection**
```
GET /sse HTTP/1.1
Host: 127.0.0.1:9000
Accept: text/event-stream

↓
Server responds with SSE headers:
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
```

**2. Client Sends Tool Request**
```
POST /messages/ HTTP/1.1
Host: 127.0.0.1:9000
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_perplexity_demo",
    "arguments": {
      "query": "what is mcp server in AI context"
    }
  }
}
```

**3. Server Processes Request**
```
1. Receives POST /messages/ request
2. Identifies tool: search_perplexity_demo
3. Calls tool with arguments
4. Tool calls Java backend: POST /search {"prompt": "..."}
5. Receives response from Java
6. Sends response via SSE stream
```

**4. Client Receives Response via SSE**
```
data: {
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "In the context of AI, MCP server stands for..."
      }
    ]
  }
}
```

## Key Components

### MCP Server (server.py)
- **Location**: 127.0.0.1:9000
- **Protocol**: HTTP/SSE
- **Endpoints**:
  - `GET /sse` - Server-Sent Events stream for responses
  - `POST /messages/` - Receives MCP protocol requests
  
- **Tools**:
  - `search_perplexity_demo(query: str)` - Search queries
  - `get_detailed_source(source_id: str)` - Fetch source details

### Java Backend
- **Location**: 127.0.0.1:8080
- **Endpoints**:
  - `POST /search` - Process search queries
  - `GET /source/{id}` - Fetch source by ID

## Data Flow

```
User Query
   ▼
Client POST /messages/ {tool: "search_perplexity_demo", args: {query: "..."}}
   ▼
FastMCP Server receives request
   ▼
Executes search_perplexity_demo("...")
   ▼
Tool calls Java Backend
   POST /search {"prompt": "..."}
   ▼
Java Backend processes (LLM inference, etc.)
   ▼
Returns response: {"response": "In the context of AI..."}
   ▼
Tool formats response
   ▼
FastMCP sends response via SSE
   ▼
Client receives data event on /sse stream
   ▼
Client displays/processes result
```

## Running the System

### 1. Start Java Backend (8080)
```bash
# Your Java application
```

### 2. Start MCP Server (9000)
```bash
python server.py
```

### 3. Test with Client
```bash
python mcp_client_http_sse.py
```

Or use curl to test:
```bash
# Open SSE stream in one terminal
curl -N http://127.0.0.1:9000/sse

# Send request in another terminal
curl -X POST http://127.0.0.1:9000/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "search_perplexity_demo",
      "arguments": {"query": "what is mcp server"}
    }
  }'
```

## Why HTTP/SSE?

✅ **Advantages**:
- Browser-compatible (uses HTTP)
- Real-time streaming responses (SSE)
- Bi-directional communication (POST for requests, GET for responses)
- No WebSocket complexity
- Load balancer friendly
- Stateless (can scale horizontally)

## Summary

Your current implementation **correctly depicts the MCP HTTP/SSE functionality**:

1. ✅ Clients connect to `GET /sse` for responses
2. ✅ Clients send requests to `POST /messages/`
3. ✅ MCP server processes requests through tools
4. ✅ Tools call Java backend
5. ✅ Responses sent back via SSE stream

This is the standard MCP HTTP/SSE protocol flow used by tools like Claude Desktop, Cline, and other MCP clients.
