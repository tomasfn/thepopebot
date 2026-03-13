#!/usr/bin/env python3
"""
iOS App Store Phygital Prospecting Script

Finds retail and food businesses in Spain and Argentina with both:
1. Physical presence (stores, locations)
2. Digital engagement/loyalty features

These are perfect targets for a UGC gamification SDK.

Uses the iTunes Search API to find apps and applies strict "phygital" filters.
"""

import requests
import csv
import time
from typing import List, Dict, Set
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration - CHANGE THESE FOR EACH RUN
COUNTRY_CODE = 'ES'  # 'ES' for Spain, 'AR' for Argentina
OUTPUT_FILE = 'es_phygital_leads.csv'  # Change to 'ar_phygital_leads.csv' for Argentina

# Search terms targeting UGC & Loyalty niches
SEARCH_TERMS = [
    "club de beneficios",
    "puntos y recompensas", 
    "hamburguesería",
    "cafetería de especialidad",
    "cervecería",
    "heladería",
    "tienda de ropa",
    "restaurante barcelona",
    "compras locales"
]

# Size filter - target mid-sized chains, avoid massive corporations
MAX_RATING_COUNT = 2500

# Phygital filter keywords (case-insensitive)
# BOTH conditions must be met (AND logic)
PHYSICAL_PRESENCE_KEYWORDS = [
    "sucursal", "local", "tienda física", "nuestra tienda", 
    "visítanos", "mesa", "barra"
]

REWARDS_INTERACTION_KEYWORDS = [
    "canjear", "puntos", "descuento", "escanear", "código QR", 
    "club", "beneficios", "cupón", "recompensas"
]

RESULTS_PER_TERM = 50
API_BASE_URL = 'https://itunes.apple.com/search'

def has_keywords(text: str, keywords: List[str]) -> tuple[bool, List[str]]:
    """
    Check if text contains any of the keywords (case-insensitive).
    
    Args:
        text: Text to search in
        keywords: List of keywords to search for
        
    Returns:
        Tuple of (bool indicating if any keyword found, list of matched keywords)
    """
    if not text:
        return False, []
    
    text_lower = text.lower()
    matched = [kw for kw in keywords if kw.lower() in text_lower]
    return len(matched) > 0, matched

def passes_phygital_filter(app: Dict) -> tuple[bool, str]:
    """
    Check if app meets BOTH phygital conditions.
    
    Args:
        app: Raw app data from iTunes API
        
    Returns:
        Tuple of (bool indicating if passes, reason string)
    """
    description = app.get('description', '')
    track_name = app.get('trackName', 'Unknown')
    
    # Check Condition A: Physical presence indicators
    has_physical, physical_matches = has_keywords(description, PHYSICAL_PRESENCE_KEYWORDS)
    
    # Check Condition B: Rewards/interaction indicators  
    has_rewards, rewards_matches = has_keywords(description, REWARDS_INTERACTION_KEYWORDS)
    
    # BOTH conditions must be met (AND logic)
    if has_physical and has_rewards:
        logger.info(f"✓ PASS: '{track_name}' - Physical: {physical_matches[:2]}, Rewards: {rewards_matches[:2]}")
        return True, "Has both physical presence and rewards/interaction"
    elif not has_physical and not has_rewards:
        logger.debug(f"✗ FAIL: '{track_name}' - Missing both physical and rewards indicators")
        return False, "Missing both physical and rewards indicators"
    elif not has_physical:
        logger.debug(f"✗ FAIL: '{track_name}' - Missing physical presence indicators (has rewards: {rewards_matches[:2]})")
        return False, "Missing physical presence indicators"
    else:  # not has_rewards
        logger.debug(f"✗ FAIL: '{track_name}' - Missing rewards/interaction indicators (has physical: {physical_matches[:2]})")
        return False, "Missing rewards/interaction indicators"

def passes_size_filter(app: Dict) -> tuple[bool, str]:
    """
    Check if app is mid-sized (not massive chain).
    
    Args:
        app: Raw app data from iTunes API
        
    Returns:
        Tuple of (bool indicating if passes, reason string)
    """
    rating_count = app.get('userRatingCount', 0)
    track_name = app.get('trackName', 'Unknown')
    
    if rating_count > MAX_RATING_COUNT:
        logger.debug(f"✗ SIZE FILTER: '{track_name}' - Too many ratings ({rating_count:,} > {MAX_RATING_COUNT:,})")
        return False, f"Too many ratings ({rating_count:,})"
    
    return True, "Within size range"

