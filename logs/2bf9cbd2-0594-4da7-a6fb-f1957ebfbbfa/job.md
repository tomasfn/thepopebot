**Run iOS prospecting script for Spain and Argentina markets with Spanish keywords**

Modify and execute the existing `scripts/ios-prospecting.py` script to generate leads for Spanish-speaking markets. The US data in `ios_prospects.csv` must remain untouched.

**Task Sequence:**

1. **Update Search Terms to Spanish:**
   - Change `SEARCH_TERMS` to: `["finanzas", "productividad", "salud y forma física", "negocios", "utilidades"]`

2. **Run for Spain:**
   - Set `COUNTRY_CODE = 'ES'`
   - Set `OUTPUT_FILE = 'es_prospects.csv'`
   - Execute the script
   - Verify `es_prospects.csv` is generated with Spanish market data

3. **Run for Argentina:**
   - Update `COUNTRY_CODE = 'AR'`
   - Update `OUTPUT_FILE = 'ar_prospects.csv'`
   - Execute the script again
   - Verify `ar_prospects.csv` is generated with Argentinian market data

**Important:**
- Do NOT modify or delete the existing `ios_prospects.csv` (US data)
- All three CSV files should exist after completion: `ios_prospects.csv`, `es_prospects.csv`, `ar_prospects.csv`
- The script itself should end in a state ready for future runs (doesn't matter which config it's left in)
- Commit all changes including both new CSV files (`es_prospects.csv` and `ar_prospects.csv`)
- Include logging output showing the script ran successfully for both countries

The final repository should have three separate prospect files for easy comparison across markets.