import pytest
from app.scraper import scrape_eci_latest_updates
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_latest_election_updates_endpoint():
    response = client.post("/mcp/tools/get_latest_election_updates", json={"query": ""})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Even if it fails to scrape, it should return a list with an error dict or default message
    assert len(data) > 0

# A simple unit test for the scraper function itself
def test_scraper_returns_list():
    result = scrape_eci_latest_updates()
    assert isinstance(result, list)
    if len(result) > 0:
        assert isinstance(result[0], dict)
