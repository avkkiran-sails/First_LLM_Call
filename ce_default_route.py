from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def default_route():
    """Root/default route — always reachable at the base URL."""
    return {"message": "Welcome to the API", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Fallback — must be defined after all specific routes
@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def fallback_route(path: str, request: Request):
    return JSONResponse(
        status_code=404,
        content={"error": "Route not found", "path": f"/{path}"},
    )