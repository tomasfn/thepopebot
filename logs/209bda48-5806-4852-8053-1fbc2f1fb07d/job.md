This job will perform a lead generation task to find Shopify Plus merchants and their marketing contacts.

**Phase 1: Domain Scraping**
1. Navigate to builtwith.com/websites/shopify-plus.
2. Scrape the list of websites on the page, aiming to collect between 100 and 200 domains.
3. Save this list to a temporary file for the next phase.

**Phase 2: Contact Enrichment**
1. For each domain collected, log in and search for the company on apollo.io.
2. Filter the employee list for titles like "Marketing Manager," "Content Manager," "Brand Manager," "Growth Manager," or "Head of Marketing."
3. From the filtered list, extract the name, title, email address, and LinkedIn URL for the most relevant contact.

**Final Output**
1. Compile all the collected data into a single CSV file located at `output/shopify_plus_leads.csv`.
2. The CSV file will have the following columns: `domain`, `contact_name`, `title`, `email`, `linkedin_url`.