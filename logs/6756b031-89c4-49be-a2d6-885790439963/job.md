**Pivot prospecting script to find "phygital" apps for UGC Gamification SDK offering**

Completely restructure `scripts/ios-prospecting.py` to target retail and food businesses in Spain and Argentina that have both physical presence AND existing customer engagement/loyalty features - perfect targets for a UGC gamification SDK.

**New Business Logic:**

1. **Target UGC & Loyalty Niches:**
   - Change `SEARCH_TERMS` to: `["club de beneficios", "puntos y recompensas", "hamburguesería", "cafetería de especialidad", "cervecería", "heladería", "tienda de ropa", "restaurante barcelona", "compras locales"]`
   - These businesses already engage customers and are primed for gamification

2. **Strict "Phygital" Description Filter (Both Conditions Required):**
   - Fetch the app's `description` field from the API response
   - The app MUST meet BOTH conditions (this is an AND requirement):
   
   **Condition A - Physical Presence Indicators (at least one of):**
   - `["sucursal", "local", "tienda física", "nuestra tienda", "visítanos", "mesa", "barra"]`
   
   **Condition B - Rewards/Interaction Indicators (at least one of):**
   - `["canjear", "puntos", "descuento", "escanear", "código QR", "club", "beneficios", "cupón", "recompensas"]`
   
   - Use case-insensitive matching
   - Only keep apps that have at least one keyword from BOTH lists
   - This ensures they're "phygital" - physical locations with digital engagement

3. **Size Filter for Mid-Sized Chains:**
   - Set `MAX_RATING_COUNT = 2500`
   - Target mid-sized local chains and strong independents
   - Massive chains won't easily adopt third-party SDKs
   - Remove outdated and low rating filters - we want active, functional apps

4. **Run for Both Countries:**
   - First run: `COUNTRY_CODE = 'ES'`, `OUTPUT_FILE = 'es_phygital_leads.csv'`
   - Execute the script
   - Second run: `COUNTRY_CODE = 'AR'`, `OUTPUT_FILE = 'ar_phygital_leads.csv'`
   - Execute the script again

**Technical Notes:**
- Extract the `description` field from the iTunes API response
- Implement the two-condition check: must have physical indicator AND rewards indicator
- Keep pagination, rate limiting with sleep, User-Agent, error handling
- Add clear logging showing:
  - Which apps pass/fail the physical presence check
  - Which apps pass/fail the rewards check
  - Which apps pass both (these are our targets)
- The CSV should include all standard columns (trackId, trackName, artistName, trackViewUrl, sellerUrl, averageUserRating, userRatingCount, currentVersionReleaseDate)

**Testing & Delivery:**
- Run the script for Spain → generate `es_phygital_leads.csv`
- Run the script for Argentina → generate `ar_phygital_leads.csv`
- Verify results show apps that mention BOTH physical locations AND loyalty/rewards
- Commit the updated `scripts/ios-prospecting.py` and both CSV files

This targets businesses that are already doing digital engagement at physical locations - the perfect fit for a UGC gamification SDK that creates missions and rewards.