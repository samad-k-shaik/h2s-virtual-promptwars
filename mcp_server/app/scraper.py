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
            browser = await p.chromium.launch(headless=True)
            try:
                context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                page = await context.new_page()
                
                logger.info(f"Navigating to {url}...")
                try:
                    # Try domcontentloaded first as it's faster and more reliable on slow sites
                    await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    # Then wait a bit for any dynamic content
                    await asyncio.sleep(3)
                except Exception as e:
                    logger.warning(f"Navigation issue, trying to proceed with available content: {e}")
                
                # Try to wait for the specific results text if it exists
                try:
                    await page.wait_for_selector("text=Result(s)", timeout=10000)
                except:
                    pass
                
                content = await page.content()
                logger.info(f"Page content length: {len(content)}")
                soup = BeautifulSoup(content, 'html.parser')
                updates = []
                # Target MUI specific structures found in the portal
                # 1. H6 tags inside CardActionArea
                # 2. MuiTypography-subtitle1
                # 3. Any element with 'title' or 'update' in class
                title_elements = soup.find_all(['h6', 'span', 'p', 'div'], class_=lambda c: c and any(kw in c for kw in ['MuiTypography-subtitle1', 'MuiTypography-h6', 'MuiCardActionArea-root', 'update-title']))
                
                if not title_elements:
                    # Direct check for all h6 tags which often contain titles
                    title_elements = soup.find_all('h6')
                
                if not title_elements:
                    # Fallback to all links and common containers
                    title_elements = soup.find_all(['a', 'button', 'div'], recursive=True)

                logger.info(f"Found {len(title_elements)} potential update titles. Filtering...")
                
                for element in title_elements:
                    text = element.get_text(strip=True)
                    # For links, we look for the nearest parent button or a tag
                    parent = element.find_parent(['button', 'a'])
                    href = ""
                    if parent:
                        href = parent.get('href', '')
                        # If it's a button, it might have data-url or similar, but often in MUI it's just a click handler
                        # For now, we'll use the text to identify relevance
                    
                    is_download_link = "/eci-backend/public/api/download" in href
                    relevant_keywords = ["notification", "press-release", "update", "current", "news", "2024", "2025", "2026", "schedule", "result", "polling", "voter"]
                    
                    if len(text) > 15 and (any(kw in text.lower() for kw in relevant_keywords) or any(kw in href.lower() for kw in relevant_keywords)):
                        full_link = href
                        if href and not href.startswith('http'):
                            full_link = "https://ecinet.eci.gov.in" + (href if href.startswith('/') else '/' + href)
                        elif not href:
                            # Fallback link to the portal itself if we can't find a direct document link
                            full_link = url
                            
                        updates.append({
                            "title": text,
                            "link": full_link
                        })
                        if len(updates) >= 10:
                            break
                
                if not updates:
                    logger.warning("No updates found on Unified Portal. Returning general link.")
                    return [{"title": "Visit ECI Unified Portal for the latest updates.", "link": url}]
                
                logger.info(f"Successfully identified {len(updates)} updates from Unified Portal.")
                return updates
            finally:
                await browser.close()
    except Exception as e:
        logger.error(f"Error scraping ECI Unified Portal: {e}")
        return [{"error": f"Failed to fetch updates: {str(e)}"}]
