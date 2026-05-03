import asyncio
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scraper import scrape_eci_latest_updates

async def main():
    print("Testing ECI Scraper...")
    updates = await scrape_eci_latest_updates()
    print(f"Scraper returned {len(updates)} results.")
    for update in updates:
        print(f"- {update.get('title')}: {update.get('link')}")

if __name__ == "__main__":
    asyncio.run(main())
