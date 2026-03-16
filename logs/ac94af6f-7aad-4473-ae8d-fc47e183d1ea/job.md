**Run lead enrichment script for Spain and Argentina prospect files**

Use the existing `scripts/enrich-leads.py` script to enrich the Spanish-speaking market prospect files with developer contact emails.

**Task Sequence:**

1. **Enrich Spain Prospects:**
   - Modify the script to read from `es_prospects.csv` as input
   - Change the output file to `enriched_es_prospects.csv`
   - Execute the script
   - Verify `enriched_es_prospects.csv` is generated with the new `Contact_Email` column

2. **Enrich Argentina Prospects:**
   - Modify the script to read from `ar_prospects.csv` as input
   - Change the output file to `enriched_ar_prospects.csv`
   - Execute the script
   - Verify `enriched_ar_prospects.csv` is generated with the new `Contact_Email` column

**Important:**
- The input files (`es_prospects.csv` and `ar_prospects.csv`) should now be in main branch since job 2bf9cbd2-0594-4da7-a6fb-f1957ebfbbfa was merged
- All the existing enrichment logic should remain the same (User-Agent headers, timeout, email regex, junk filtering, error handling)
- Commit both enriched output files: `enriched_es_prospects.csv` and `enriched_ar_prospects.csv`
- Include logging showing progress for both runs

The final repository should have enriched prospect data for both Spanish-speaking markets ready for outreach.