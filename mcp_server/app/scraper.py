from playwright.sync_api import sync_playwright
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_eci_latest_updates():
    """
    Scrapes the latest updates from the Election Commission of India website using Playwright.
    This bypasses basic bot detection (403 errors) that simple requests often face.
    """
    url = "https://eci.gov.in/"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            logger.info(f"Navigating to {url}...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Get the content after JavaScript execution
            content = page.content()
            browser.close()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            updates = []
            # Looking for links that look like news or updates
            # Often ECI site has a 'what's new' section
            links = soup.find_all('a', href=True)
            
            for link in links:
                text = link.get_text(strip=True)
                href = link['href']
                
                # Heuristic to find relevant updates
                if len(text) > 25 and ("/whats-new/" in href or "/notifications/" in href or "update" in text.lower()):
                    updates.append({
                        "title": text,
                        "link": href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
                    })
                    if len(updates) >= 5:
                        break
            
            # If no specific updates found, just take some prominent links
            if not updates:
                for link in links[:50]:
                    text = link.get_text(strip=True)
                    if len(text) > 30:
                        updates.append({
                            "title": text,
                            "link": link['href'] if link['href'].startswith('http') else url.rstrip('/') + '/' + link['href'].lstrip('/')
                        })
                        if len(updates) >= 5:
                            break
                            
            if not updates:
                return [{"title": "Fetched successfully but no specific updates identified.", "link": url}]
                
            return updates

    except Exception as e:
        logger.error(f"Error scraping ECI site with Playwright: {e}")
        return [{"error": f"Failed to fetch updates via browser: {str(e)}"}]
