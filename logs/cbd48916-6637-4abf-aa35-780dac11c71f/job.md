Build a Shopify Plus lead generation pipeline:

1. **Scrape BuiltWith free list**: Navigate to builtwith.com/websites/shopify-plus using the browser. Extract all visible brand domains and names from the free listing. Save to `data/shopify-leads-raw.json`.

2. **Scrape Shopify App Store (UGC apps)**: Go to apps.shopify.com and search for popular UGC/review apps: "Loox", "Stamped.io", "Judge.me", "Yotpo". For each app, extract store names/URLs from the reviews section (stores that left reviews). These are pre-qualified leads who already spend on UGC tools. Add to the same JSON file.

3. **Enrich with basic info**: For each domain collected, visit the site briefly to extract:
   - Store name
   - Primary product category (fashion, beauty, fitness, food, etc.)
   - Whether store appears active (has products, recent updates)
   - Store URL

4. **Structure the output**: Create `data/shopify-plus-leads.csv` with columns: Domain, Brand Name, Category, Active (yes/no), Source (BuiltWith/App Store), Notes.

5. **Prioritize**: Sort by category and filter to brands that look like good UGC fits (active stores with visual products).

Target: 50-200 qualified leads. Focus on brands in fashion, beauty, fitness, food, and lifestyle.

Do not attempt email lookup or Apollo/Hunter scraping yet — just build the domain/brand list first. We'll handle contact enrichment in a follow-up job if needed.