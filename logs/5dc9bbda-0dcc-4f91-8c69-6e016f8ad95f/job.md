**Update the iOS App Store prospecting script with broader search and corporate filtering**

Update the existing script at `scripts/ios-prospecting.py` with the following improvements:

**Changes Required:**

1. **Broader Search Terms:**
   - Replace the current 3 search terms with 5 broader categories: `["finance", "productivity", "fitness", "business", "utilities"]`

2. **Geographical Targeting:**
   - Add a configurable variable at the top: `COUNTRY_CODE = 'US'`
   - Append `&country={COUNTRY_CODE}` to the iTunes Search API URL

3. **"David vs. Goliath" Filter (Critical New Logic):**
   - Add a **mandatory filter**: `userRatingCount < 5000`
   - This filter must be applied BEFORE the existing conditions
   - If an app has 5,000+ ratings, skip it entirely (it's from a massive corporation)
   - The existing filters (low rating OR outdated) still apply to apps that pass the rating count filter

4. **Pagination:**
   - Implement pagination using the `offset` parameter
   - Fetch up to 300 results per keyword (3 pages of 100 results each: offset=0, offset=100, offset=200)
   - **Critical**: Add `time.sleep(1.5)` between each API call to respect Apple's rate limits

5. **Additional Data Fields:**
   - Extract and add `trackId` (unique Apple App ID) to the CSV
   - Extract and add `userRatingCount` (total number of ratings) to the CSV
   - Update CSV columns to include these new fields

6. **Updated CSV Output:**
   - Columns should now be:
     - Track ID (`trackId`)
     - App Name (`trackName`)
     - Developer Name (`artistName`)
     - App Store URL (`trackViewUrl`)
     - Developer Website (`sellerUrl` - if available)
     - Rating (`averageUserRating`)
     - Rating Count (`userRatingCount`)
     - Last Updated Date (`currentVersionReleaseDate`)

7. **Testing & Delivery:**
   - Run the updated script to verify it works with the new pagination and filtering
   - Ensure the CSV shows only apps with < 5,000 ratings
   - Verify the sleep delays are working (script should take time to complete)
   - Commit both the updated `scripts/ios-prospecting.py` and the new `ios_prospects.csv`

The script should maintain good logging to show progress through keywords and pagination offsets.