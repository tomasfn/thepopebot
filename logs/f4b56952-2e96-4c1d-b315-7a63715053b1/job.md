Build a Shopify Plus lead generation pipeline with error handling:

1. **Check if data directory exists**, create it if not: `mkdir -p data`

2. **Scrape BuiltWith**: Navigate to builtwith.com/websites/shopify-plus with browser automation. Take a screenshot on arrival. Extract all visible domains/brand names. If blocked or no data found, log the issue and continue. Save findings to `data/shopify-leads-raw.json`.

3. **Scrape Shopify App Store**: Search for "Loox", "Stamped.io", "Judge.me" on apps.shopify.com. For each app page, extract store URLs/names from reviews. Take screenshots if extraction fails. Save to the raw JSON file.

4. **Enrich**: For each collected domain (limit to first 50 to avoid timeouts), visit the site and extract: brand name, category guess, whether it looks active. Log any domains that fail to load.

5. **Generate CSV**: Create `data/shopify-plus-leads.csv` with headers: Domain, Brand Name, Category, Active, Source, Notes. Even if you only get 10-20 leads, output them.

6. **Summary report**: Create `data/scraping-report.md` documenting what worked, what failed, how many leads collected, any errors encountered.

Prioritize getting SOME data over perfect data. If BuiltWith blocks you, focus on the App Store method. Target at least 20-50 leads minimum.