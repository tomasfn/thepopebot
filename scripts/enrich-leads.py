#!/usr/bin/env python3
"""
Lead Enrichment Script

Enriches prospect CSV files by scraping developer websites
for contact email addresses.

Features:
- Scrapes developer URLs and app URLs for email addresses
- Filters out common junk/generic emails
- Handles timeouts and errors gracefully
- Configurable input/output files
- Progress logging
"""

import requests
import csv
import re
import time
import logging
from typing import Optional, List, Set
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
INPUT_FILE = 'ar_prospects.csv'
OUTPUT_FILE = 'enriched_ar_prospects.csv'
REQUEST_TIMEOUT = 10  # seconds
REQUEST_DELAY = 0.5  # seconds between requests (be nice to servers)

# User-Agent to appear as a real browser
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Email regex pattern
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# Junk email patterns to filter out
JUNK_PATTERNS = [
    r'no-?reply@',
    r'noreply@',
    r'donotreply@',
    r'support@',
    r'help@',
    r'info@apple\.com',
    r'@example\.com',
    r'@test\.com',
    r'@localhost',
    r'privacy@',
    r'legal@',
    r'abuse@',
    r'postmaster@',
    r'admin@',
    r'webmaster@',
]

def is_junk_email(email: str) -> bool:
    """
    Check if an email matches common junk/generic patterns.
    
    Args:
        email: Email address to check
        
    Returns:
        True if email appears to be junk/generic
    """
    email_lower = email.lower()
    for pattern in JUNK_PATTERNS:
        if re.search(pattern, email_lower):
            return True
    return False

def extract_emails_from_text(text: str) -> Set[str]:
    """
    Extract all valid email addresses from text.
    
    Args:
        text: Text content to search
        
    Returns:
        Set of unique email addresses found
    """
    emails = set()
    matches = EMAIL_PATTERN.findall(text)
    
    for email in matches:
        # Filter out junk emails
        if not is_junk_email(email):
            emails.add(email.lower())
    
    return emails

def scrape_url_for_emails(url: str) -> Set[str]:
    """
    Scrape a URL for email addresses.
    
    Args:
        url: URL to scrape
        
    Returns:
        Set of email addresses found
    """
    if not url or url == 'N/A':
        return set()
    
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Extract emails from page content
        emails = extract_emails_from_text(response.text)
        
        return emails
        
    except requests.exceptions.Timeout:
        logger.debug(f"Timeout scraping {url}")
        return set()
    except requests.exceptions.RequestException as e:
        logger.debug(f"Error scraping {url}: {e}")
        return set()
    except Exception as e:
        logger.debug(f"Unexpected error scraping {url}: {e}")
        return set()

def find_contact_email(prospect: dict) -> Optional[str]:
    """
    Find a contact email for a prospect by scraping their URLs.
    
    Args:
        prospect: Dictionary with prospect information
        
    Returns:
        Best contact email found, or None
    """
    all_emails = set()
    
    # Try developer URL first (most likely to have contact info)
    developer_url = prospect.get('developer_url', '')
    if developer_url and developer_url != 'N/A':
        emails = scrape_url_for_emails(developer_url)
        all_emails.update(emails)
        
        # If we found emails on developer page, use those
        if emails:
            logger.debug(f"Found {len(emails)} email(s) on developer page")
            return sorted(emails)[0]  # Return first alphabetically for consistency
    
    # Try app URL as fallback
    app_url = prospect.get('app_url', '')
    if app_url and app_url != 'N/A':
        emails = scrape_url_for_emails(app_url)
        all_emails.update(emails)
    
    # Return best email found, or None
    if all_emails:
        return sorted(all_emails)[0]
    return None

def enrich_prospects(input_file: str, output_file: str):
    """
    Enrich prospects CSV file with contact email addresses.
    
    Args:
        input_file: Input CSV filename
        output_file: Output CSV filename
    """
    logger.info(f"Starting enrichment: {input_file} -> {output_file}")
    
    try:
        # Read input CSV
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            prospects = list(reader)
            fieldnames = reader.fieldnames
        
        logger.info(f"Loaded {len(prospects)} prospects from {input_file}")
        
        # Add Contact_Email field if not present
        if 'Contact_Email' not in fieldnames:
            fieldnames = list(fieldnames) + ['Contact_Email']
        
        # Enrich each prospect
        enriched_count = 0
        for i, prospect in enumerate(prospects, 1):
            developer_name = prospect.get('developer_name', 'Unknown')
            app_name = prospect.get('app_name', 'Unknown')
            
            logger.info(f"[{i}/{len(prospects)}] Processing: {developer_name} - {app_name}")
            
            # Find contact email
            email = find_contact_email(prospect)
            
            if email:
                prospect['Contact_Email'] = email
                enriched_count += 1
                logger.info(f"  ✓ Found email: {email}")
            else:
                prospect['Contact_Email'] = ''
                logger.info(f"  ✗ No email found")
            
            # Be nice to servers - add delay between requests
            if i < len(prospects):
                time.sleep(REQUEST_DELAY)
        
        # Write output CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(prospects)
        
        logger.info(f"✓ Enrichment complete!")
        logger.info(f"  Total prospects: {len(prospects)}")
        logger.info(f"  Emails found: {enriched_count} ({enriched_count/len(prospects)*100:.1f}%)")
        logger.info(f"  Output saved to: {output_file}")
        
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        raise
    except IOError as e:
        logger.error(f"Error reading/writing files: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during enrichment: {e}")
        raise

def main():
    """Main execution function."""
    logger.info("="*60)
    logger.info("Lead Enrichment Script")
    logger.info("="*60)
    
    enrich_prospects(INPUT_FILE, OUTPUT_FILE)

if __name__ == '__main__':
    main()
