import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_eci_latest_updates():
    """
    Scrapes the latest updates from the Election Commission of India website.
    This is a simplified example that fetches titles from a hypothetical news section.
    In a real scenario, this would target specific elements on the ECI site.
    """
    # Note: ECI website structure changes frequently and scraping might be blocked.
    # This is a representative example for the challenge.
    url = "https://eci.gov.in/"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Hypothetical: finding news items in a list or div with class 'news-item' or similar
        # ECI site uses various structures. We will simulate finding some generic links for the demo
        # Let's try to extract text from a few prominent links as "updates"
        
        updates = []
        # Fallback simplistic extraction for demonstration purposes:
        links = soup.find_all('a', href=True, limit=20) 
        
        for link in links:
            text = link.get_text(strip=True)
            if len(text) > 20: # Arbitrary length to filter out small navigation links
                 updates.append({
                     "title": text,
                     "link": link['href'] if link['href'].startswith('http') else url + link['href'].lstrip('/')
                 })
                 if len(updates) >= 5: # Limit to top 5 updates
                     break
                     
        if not updates:
             return [{"title": "No latest updates found or site structure changed.", "link": url}]
             
        return updates

    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping ECI site: {e}")
        return [{"error": f"Failed to fetch updates: {str(e)}"}]
