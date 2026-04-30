from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from .scraper import scrape_eci_latest_updates
import os
import uvicorn
import redis
import json
import logging

logger = logging.getLogger(__name__)

from fastapi.middleware.cors import CORSMiddleware

# Configuration from environment variables
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "h2s-virtual-promptwars")
LOCATION = os.environ.get("VERTEX_AI_LOCATION", "global")
DATA_STORE_ID = os.environ.get("VERTEX_AI_DATA_STORE_ID", "election-data-store")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "*") 

app = FastAPI(title="Election Education MCP Server", description="Provides real-time election updates.")

# Configure CORS - Restrict to specific frontend for Security criteria
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Redis configuration (Memorystore in GCP)
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
CACHE_EXPIRATION = 3600 # Cache for 1 hour

redis_client = None
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
except Exception as e:
    logger.warning(f"Failed to connect to Redis: {e}. Running without cache.")

class ToolRequest(BaseModel):
    query: str = ""

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/mcp/tools/get_latest_election_updates")
def get_latest_election_updates(request: ToolRequest) -> List[Dict[str, Any]]:
    """
    MCP Tool endpoint to fetch the latest updates from the Election Commission.
    Implements Memorystore (Redis) caching to reduce load on the source website.
    """
    cache_key = "eci_latest_updates"
    
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info("Returning cached updates.")
                return json.loads(cached_data)
        except redis.RedisError as e:
            logger.warning(f"Redis get error: {e}")

    logger.info("Cache miss. Scraping new updates.")
    updates = scrape_eci_latest_updates()
    
    if redis_client and updates and not "error" in updates[0]:
        try:
            redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(updates))
        except redis.RedisError as e:
            logger.warning(f"Redis set error: {e}")
            
    return updates

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Proxy endpoint to communicate with Vertex AI Agent Builder.
    Integrates live scraper data if keywords are detected.
    """
    try:
        from google.cloud import discoveryengine_v1 as discoveryengine
        
        client = discoveryengine.SearchServiceClient()
        
        serving_config = client.serving_config_path(
            project=PROJECT_ID,
            location=LOCATION,
            data_store=DATA_STORE_ID,
            serving_config="default_serving_config",
        )
        
        # Detect intent for live updates to trigger the scraper
        live_data_context = ""
        live_keywords = ["latest", "update", "current", "news", "live", "results", "today", "eci"]
        query_lower = request.message.lower()
        if any(keyword in query_lower for keyword in live_keywords):
            logger.info(f"Live update intent detected for query: {request.message}")
            try:
                updates = get_latest_election_updates(ToolRequest(query=request.message))
                if updates and isinstance(updates, list) and len(updates) > 0 and "error" not in updates[0]:
                    # Take top 3 updates for context
                    # Note: scraper returns 'title' and 'link'
                    live_data_context = " CURRENT LIVE UPDATES FROM ECI: " + " | ".join([f"{u.get('title', 'Update')}: {u.get('link', '')}" for u in updates[:3]])
                    logger.info("Successfully fetched live updates for context.")
            except Exception as se:
                logger.warning(f"Scraper failed during chat: {se}")

        # Construct preamble with live context if found
        preamble = "You are a friendly and professional Election Education Assistant for India. Your goal is to explain the electoral process simply and clearly. Use a warm, encouraging tone. Avoid using technical IDs or raw data in your response."
        if live_data_context:
            preamble += f" IMPORTANT: Use the following live updates in your answer to provide the most current information: {live_data_context}"

        search_request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=request.message,
            page_size=3,
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                    summary_result_count=3,
                    include_citations=False,
                    model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
                        preamble=preamble
                    ),
                    model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                        version="stable"
                    )
                )
            )
        )
        
        response = client.search(search_request)
        
        summary_text = response.summary.summary_text if response.summary else ""
        logger.info(f"Vertex Search raw summary: {summary_text[:100]}...")

        # Robust check for "No results" - Discovery Engine often returns variations of this string
        no_results_patterns = ["no results", "could not find", "don't have information", "sorry", "not found"]
        is_empty_response = not summary_text or any(pattern in summary_text.lower() for pattern in no_results_patterns)

        if not is_empty_response:
            return {"reply": summary_text}
        
        # Fallback if Vertex AI Search didn't find documents but we have live scraper data
        if live_data_context:
            logger.info("Vertex Search yielded no useful summary. Using live context fallback.")
            # Format the live updates into a friendly response
            formatted_updates = live_data_context.replace(" CURRENT LIVE UPDATES FROM ECI: ", "").replace(" | ", "\n\n")
            return {"reply": f"While I couldn't find a matching educational document right now, I have fetched the latest live updates directly from the Election Commission of India for you:\n\n{formatted_updates}"}
            
        return {"reply": "I couldn't find a specific answer in the election knowledge base. Could you try rephrasing your question about eligibility, registration, or polling procedures?"}

    except Exception as e:
        logger.error(f"Vertex AI Integration Error: {str(e)}")
        return {"reply": "I'm having trouble accessing my election knowledge right now. Please try again in a moment!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
