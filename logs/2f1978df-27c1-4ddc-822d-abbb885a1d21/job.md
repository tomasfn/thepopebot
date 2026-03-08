**Create a lead enrichment script to extract developer contact emails from websites**

Create a new Python script at `scripts/enrich-leads.py` that reads prospect data and enriches it with contact emails scraped from developer websites.

**Requirements:**

1. **Input:**
   - Read from `ios_prospects.csv`
   - Process all rows, looking for the `Developer Website` column (mapped from `sellerUrl`)

2. **Web Scraping with Protection:**
   - Use the `requests` library to fetch webpage HTML
   - **Critical**: Include a realistic User-Agent header to avoid bot detection:
     ```python
     headers = {
         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
     }
     ```
   - Set `timeout=10` seconds for each request
   - Use try/except blocks to handle connection errors, timeouts, and HTTP errors gracefully
   - Continue processing other leads if one website fails
   - Add a small delay between requests (e.g., `time.sleep(0.5)`) to be respectful

3. **Email Extraction:**
   - Use regex to find email addresses in the HTML text
   - Use a robust pattern like: `r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'`
   - Make the search case-insensitive

4. **Junk Email Filtering:**
   - Exclude emails starting with: `sentry@`, `noreply@`, `no-reply@`, `admin@`
   - Exclude strings ending with image extensions: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`
   - Consider also filtering out other common non-contact emails like: `support@`, `info@`, `webmaster@`, `postmaster@` (use your judgment on these)

5. **Output CSV:**
   - Create `enriched_ios_prospects.csv` with all original columns PLUS a new `Contact_Email` column at the end
   - If multiple valid emails are found, join them with a comma and space (`, `)
   - If no website exists, website is unreachable, or no emails found, leave the `Contact_Email` cell empty
   - Preserve all original data exactly as it was

6. **Logging:**
   - Print progress showing which lead is being processed
   - Show when emails are found vs. not found
   - Show errors/timeouts in a user-friendly way

7. **Testing & Delivery:**
   - Run the script on `ios_prospects.csv` to generate `enriched_ios_prospects.csv`
   - Verify the output CSV has the new Contact_Email column with discovered emails
   - Commit both `scripts/enrich-leads.py` and `enriched_ios_prospects.csv` to the repository
   - Include helpful comments in the script explaining the logic

The script should be robust enough to handle various edge cases (missing URLs, dead websites, malformed HTML, etc.) without crashing.