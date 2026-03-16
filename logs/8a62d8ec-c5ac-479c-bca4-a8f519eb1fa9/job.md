**Hyper-target iOS prospecting script for small, abandoned apps in LatAm/Spain**

Update `scripts/ios-prospecting.py` to apply much more aggressive filtering that targets truly small, independent developers with abandoned apps — filtering out large companies like banks and fintechs.

**Critical Filter Changes:**

1. **Lower the Rating Count Threshold:**
   - Change `MAX_RATING_COUNT` from `5000` to `250`
   - Apps with more than 250 ratings in LatAm/Spain are typically large companies

2. **Raise the Low Rating Bar:**
   - Change `LOW_RATING_THRESHOLD` from `3.5` to `3.0`
   - Only include apps with ratings strictly below 3.0 (severely struggling)

3. **STRICT "AND" Logic (Most Important Change):**
   - **Current logic**: Keep if (low_rating OR outdated)
   - **NEW logic**: Keep ONLY if (rating_count < 250 AND is_outdated)
   - The low rating becomes a bonus signal, NOT a primary filter
   - Being outdated (18+ months) is now MANDATORY
   - This targets abandoned apps that need external help

4. **Narrow Search Terms to Long-Tail Utilities:**
   - Replace broad categories with hyper-specific Spanish utility keywords:
   - New `SEARCH_TERMS`: `["calculadora de propinas", "creador de facturas", "control de gastos diarios", "gestor de inventario", "turnos y reservas", "registro de kilometraje"]`
   - These avoid banks/fintechs and target small utility apps

5. **Set Country:**
   - Ensure `COUNTRY_CODE = 'AR'` (Argentina)

6. **Output File:**
   - Set `OUTPUT_FILE = 'ar_hyper_targeted_prospects.csv'` to distinguish from the previous broader search

**Testing & Delivery:**
- Run the updated script to generate `ar_hyper_targeted_prospects.csv`
- Verify the results show truly small apps (< 250 ratings) that are ALL outdated
- The result set should be much smaller but higher quality
- Commit both the updated script and the new CSV file
- Include logging that shows the stricter filtering in action

The goal is a curated list of small, abandoned utility apps in Argentina where developers likely need help or might be willing to sell.