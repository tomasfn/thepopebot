#!/usr/bin/env python3
"""
Lead Enrichment Script
======================
Reads prospect data from CSV and enriches it by scraping developer websites
for contact email addresses.

Usage: python scripts/enrich-leads.py
"""

import csv
import re
import time
import requests
from typing import List, Set

# Configuration
INPUT_FILE = 'ios_prospects.csv'
OUTPUT_FILE = 'enriched_ios_prospects.csv'
REQUEST_TIMEOUT = 10  # seconds
REQUEST_DELAY = 0.5  # seconds between requests

# Realistic User-Agent to avoid bot detection
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Email regex pattern - matches standard email formats
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', re.IGNORECASE)

# Junk email prefixes to filter out
JUNK_PREFIXES = [
    'sentry@',
    'noreply@',
    'no-reply@',
    'admin@',
    'support@',
    'info@',
    'webmaster@',
    'postmaster@',
    'abuse@',
    'privacy@',
    'legal@',
    'security@',
    'help@',
    'sales@',
    'hello@',
    'contact@',  # Often generic forms, not direct emails
]

# Image file extensions to filter out (false positives in email regex)
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp', '.ico']


def is_junk_email(email: str) -> bool:
    """
    Check if an email should be filtered out as junk.
    
    Args:
        email: Email address to check
        
    Returns:
        True if email is junk, False if it's valid
    """
    email_lower = email.lower()
    
    # Check for junk prefixes
    for prefix in JUNK_PREFIXES:
        if email_lower.startswith(prefix):
            return True
    
    # Check for image file extensions (false positives)
    for ext in IMAGE_EXTENSIONS:
        if email_lower.endswith(ext):
            return True
    
    return False


def extract_emails_from_html(html: str) -> List[str]:
    """
    Extract valid email addresses from HTML content.
    
    Args:
        html: Raw HTML content as string
        
    Returns:
        List of unique, valid email addresses
    """
    # Find all email-like patterns
    all_emails = EMAIL_PATTERN.findall(html)
    
    # Use set to deduplicate, then filter out junk
    unique_emails: Set[str] = set()
    
    for email in all_emails:
        if not is_junk_email(email):
            unique_emails.add(email.lower())  # Normalize to lowercase
    
    return sorted(list(unique_emails))


def scrape_website_for_emails(url: str) -> List[str]:
    """
    Scrape a website and extract contact emails.
    
    Args:
        url: Website URL to scrape
        
    Returns:
        List of found email addresses (empty if error or none found)
    """
    if not url or url.strip() == '':
        return []
    
    # Ensure URL has a protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # Make request with timeout and custom headers
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Extract emails from HTML
        emails = extract_emails_from_html(response.text)
        
        return emails
        
    except requests.exceptions.Timeout:
        print(f"  ⏱️  Timeout accessing {url}")
        return []
    
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Connection error for {url}")
        return []
    
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ HTTP error {e.response.status_code} for {url}")
        return []
    
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error accessing {url}: {str(e)}")
        return []
    
    except Exception as e:
        print(f"  ❌ Unexpected error for {url}: {str(e)}")
        return []


def enrich_leads():
    """
    Main function to read prospects CSV, enrich with emails, and write output.
    """
    print(f"\n🚀 Starting lead enrichment from {INPUT_FILE}\n")
    
    try:
        # Read input CSV
        with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            if not fieldnames:
                print("❌ Error: CSV file has no headers")
                return
            
            # Add new column for contact emails
            output_fieldnames = list(fieldnames) + ['Contact_Email']
            
            # Store enriched rows
            enriched_rows = []
            
            # Process each lead
            for i, row in enumerate(reader, 1):
                app_name = row.get('App Name', 'Unknown')
                developer_name = row.get('Developer Name', 'Unknown')
                website = row.get('Developer Website', '')
                
                print(f"[{i}] Processing: {app_name} by {developer_name}")
                
                if not website or website.strip() == '':
                    print(f"  ⚠️  No website provided")
                    row['Contact_Email'] = ''
                else:
                    print(f"  🔍 Scraping {website}")
                    emails = scrape_website_for_emails(website)
                    
                    if emails:
                        row['Contact_Email'] = ', '.join(emails)
                        print(f"  ✅ Found {len(emails)} email(s): {row['Contact_Email']}")
                    else:
                        row['Contact_Email'] = ''
                        print(f"  ⚠️  No valid emails found")
                    
                    # Be respectful - delay between requests
                    time.sleep(REQUEST_DELAY)
                
                enriched_rows.append(row)
                print()  # Blank line for readability
            
            # Write output CSV
            print(f"💾 Writing enriched data to {OUTPUT_FILE}")
            with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
                writer.writeheader()
                writer.writerows(enriched_rows)
            
            print(f"\n✅ Enrichment complete! Processed {len(enriched_rows)} leads")
            print(f"📄 Output saved to: {OUTPUT_FILE}\n")
    
    except FileNotFoundError:
        print(f"❌ Error: Could not find {INPUT_FILE}")
        print(f"   Please ensure the input CSV file exists in the current directory.")
    
    except csv.Error as e:
        print(f"❌ CSV error: {str(e)}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


if __name__ == '__main__':
    enrich_leads()
