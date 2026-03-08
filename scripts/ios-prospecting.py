#!/usr/bin/env python3
"""
iOS App Store Prospecting Script

Searches the iTunes Search API for iOS apps that may be acquisition or improvement
opportunities based on:
- Low ratings (< 3.5 stars)
- Outdated apps (not updated in 18+ months)

Outputs a CSV file with app details for further analysis.
"""

import requests
import csv
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys

# Configuration
ITUNES_API_URL = "https://itunes.apple.com/search"
SEARCH_TERMS = ["fitness", "productivity", "finance"]
RESULTS_LIMIT = 100
RATING_THRESHOLD = 3.5
MONTHS_OUTDATED = 18
OUTPUT_FILE = "ios_prospects.csv"
REQUEST_DELAY = 0.75  # seconds between API calls

# Calculate the cutoff date for "outdated" apps
REFERENCE_DATE = datetime(2026, 3, 8)
OUTDATED_CUTOFF = REFERENCE_DATE - timedelta(days=MONTHS_OUTDATED * 30)

print(f"🔍 iOS App Store Prospecting Script")
print(f"📅 Reference Date: {REFERENCE_DATE.strftime('%Y-%m-%d')}")
print(f"⏰ Outdated Cutoff: {OUTDATED_CUTOFF.strftime('%Y-%m-%d')} (18 months ago)")
print(f"⭐ Rating Threshold: < {RATING_THRESHOLD}")
print("-" * 70)


def search_apps(term: str) -> List[Dict]:
    """
    Search iTunes API for apps matching the given term.
    
    Args:
        term: Search term to query
        
    Returns:
        List of app dictionaries from the API response
    """
    params = {
        'term': term,
        'entity': 'software',
        'limit': RESULTS_LIMIT,
        'country': 'US'
    }
    
    try:
        print(f"🔎 Searching for '{term}'...", end=" ")
        response = requests.get(ITUNES_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get('results', [])
        print(f"✓ Found {len(results)} apps")
        return results
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {e}")
        return []


def parse_date(date_string: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO date string from iTunes API.
    
    Args:
        date_string: ISO format date string
        
    Returns:
        datetime object or None if parsing fails
    """
    if not date_string:
        return None
    
    try:
        # iTunes API returns dates in ISO 8601 format
        # Example: "2024-01-15T08:00:00Z"
        # Parse and remove timezone info for comparison
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.replace(tzinfo=None)
    except (ValueError, AttributeError):
        return None


def is_outdated(release_date: Optional[datetime]) -> bool:
    """
    Check if an app is outdated (not updated in 18+ months).
    
    Args:
        release_date: Last update date of the app
        
    Returns:
        True if outdated, False otherwise
    """
    if not release_date:
        return False
    return release_date < OUTDATED_CUTOFF


def filter_prospects(apps: List[Dict]) -> List[Dict]:
    """
    Filter apps that meet prospect criteria:
    - Low rating (< 3.5) OR
    - Outdated (18+ months since last update)
    
    Args:
        apps: List of app dictionaries from iTunes API
        
    Returns:
        Filtered list of prospect apps with analysis data
    """
    prospects = []
    
    for app in apps:
        # Extract fields
        rating = app.get('averageUserRating')
        release_date_str = app.get('currentVersionReleaseDate')
        release_date = parse_date(release_date_str)
        
        # Check conditions
        is_low_rated = rating is not None and rating < RATING_THRESHOLD
        is_old = is_outdated(release_date)
        
        # Keep if meets either condition
        if is_low_rated or is_old:
            prospects.append({
                'trackName': app.get('trackName', 'Unknown'),
                'artistName': app.get('artistName', 'Unknown'),
                'trackViewUrl': app.get('trackViewUrl', ''),
                'sellerUrl': app.get('sellerUrl', ''),
                'averageUserRating': rating if rating is not None else '',
                'currentVersionReleaseDate': release_date.strftime('%Y-%m-%d') if release_date else '',
                'isLowRated': is_low_rated,
                'isOutdated': is_old
            })
    
    return prospects


def deduplicate_apps(apps: List[Dict]) -> List[Dict]:
    """
    Remove duplicate apps based on trackViewUrl.
    
    Args:
        apps: List of app dictionaries
        
    Returns:
        Deduplicated list of apps
    """
    seen_urls = set()
    unique_apps = []
    
    for app in apps:
        url = app.get('trackViewUrl', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_apps.append(app)
    
    return unique_apps


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
        'App Name',
        'Developer Name',
        'App Store URL',
        'Developer Website',
        'Rating',
        'Last Updated Date'
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)
            
            for app in prospects:
                writer.writerow([
                    app['trackName'],
                    app['artistName'],
                    app['trackViewUrl'],
                    app['sellerUrl'],
                    app['averageUserRating'],
                    app['currentVersionReleaseDate']
                ])
        
        print(f"💾 Saved {len(prospects)} prospects to '{filename}'")
    except IOError as e:
        print(f"❌ Error saving CSV: {e}")
        sys.exit(1)


def main():
    """Main execution function."""
    all_prospects = []
    
    # Search for each term
    for term in SEARCH_TERMS:
        apps = search_apps(term)
        prospects = filter_prospects(apps)
        
        # Show breakdown
        low_rated = sum(1 for p in prospects if p['isLowRated'])
        outdated = sum(1 for p in prospects if p['isOutdated'])
        both = sum(1 for p in prospects if p['isLowRated'] and p['isOutdated'])
        
        print(f"  📊 Prospects: {len(prospects)} total "
              f"(Low Rated: {low_rated}, Outdated: {outdated}, Both: {both})")
        
        all_prospects.extend(prospects)
        
        # Be respectful to the API
        if term != SEARCH_TERMS[-1]:  # Don't delay after last term
            time.sleep(REQUEST_DELAY)
    
    print("-" * 70)
    
    # Remove duplicates (same app may appear in multiple searches)
    unique_prospects = deduplicate_apps(all_prospects)
    print(f"📱 Total unique prospects: {len(unique_prospects)}")
    
    # Save to CSV
    save_to_csv(unique_prospects, OUTPUT_FILE)
    
    print("✅ Done!")


if __name__ == "__main__":
    main()
