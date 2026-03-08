# iOS App Store Prospecting Script

## Overview

This script searches the Apple App Store for acquisition opportunities by finding apps from smaller developers (< 5,000 ratings) that either have low ratings or haven't been updated recently.

## Quick Start

```bash
python3 scripts/ios-prospecting.py
```

Output: `ios_prospects.csv`

## Configuration

Edit these variables at the top of `scripts/ios-prospecting.py`:

```python
COUNTRY_CODE = 'US'           # Target country (US, GB, CA, etc.)
SEARCH_TERMS = [              # Broad categories to search
    "finance",
    "productivity",
    "fitness",
    "business",
    "utilities"
]
MAX_RATING_COUNT = 5000       # "David vs. Goliath" threshold
LOW_RATING_THRESHOLD = 3.5    # Apps rated below this
DAYS_OUTDATED = 365           # Apps not updated in X days
```

## Filtering Logic

The script finds apps that match:

1. **MUST** have < 5,000 ratings (excludes big corporations)
2. **AND** (rating < 3.5 **OR** not updated in 365+ days)

This ensures you're only prospecting smaller developers with underperforming or neglected apps.

## CSV Output

| Column | Description |
|--------|-------------|
| `trackId` | Unique Apple App ID |
| `trackName` | App name |
| `artistName` | Developer/company name |
| `trackViewUrl` | App Store link |
| `sellerUrl` | Developer website (if available) |
| `averageUserRating` | Rating (0-5) |
| `userRatingCount` | Total number of ratings |
| `currentVersionReleaseDate` | Last update date |

## Examples

### Change target country to UK:
```python
COUNTRY_CODE = 'GB'
```

### Search different categories:
```python
SEARCH_TERMS = ["travel", "food", "shopping", "education"]
```

### More aggressive filtering (really small apps):
```python
MAX_RATING_COUNT = 1000
LOW_RATING_THRESHOLD = 4.0
DAYS_OUTDATED = 180
```

## Rate Limiting

The script respects Apple's rate limits with a 1.5-second delay between API calls. For 5 keywords × 3 pages = 15 calls, expect ~22 seconds execution time.

## Dependencies

- Python 3
- `requests` library

Install: `apt-get install python3-requests` or `pip3 install requests`
