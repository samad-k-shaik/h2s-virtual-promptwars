import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Mock heavy modules
sys.modules["playwright"] = MagicMock()
sys.modules["playwright.sync_api"] = MagicMock()
sys.modules["app.scraper"] = MagicMock()
sys.modules["redis"] = MagicMock()

# Ensure imports work
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.main import chat, health_check

@pytest.mark.asyncio
async def test_health_check_direct():
    """Test health check function directly."""
    response = await health_check()
    assert response["status"] == "ok"

@pytest.mark.asyncio
async def test_chat_error_handling_direct():
    """Test chat function error handling directly."""
    with patch("google.cloud.discoveryengine_v1.SearchServiceClient") as mock_client:
        mock_client.side_effect = Exception("Vertex Error")
        from app.main import ChatRequest
        request = ChatRequest(message="test")
        response = await chat(request)
        assert "trouble accessing" in response["reply"]

@pytest.mark.asyncio
async def test_chat_success_direct():
    """Test chat function success path directly."""
    with patch("google.cloud.discoveryengine_v1.SearchServiceClient") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.answer.answer_text = "Eligibility is 18+."
        mock_instance.search.return_value = mock_response
        
        from app.main import ChatRequest
        request = ChatRequest(message="how to vote")
        response = await chat(request)
        assert "Eligibility" in response["reply"]
