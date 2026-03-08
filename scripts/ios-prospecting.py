#!/usr/bin/env python3
"""
iOS App Store Prospecting Script
Finds apps with low ratings or outdated versions from smaller developers (< 5000 ratings)
"""

import requests
import csv
import time
from datetime import datetime
from typing import List, Dict

# Configuration
COUNTRY_CODE = 'US'
SEARCH_TERMS = ["finance", "productivity", "fitness", "business", "utilities"]
RESULTS_PER_PAGE = 100
PAGES_PER_KEYWORD = 3
RATE_LIMIT_DELAY = 1.5  # seconds between API calls
OUTPUT_FILE = 'ios_prospects.csv'

# Filter thresholds
MAX_RATING_COUNT = 5000  # "David vs. Goliath" filter - skip big corporations
LOW_RATING_THRESHOLD = 3.5  # Apps with ratings below this
DAYS_OUTDATED = 365  # Apps not updated in this many days

def search_apps(term: str, offset: int = 0) -> List[Dict]:
    """
    Search iTunes App Store API for apps matching the search term.
    
    Args:
        term: Search keyword
        offset: Pagination offset
        
    Returns:
        List of app dictionaries from API response
    """
    url = f"https://itunes.apple.com/search?term={term}&entity=software&limit={RESULTS_PER_PAGE}&offset={offset}&country={COUNTRY_CODE}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data for '{term}' (offset {offset}): {e}")
        return []

def is_outdated(release_date_str: str) -> bool:
    """
    Check if an app hasn't been updated in over DAYS_OUTDATED days.
    
    Args:
        release_date_str: ISO format date string
        
    Returns:
        True if app is outdated, False otherwise
    """
    try:
        release_date = datetime.fromisoformat(release_date_str.replace('Z', '+00:00'))
        days_since_update = (datetime.now(release_date.tzinfo) - release_date).days
        return days_since_update > DAYS_OUTDATED
    except (ValueError, AttributeError):
        return False

def filter_prospects(apps: List[Dict]) -> List[Dict]:
    """
    Filter apps to find prospecting opportunities.
    
    Criteria:
    1. MUST have < 5000 ratings (David vs. Goliath filter)
    2. AND (low rating < 3.5 OR outdated > 365 days)
    
    Args:
        apps: List of app dictionaries from API
        
    Returns:
        Filtered list of prospect apps
    """
    prospects = []
    
    for app in apps:
        # Skip if missing critical data
        if 'averageUserRating' not in app or 'userRatingCount' not in app:
            continue
            
        rating_count = app.get('userRatingCount', 0)
        rating = app.get('averageUserRating', 0)
        release_date = app.get('currentVersionReleaseDate', '')
        
        # CRITICAL: David vs. Goliath filter - skip big corporations
        if rating_count >= MAX_RATING_COUNT:
            continue
        
        # Apply existing filters: low rating OR outdated
        is_low_rated = rating < LOW_RATING_THRESHOLD
        is_app_outdated = is_outdated(release_date)
        
        if is_low_rated or is_app_outdated:
            prospects.append(app)
    
    return prospects

def extract_app_data(app: Dict) -> Dict:
    """
    Extract relevant fields from app data for CSV export.
    
    Args:
        app: App dictionary from API
        
    Returns:
        Dictionary with extracted fields
    """
    return {
        'trackId': app.get('trackId', ''),
        'trackName': app.get('trackName', ''),
        'artistName': app.get('artistName', ''),
        'trackViewUrl': app.get('trackViewUrl', ''),
        'sellerUrl': app.get('sellerUrl', ''),
        'averageUserRating': app.get('averageUserRating', ''),
        'userRatingCount': app.get('userRatingCount', ''),
        'currentVersionReleaseDate': app.get('currentVersionReleaseDate', '')
    }

def save_to_csv(prospects: List[Dict], filename: str):
    """
    Save prospect apps to CSV file.
    
    Args:
        prospects: List of prospect app dictionaries
        filename: Output CSV filename
    """
    if not prospects:
        print("⚠️  No prospects found to save")
        return
    
    fieldnames = [
        'trackId',
        'trackName',
        'artistName',
        'trackViewUrl',
        'sellerUrl',
        'averageUserRating',
        'userRatingCount',
        'currentVersionReleaseDate'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(prospects)
    
    print(f"✅ Saved {len(prospects)} prospects to {filename}")

def main():
    """
    Main execution function.
    """
    print("=" * 70)
    print("iOS APP STORE PROSPECTING SCRIPT")
    print("=" * 70)
    print(f"Country: {COUNTRY_CODE}")
    print(f"Search Terms: {', '.join(SEARCH_TERMS)}")
    print(f"Max Rating Count: {MAX_RATING_COUNT} (David vs. Goliath filter)")
    print(f"Low Rating Threshold: {LOW_RATING_THRESHOLD}")
    print(f"Outdated Threshold: {DAYS_OUTDATED} days")
    print(f"Pages per keyword: {PAGES_PER_KEYWORD}")
    print("=" * 70)
    print()
    
    all_prospects = []
    api_calls = 0
    
    for term in SEARCH_TERMS:
        print(f"🔍 Searching: '{term}'")
        
        for page in range(PAGES_PER_KEYWORD):
            offset = page * RESULTS_PER_PAGE
            print(f"   📄 Page {page + 1}/{PAGES_PER_KEYWORD} (offset={offset})...", end=" ")
            
            # Fetch apps
            apps = search_apps(term, offset)
            api_calls += 1
            
            if not apps:
                print("No results")
                break
            
            # Filter for prospects
            prospects = filter_prospects(apps)
            print(f"Found {len(prospects)} prospects from {len(apps)} apps")
            
            # Extract data and add to collection
            for app in prospects:
                app_data = extract_app_data(app)
                # Avoid duplicates (same trackId)
                if not any(p['trackId'] == app_data['trackId'] for p in all_prospects):
                    all_prospects.append(app_data)
            
            # Rate limiting - respect Apple's API limits
            if api_calls < len(SEARCH_TERMS) * PAGES_PER_KEYWORD:
                time.sleep(RATE_LIMIT_DELAY)
        
        print()
    
    print("=" * 70)
    print(f"📊 SUMMARY")
    print("=" * 70)
    print(f"Total API calls: {api_calls}")
    print(f"Unique prospects found: {len(all_prospects)}")
    print()
    
    # Save results
    save_to_csv(all_prospects, OUTPUT_FILE)
    print()
    print("✨ Done!")

if __name__ == "__main__":
    main()
