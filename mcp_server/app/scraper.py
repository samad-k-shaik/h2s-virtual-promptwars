import asyncio
from playwright.async_api import async_playwright
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scrape_eci_latest_updates():
    """
    Scrapes the latest updates from the ECI Unified Portal using Async Playwright.
    This portal is more robust and less likely to block GCP IP ranges.
    """
    url = "https://ecinet.eci.gov.in/home/eciUpdates"
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            try:
                # Use a larger viewport and a modern UA
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 800}
                )
                page = await context.new_page()
                
                logger.info(f"Navigating to {url}...")
                try:
                    # Extended timeout to 120s for the slow portal
                    # Using 'load' instead of 'domcontentloaded' to ensure components are ready
                    await page.goto(url, wait_until="load", timeout=120000)
                    # Wait for network activity to settle
                    try:
                        await page.wait_for_load_state("networkidle", timeout=15000)
                    except:
                        logger.warning("Network did not go idle, proceeding anyway")
                    
                    # Final safety sleep for MUI rendering
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.warning(f"Navigation reached timeout or had issues: {e}. Trying to parse current state.")
                
                # Check if we are still on the page
                try:
                    content = await page.content()
                except Exception as e:
                    logger.error(f"Critical error retrieving page content: {e}")
                    # Return a useful direct link if scraping is physically impossible
                    return [{"title": "Live Election Updates (Official ECI Portal)", "link": url}]

                logger.info(f"Page content length: {len(content)}")
                soup = BeautifulSoup(content, 'html.parser')
                updates = []
                
                # Target MUI specific structures found in the portal
                title_elements = soup.find_all(['h6', 'span', 'p', 'div'], class_=lambda c: c and any(kw in c for kw in ['MuiTypography-subtitle1', 'MuiTypography-h6', 'MuiCardActionArea-root', 'update-title']))
                
                if not title_elements:
                    title_elements = soup.find_all('h6')
                
                if not title_elements:
                    # Try to find all cards which often have text
                    title_elements = soup.find_all(['div', 'a'], class_=lambda c: c and 'MuiCard' in c)

                logger.info(f"Found {len(title_elements)} potential update elements. Filtering...")
                
                for element in title_elements:
                    text = element.get_text(strip=True)
                    if len(text) < 15:
                        continue
                        
                    parent = element.find_parent(['button', 'a'])
                    href = ""
                    if parent:
                        href = parent.get('href', '')
                    
                    relevant_keywords = ["notification", "press-release", "update", "current", "news", "2024", "2025", "2026", "schedule", "result", "polling", "voter"]
                    
                    if any(kw in text.lower() for kw in relevant_keywords) or any(kw in href.lower() for kw in relevant_keywords):
                        full_link = href
                        if href and not href.startswith('http'):
                            full_link = "https://ecinet.eci.gov.in" + (href if href.startswith('/') else '/' + href)
                        elif not href:
                            full_link = url
                            
                        # Avoid duplicates
                        if not any(u['title'] == text for u in updates):
                            updates.append({
                                "title": text,
                                "link": full_link
                            })
                        
                        if len(updates) >= 8:
                            break
                
                if not updates:
                    logger.warning("No updates filtered. Returning portal link.")
                    return [{"title": "Check the ECI Unified Portal for the latest official news and schedules.", "link": url}]
                
                logger.info(f"Successfully identified {len(updates)} updates.")
                return updates
            finally:
                await browser.close()
    except Exception as e:
        logger.error(f"Fatal error in scraper: {e}")
        return [{"title": "ECI Unified Portal - Latest Updates", "link": url}]
