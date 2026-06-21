import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

# 1. Initialize the FastMCP server instance
mcp = FastMCP("GenBodha-AI-Server")

BASE_URL = "https://genbodha.ai/learn/ai-agent-engineer/lesson/ahm-c30-l2/read"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 2. Expose a Tool to scrape/read pages from genbodha.ai
@mcp.tool()
async def fetch_page_content(path: str = "") -> str:
    """
    Fetches and extracts clean text content from a specific path on genbodha.ai.
    
    :param path: The URL sub-path to fetch (e.g., 'about', 'services', or leave empty for homepage).
    """
    # Clean up the path input safely
    clean_path = path.lstrip("/")
    target_url = f"{BASE_URL}/{clean_path}"
    
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        try:
            response = await client.get(target_url)
            response.raise_for_status()
            
            # Parse the HTML to extract only relevant text (avoiding heavy markup)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove scripts, styles, and nav elements to keep the LLM context clean
            for element in soup(["script", "style", "nav", "footer"]):
                element.decompose()
                
            return soup.get_text(separator="\n", strip=True)
            
        except httpx.HTTPStatusError as e:
            return f"Error fetching page: HTTP {e.response.status_code} encountered."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

# 3. Expose a Resource (static/dynamic data the LLM can reference)
@mcp.resource("genbodha://info")
def get_server_info() -> str:
    """Provides base context about the GenBodha AI MCP connector."""
    return f"This MCP server connects directly to {BASE_URL} to pull real-time documentation and structure."

# 4. Standard entry point to run the server over stdio (used by Claude Desktop/Cursor)
if __name__ == "__main__":
    mcp.run(transport="stdio")