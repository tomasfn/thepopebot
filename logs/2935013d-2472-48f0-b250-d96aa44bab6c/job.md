**Audit and implement sensitive data filtering for logs and PR content:**

1. **Audit current exposure:**
   - Review GitHub Actions workflow files (`.github/workflows/`) to identify what gets logged (PR titles, descriptions, commit messages, job outputs, etc.)
   - Check the event handler code, Docker agent code, and any PR creation logic to see what data is currently exposed
   - Identify specific places where sensitive data could leak (API keys, tokens, passwords, webhook URLs, credentials, file paths with secrets)

2. **Implement filtering/redaction:**
   - Add logic to detect and redact common sensitive patterns before logging or creating PRs:
     - API keys and tokens (patterns like `key=`, `token=`, `Bearer `, etc.)
     - Passwords and secrets
     - URLs with credentials embedded
     - Environment variables that might contain secrets
     - Any `AGENT_LLM_*` credential values
   - Apply filtering at key points: workflow logs, PR titles, PR descriptions, commit messages, and any other output visible in GitHub
   - Use pattern matching/regex to catch common formats, and consider a configurable list of patterns in `config/` if needed

3. **Document the approach:**
   - Add a brief note to the relevant config or docs explaining what's being filtered and where
   - Ensure the filtering doesn't break legitimate functionality

4. **Test:**
   - Verify that normal operations still work
   - Confirm sensitive patterns would be redacted (check with test strings if possible)

5. **Commit changes** with a clear description of the security improvement