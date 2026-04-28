from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from .scraper import scrape_eci_latest_updates
import os
import uvicorn

app = FastAPI(title="Election Education MCP Server", description="Provides real-time election updates.")

# Simple implementation of an MCP-like endpoint structure
# In a full MCP implementation, this would adhere strictly to the Model Context Protocol JSON-RPC spec.
# Here we provide a REST endpoint that the Vertex Agent can call as a "Tool" or "Extension".

class ToolRequest(BaseModel):
    query: str = ""

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/mcp/tools/get_latest_election_updates")
def get_latest_election_updates(request: ToolRequest) -> List[Dict[str, Any]]:
    """
    MCP Tool endpoint to fetch the latest updates from the Election Commission.
    """
    updates = scrape_eci_latest_updates()
    return updates

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
