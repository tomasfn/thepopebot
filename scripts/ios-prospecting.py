#!/usr/bin/env python3
"""
iOS App Store Prospecting Script

Searches the App Store for apps in specified categories and extracts
developer contact information for prospecting purposes.

Uses the iTunes Search API to find apps and developer details.
"""

import requests
import csv
import time
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SEARCH_TERMS = ["finance", "productivity", "health & fitness", "business", "utilities"]
COUNTRY_CODE = 'US'
OUTPUT_FILE = 'ios_prospects.csv'
RESULTS_PER_TERM = 50  # Number of apps to fetch per search term
API_BASE_URL = 'https://itunes.apple.com/search'

def search_app_store(term: str, country: str, limit: int = 50) -> List[Dict]:
    """
    Search the App Store for apps matching the given term.
    
    Args:
        term: Search term/category
        country: Two-letter country code (e.g., 'US', 'ES', 'AR')
        limit: Maximum number of results to return
        
    Returns:
        List of app dictionaries with developer information
    """
    params = {
        'term': term,
        'country': country,
        'entity': 'software',
        'limit': limit
    }
    
    try:
        logger.info(f"Searching for '{term}' in {country}...")
        response = requests.get(API_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results = data.get('results', [])
        logger.info(f"Found {len(results)} apps for '{term}'")
        return results
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching for '{term}': {e}")
        return []

def extract_prospect_info(app: Dict) -> Dict:
    """
    Extract relevant prospecting information from app data.
    
    Args:
        app: Raw app data from iTunes API
        
    Returns:
        Dictionary with cleaned prospect information
    """
    return {
        'app_name': app.get('trackName', 'N/A'),
        'app_id': app.get('trackId', 'N/A'),
        'developer_name': app.get('artistName', 'N/A'),
        'developer_id': app.get('artistId', 'N/A'),
        'developer_url': app.get('artistViewUrl', 'N/A'),
        'app_url': app.get('trackViewUrl', 'N/A'),
        'category': app.get('primaryGenreName', 'N/A'),
        'price': app.get('formattedPrice', 'N/A'),
        'rating': app.get('averageUserRating', 'N/A'),
        'rating_count': app.get('userRatingCount', 'N/A'),
        'release_date': app.get('releaseDate', 'N/A'),
        'bundle_id': app.get('bundleId', 'N/A'),
        'description': app.get('description', 'N/A')[:200] + '...' if app.get('description') else 'N/A'
    }

def save_to_csv(prospects: List[Dict], filename: str):
    """
    Save prospect data to CSV file.
    
    Args:
        prospects: List of prospect dictionaries
        filename: Output CSV filename
    """
    if not prospects:
        logger.warning("No prospects to save!")
        return
    
    fieldnames = [
        'app_name', 'app_id', 'developer_name', 'developer_id', 
        'developer_url', 'app_url', 'category', 'price', 
        'rating', 'rating_count', 'release_date', 'bundle_id', 'description'
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(prospects)
        
        logger.info(f"Successfully saved {len(prospects)} prospects to {filename}")
        
    except IOError as e:
        logger.error(f"Error writing to {filename}: {e}")

def main():
    """Main execution function."""
    logger.info(f"Starting iOS prospecting for country: {COUNTRY_CODE}")
    logger.info(f"Search terms: {SEARCH_TERMS}")
    logger.info(f"Output file: {OUTPUT_FILE}")
    
    all_prospects = []
    seen_apps = set()  # Track unique apps to avoid duplicates
    
    for term in SEARCH_TERMS:
        apps = search_app_store(term, COUNTRY_CODE, RESULTS_PER_TERM)
        
        for app in apps:
            app_id = app.get('trackId')
            
            # Skip duplicates
            if app_id in seen_apps:
                continue
                
            seen_apps.add(app_id)
            prospect = extract_prospect_info(app)
            all_prospects.append(prospect)
        
        # Be nice to the API
        time.sleep(1)
    
    logger.info(f"Total unique prospects found: {len(all_prospects)}")
    
    # Save to CSV
    save_to_csv(all_prospects, OUTPUT_FILE)
    
    logger.info("Prospecting complete!")

if __name__ == '__main__':
    main()
