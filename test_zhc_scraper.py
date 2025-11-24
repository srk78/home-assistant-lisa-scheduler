"""Test script for ZHC custom scraper.

This script helps you test and debug the ZHC scraper before using it in Home Assistant.

Usage:
    python test_zhc_scraper.py

The script will:
1. Attempt to fetch schedules from both URLs
2. Show any events found
3. Save the HTML for manual inspection if needed
4. Provide debugging information
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the custom_components to the path
sys.path.insert(0, str(Path(__file__).parent))

from custom_components.zhc_heating_scheduler.zhc_custom_scraper import ZHCCustomScraper

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def test_scraper():
    """Test the ZHC custom scraper."""
    print("=" * 70)
    print("ZHC Heating Scheduler - Scraper Test")
    print("=" * 70)
    print()
    
    scraper = ZHCCustomScraper()
    
    print("Fetching schedules from:")
    print(f"  Training: {scraper.training_url}")
    print(f"  Matches:  {scraper.match_url}")
    print()
    
    try:
        events = await scraper.fetch_schedule(days_ahead=14)
        
        print("=" * 70)
        print(f"RESULTS: Found {len(events)} events")
        print("=" * 70)
        print()
        
        if events:
            # Group events by type
            training_events = [e for e in events if e.event_type == "training"]
            match_events = [e for e in events if e.event_type == "match"]
            
            print(f"📅 Training events: {len(training_events)}")
            print(f"🏑 Match events: {len(match_events)}")
            print()
            
            # Show first few events
            print("Upcoming events:")
            print("-" * 70)
            for i, event in enumerate(events[:10], 1):
                print(f"{i}. {event.event_type.upper()}")
                print(f"   Title: {event.title}")
                print(f"   Start: {event.start_time.strftime('%Y-%m-%d %H:%M')}")
                print(f"   End:   {event.end_time.strftime('%Y-%m-%d %H:%M')}")
                print()
            
            if len(events) > 10:
                print(f"... and {len(events) - 10} more events")
            
            print()
            print("✅ SUCCESS: Scraper is working!")
            print()
            print("Next steps:")
            print("1. Review the events above")
            print("2. If they look correct, the scraper is ready to use")
            print("3. Update coordinator.py to use ZHCCustomScraper")
            
        else:
            print("⚠️  WARNING: No events found!")
            print()
            print("Possible reasons:")
            print("1. The website uses JavaScript to load content dynamically")
            print("2. The HTML structure is different than expected")
            print("3. There are no events scheduled in the next 14 days")
            print()
            print("Troubleshooting steps:")
            print("1. Check the debug logs above for any error messages")
            print("2. Visit the URLs in a browser to verify events exist")
            print("3. Check browser Developer Tools > Network tab for API calls")
            print("4. Look for AJAX/fetch requests when the page loads")
            print()
            print("The page HTML has been logged above. Look for:")
            print("- JavaScript files that load the schedule")
            print("- API endpoints in the Network tab")
            print("- Hidden JSON data in the HTML")
            
    except Exception as e:
        print("❌ ERROR: Scraper failed!")
        print()
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("This error needs to be fixed before the scraper can work.")
    
    finally:
        await scraper._session.close()


async def save_html_for_inspection():
    """Save HTML from both pages for manual inspection."""
    print("\nSaving HTML files for manual inspection...")
    
    scraper = ZHCCustomScraper()
    
    try:
        # Fetch and save training page
        training_html = await scraper._fetch_html_from_url(scraper.training_url)
        with open('zhc_training_page.html', 'w', encoding='utf-8') as f:
            f.write(training_html)
        print(f"✅ Saved training page HTML to: zhc_training_page.html")
        
        # Fetch and save match page
        match_html = await scraper._fetch_html_from_url(scraper.match_url)
        with open('zhc_match_page.html', 'w', encoding='utf-8') as f:
            f.write(match_html)
        print(f"✅ Saved match page HTML to: zhc_match_page.html")
        
        print()
        print("You can now:")
        print("1. Open these HTML files in a text editor")
        print("2. Search for schedule data, API endpoints, or JSON")
        print("3. Use this info to customize the scraper")
        
    finally:
        await scraper._session.close()


if __name__ == "__main__":
    print()
    print("Starting ZHC scraper test...")
    print()
    
    # Run the scraper test
    asyncio.run(test_scraper())
    
    # Optionally save HTML files
    print()
    response = input("Save HTML files for manual inspection? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(save_html_for_inspection())
    
    print()
    print("Test complete!")

