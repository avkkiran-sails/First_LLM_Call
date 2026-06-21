import logging
import json
import urllib.request
import urllib.error
from mcp.server.fastmcp import FastMCP

# Create FastMCP server with HTTP/SSE transport support.
# The server exposes:
#   GET  /sse      - SSE connection endpoint
#   POST /messages/ - HTTP message endpoint
server = FastMCP(
    name="Perplexity Demo Server",
    host="127.0.0.1",
    port=8001,
    mount_path="/",
    sse_path="/sse/test-2",
    message_path="/message",
    log_level="INFO",
)

logger = logging.getLogger("perplexity-demo")

# Java backend service configuration
JAVA_API_URL = "http://127.0.0.1:8080"

def call_java_backend(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Make HTTP request to Java backend service."""
    try:
        url = f"{JAVA_API_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if data:
            body = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
        else:
            req = urllib.request.Request(url, headers=headers, method=method)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='ignore')
        logger.error(f"HTTP Error {e.code}: {error_body}")
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        logger.error(f"Error calling Java backend: {e}")
        return {"error": str(e)}

@server.tool()
def search_perplexity_demo(query: str) -> str:
    """Search the demo application by forwarding to Java backend service."""
    logger.info("Forwarding search request to Java backend: query=%s", query)
    
    response = call_java_backend(
        "/search",
        method="POST",
        data={"prompt": query}
    )
    
    if "error" in response:
        return f"Error: {response['error']}"
    
    return json.dumps(response, indent=2)

@server.tool()
def get_detailed_source(source_id: str) -> str:
    """Retrieve detailed source content from Java backend service."""
    logger.info("Fetching source details from Java backend: source_id=%s", source_id)
    
    response = call_java_backend(f"/source/{source_id}", method="GET")
    
    if "error" in response:
        return f"Error: {response['error']}"
    
    return json.dumps(response, indent=2)

if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting MCP server with HTTP/SSE transport on http://%s:%s", server.settings.host, server.settings.port)
    
    # Get the ASGI app for SSE transport
    app = server.sse_app()
    
    # Run with Uvicorn
    uvicorn.run(
        app,
        host=server.settings.host,
        port=server.settings.port,
        log_level="info"
    )
