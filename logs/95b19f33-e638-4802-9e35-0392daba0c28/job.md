**Create an iOS App Store prospecting script to find acquisition/improvement opportunities**

Write a Python script at `scripts/ios-prospecting.py` that searches the iTunes Search API for poorly-rated or outdated iOS apps.

**Requirements:**

1. **API Integration:**
   - Use the iTunes Search API: `https://itunes.apple.com/search`
   - Search parameters: `entity=software`, `limit=100` per term
   - Test with 3 search terms: "fitness", "productivity", "finance"

2. **Filtering Logic:**
   - **Condition A (Low Rating):** `averageUserRating < 3.5`
   - **Condition B (Outdated):** `currentVersionReleaseDate` is older than 18 months from today (2026-03-08)
   - Keep apps that meet **either** Condition A **OR** Condition B (or both)

3. **Output CSV:**
   - Save to `ios_prospects.csv` in the repository root
   - Columns:
     - App Name (`trackName`)
     - Developer Name (`artistName`)
     - App Store URL (`trackViewUrl`)
     - Developer Website (`sellerUrl` - if available, otherwise empty)
     - Rating (`averageUserRating`)
     - Last Updated Date (`currentVersionReleaseDate`)

4. **Implementation Details:**
   - Handle missing fields gracefully (some apps may not have ratings or all fields)
   - Parse the `currentVersionReleaseDate` (ISO format) and calculate if it's 18+ months old
   - Use proper error handling for API requests
   - Add a small delay between API calls to be respectful (0.5-1 second)
   - Include helpful logging/print statements showing progress

5. **Testing & Delivery:**
   - Run the script to verify it works and generates real data
   - Ensure the CSV is properly formatted and contains meaningful prospects
   - Commit both the script (`scripts/ios-prospecting.py`) and the generated output (`ios_prospects.csv`) to the repository
   - Include a brief comment at the top of the script explaining its purpose

The script should be production-ready, well-commented, and ready to be extended with more search terms in the future.