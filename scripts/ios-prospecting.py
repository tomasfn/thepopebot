#!/usr/bin/env python3
"""
iOS App Store Prospecting Script - Hyper-Targeted for Small Abandoned Apps

Searches the App Store for small, abandoned utility apps in LatAm/Spain.
Uses aggressive filtering to target independent developers with struggling apps.

Filtering Strategy:
- MANDATORY: App must be outdated (18+ months since last update)
- MANDATORY: Rating count < 250 (filters out large companies)
- BONUS: Low rating (< 3.0) indicates struggling app
- Focus on long-tail Spanish utility keywords

Uses the iTunes Search API to find apps and developer details.
"""

import requests
import csv
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
# Hyper-specific Spanish utility keywords to avoid banks/fintechs
SEARCH_TERMS = [
    "calculadora de propinas",
    "creador de facturas", 
    "control de gastos diarios",
    "gestor de inventario",
    "turnos y reservas",
    "registro de kilometraje"
]
COUNTRY_CODE = 'AR'  # Argentina
OUTPUT_FILE = 'ar_hyper_targeted_prospects.csv'
RESULTS_PER_TERM = 50  # Number of apps to fetch per search term
API_BASE_URL = 'https://itunes.apple.com/search'

# Filtering thresholds
MAX_RATING_COUNT = 250  # Apps with more ratings are typically large companies
LOW_RATING_THRESHOLD = 3.0  # Severely struggling apps (bonus signal)
MONTHS_OUTDATED = 18  # Must be 18+ months since last update

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
        'current_version_release_date': app.get('currentVersionReleaseDate', 'N/A'),
        'bundle_id': app.get('bundleId', 'N/A'),
        'description': app.get('description', 'N/A')[:200] + '...' if app.get('description') else 'N/A'
    }

def is_app_outdated(app: Dict, months: int = MONTHS_OUTDATED) -> bool:
    """
    Check if an app hasn't been updated in the specified number of months.
    
    Args:
        app: Raw app data from iTunes API
        months: Number of months to consider outdated
        
    Returns:
        True if app is outdated, False otherwise
    """
    # Use currentVersionReleaseDate (last update) if available, otherwise releaseDate
    date_str = app.get('currentVersionReleaseDate') or app.get('releaseDate')
    
    if not date_str:
        return False
    
    try:
        # Parse ISO 8601 date format
        release_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        cutoff_date = datetime.now(release_date.tzinfo) - timedelta(days=months * 30)
        
        return release_date < cutoff_date
    except (ValueError, AttributeError) as e:
        logger.debug(f"Could not parse date '{date_str}': {e}")
        return False

def passes_filters(app: Dict) -> tuple[bool, str]:
    """
    Apply strict filtering to identify small, abandoned apps.
    
    MANDATORY FILTERS (both must pass):
    - Rating count < MAX_RATING_COUNT (filters out large companies)
    - App is outdated (MONTHS_OUTDATED+ months since update)
    
    BONUS SIGNAL:
    - Low rating (< LOW_RATING_THRESHOLD) indicates struggling app
    
    Args:
        app: Raw app data from iTunes API
        
    Returns:
        Tuple of (passes: bool, reason: str)
    """
    app_name = app.get('trackName', 'Unknown')
    rating_count = app.get('userRatingCount', 0) or 0
    rating = app.get('averageUserRating')
    
    # MANDATORY: Rating count must be below threshold
    if rating_count >= MAX_RATING_COUNT:
        return False, f"Too many ratings ({rating_count} >= {MAX_RATING_COUNT}) - likely large company"
    
    # MANDATORY: App must be outdated
    if not is_app_outdated(app):
        return False, f"Not outdated (< {MONTHS_OUTDATED} months) - still actively maintained"
    
    # If we get here, both mandatory filters passed
    # Check for bonus low rating signal
    has_low_rating = rating and rating < LOW_RATING_THRESHOLD
    
    if has_low_rating:
        reason = f"✓ PERFECT TARGET: Small ({rating_count} ratings), abandoned, AND struggling (rating: {rating:.1f})"
    else:
        reason = f"✓ Good target: Small ({rating_count} ratings) and abandoned"
    
    return True, reason

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
        'rating', 'rating_count', 'release_date', 'current_version_release_date',
        'bundle_id', 'description'
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
    """Main execution function with aggressive filtering."""
    logger.info("=" * 80)
    logger.info("iOS HYPER-TARGETED PROSPECTING - Small Abandoned Apps")
    logger.info("=" * 80)
    logger.info(f"Country: {COUNTRY_CODE}")
    logger.info(f"Search terms: {SEARCH_TERMS}")
    logger.info(f"Output file: {OUTPUT_FILE}")
    logger.info("")
    logger.info("FILTERING CRITERIA:")
    logger.info(f"  ✓ MANDATORY: Rating count < {MAX_RATING_COUNT}")
    logger.info(f"  ✓ MANDATORY: Not updated in {MONTHS_OUTDATED}+ months")
    logger.info(f"  ✓ BONUS: Rating < {LOW_RATING_THRESHOLD} (struggling app)")
    logger.info("=" * 80)
    logger.info("")
    
    all_prospects = []
    seen_apps = set()  # Track unique apps to avoid duplicates
    total_found = 0
    total_filtered_out = 0
    
    for term in SEARCH_TERMS:
        apps = search_app_store(term, COUNTRY_CODE, RESULTS_PER_TERM)
        
        logger.info(f"\n--- Filtering results for '{term}' ---")
        term_kept = 0
        term_filtered = 0
        
        for app in apps:
            app_id = app.get('trackId')
            app_name = app.get('trackName', 'Unknown')
            
            # Skip duplicates
            if app_id in seen_apps:
                continue
            
            total_found += 1
            seen_apps.add(app_id)
            
            # Apply strict filtering
            passes, reason = passes_filters(app)
            
            if passes:
                prospect = extract_prospect_info(app)
                all_prospects.append(prospect)
                term_kept += 1
                logger.info(f"  {reason} - '{app_name}'")
            else:
                term_filtered += 1
                total_filtered_out += 1
                logger.debug(f"  ✗ Filtered out: {reason} - '{app_name}'")
        
        logger.info(f"  → Kept {term_kept}/{len(apps)} apps from '{term}'")
        
        # Be nice to the API
        time.sleep(1)
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("FINAL RESULTS:")
    logger.info(f"  Total apps found: {total_found}")
    logger.info(f"  Filtered out: {total_filtered_out}")
    logger.info(f"  High-quality prospects: {len(all_prospects)}")
    logger.info(f"  Conversion rate: {len(all_prospects)/total_found*100:.1f}%" if total_found > 0 else "  Conversion rate: 0%")
    logger.info("=" * 80)
    
    # Save to CSV
    if all_prospects:
        save_to_csv(all_prospects, OUTPUT_FILE)
        logger.info("")
        logger.info(f"✓ Successfully exported {len(all_prospects)} hyper-targeted prospects!")
    else:
        logger.warning("")
        logger.warning("⚠ No prospects passed the strict filters. Consider adjusting search terms.")
    
    logger.info("")
    logger.info("Prospecting complete!")

if __name__ == '__main__':
    main()