def search_app_store(term: str, country: str, limit: int = 50) -> List[Dict]:
    """
    Search the App Store for apps matching the given term.
    
    Args:
        term: Search term/category
        country: Two-letter country code (e.g., 'ES', 'AR')
        limit: Maximum number of results to return
        
    Returns:
        List of app dictionaries
    """
    params = {
        'term': term,
        'country': country,
        'entity': 'software',
        'limit': limit
    }
    
    # Add User-Agent to avoid blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        logger.info(f"Searching for '{term}' in {country}...")
        response = requests.get(API_BASE_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results = data.get('results', [])
        logger.info(f"Found {len(results)} apps for '{term}'")
        return results
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching for '{term}': {e}")
        return []

def extract_lead_info(app: Dict) -> Dict:
    """
    Extract relevant lead information from app data.
    
    Args:
        app: Raw app data from iTunes API
        
    Returns:
        Dictionary with cleaned lead information
    """
    return {
        'trackId': app.get('trackId', ''),
        'trackName': app.get('trackName', ''),
        'artistName': app.get('artistName', ''),
        'trackViewUrl': app.get('trackViewUrl', ''),
        'sellerUrl': app.get('sellerUrl', ''),
        'averageUserRating': app.get('averageUserRating', ''),
        'userRatingCount': app.get('userRatingCount', 0),
        'currentVersionReleaseDate': app.get('currentVersionReleaseDate', '')
    }

def save_to_csv(leads: List[Dict], filename: str):
    """
    Save lead data to CSV file.
    
    Args:
        leads: List of lead dictionaries
        filename: Output CSV filename
    """
    if not leads:
        logger.warning("No leads to save!")
        return
    
    fieldnames = [
        'trackId', 'trackName', 'artistName', 'trackViewUrl', 
        'sellerUrl', 'averageUserRating', 'userRatingCount', 
        'currentVersionReleaseDate'
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(leads)
        
        logger.info(f"Successfully saved {len(leads)} phygital leads to {filename}")
        
    except IOError as e:
        logger.error(f"Error writing to {filename}: {e}")

def main():
    """Main execution function."""
    logger.info("=" * 80)
    logger.info(f"PHYGITAL APP PROSPECTING - {COUNTRY_CODE}")
    logger.info("=" * 80)
    logger.info(f"Target: Apps with BOTH physical presence AND rewards/loyalty features")
    logger.info(f"Max rating count: {MAX_RATING_COUNT:,}")
    logger.info(f"Search terms: {SEARCH_TERMS}")
    logger.info(f"Output file: {OUTPUT_FILE}")
    logger.info("=" * 80)
    
    all_leads = []
    seen_apps: Set[int] = set()
    
    total_found = 0
    total_duplicates = 0
    total_failed_size = 0
    total_failed_phygital = 0
    
    for term in SEARCH_TERMS:
        apps = search_app_store(term, COUNTRY_CODE, RESULTS_PER_TERM)
        total_found += len(apps)
        
        for app in apps:
            app_id = app.get('trackId')
            
            # Skip duplicates
            if app_id in seen_apps:
                total_duplicates += 1
                continue
            
            seen_apps.add(app_id)
            
            # Apply size filter
            passes_size, size_reason = passes_size_filter(app)
            if not passes_size:
                total_failed_size += 1
                continue
            
            # Apply phygital filter (BOTH conditions must pass)
            passes_phygital, phygital_reason = passes_phygital_filter(app)
            if not passes_phygital:
                total_failed_phygital += 1
                continue
            
            # This app passed all filters!
            lead = extract_lead_info(app)
            all_leads.append(lead)
        
        # Be nice to the API - rate limiting
        time.sleep(1.5)
    
    # Summary
    logger.info("=" * 80)
    logger.info("PROSPECTING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total apps found: {total_found}")
    logger.info(f"Duplicates skipped: {total_duplicates}")
    logger.info(f"Failed size filter (>{MAX_RATING_COUNT:,} ratings): {total_failed_size}")
    logger.info(f"Failed phygital filter (missing physical OR rewards): {total_failed_phygital}")
    logger.info(f"✓ QUALIFIED PHYGITAL LEADS: {len(all_leads)}")
    logger.info("=" * 80)
    
    # Save to CSV
    save_to_csv(all_leads, OUTPUT_FILE)
    
    logger.info("Prospecting complete!")

if __name__ == '__main__':
    main()
