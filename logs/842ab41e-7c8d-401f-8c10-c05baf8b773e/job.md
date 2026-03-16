Research and compile a list of fashion brands (major and mid-size) in Europe and the United States that have physical stores and would benefit from a UGC (user-generated content) missions widget.

**Requirements:**

1. **Target Criteria:**
   - Fashion retail brands with physical store locations in Europe and/or US
   - Mix of major brands and mid-size retail chains
   - Brands that would benefit from customer UGC content (look for those with active social media, community engagement, or lacking social proof on their sites)

2. **Research Tasks:**
   - Use web search to identify 30-50 qualifying fashion brands
   - For each brand, visit their website and find contact information
   - Prioritize finding decision-maker emails (marketing directors, CMOs, digital marketing leads, brand managers)
   - If specific decision-maker contacts aren't available, collect general marketing/sales/contact emails
   - Analyze why each brand would benefit from UGC (e.g., lacks customer photos, strong social presence but not leveraging it on site, experiential retail focus, etc.)

3. **Output Format:**
   - Create a CSV file at `data/fashion-brands-ugc-leads.csv` with columns:
     - Brand Name
     - Website
     - Email Contact (prioritize decision-makers)
     - Contact Title/Type (e.g., "Marketing Director" or "General Sales")
     - Industry Segment (e.g., "Fast Fashion", "Luxury", "Athleisure", "Streetwear")
     - Approximate Store Count/Regions
     - Why They'd Benefit from UGC (brief analysis)
     - Current UGC Strategy (if observable - "None visible", "Limited Instagram integration", etc.)

4. **Research Strategy:**
   - Search for "fashion retail brands with stores [region]"
   - Check brand websites for "Contact", "Press", "Partnerships", "About" pages
   - Look for LinkedIn company pages to identify marketing leadership

5. **CRITICAL - File Delivery:**
   - Ensure the `data/` directory exists (create if needed)
   - Save the CSV file to `data/fashion-brands-ugc-leads.csv`
   - Create a summary report at `data/ugc-leads-summary.md` with methodology and key findings
   - Use git add to stage both files: `git add data/fashion-brands-ugc-leads.csv data/ugc-leads-summary.md`
   - Verify the files are included in your commit before pushing

The deliverable MUST include the CSV file with actual brand data - do not complete the job without creating and committing this file.