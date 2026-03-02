Update the repository configuration to prevent auto-merging of log files:

1. Check the current `ALLOWED_PATHS` setting in `.github/workflows/auto-merge.yml` 
2. Modify the auto-merge workflow or update the GitHub repository variable `ALLOWED_PATHS` to exclude `/logs` directory
3. Document the change in a file at `docs/privacy-config.md` explaining that logs containing conversations are not auto-merged for privacy

The goal is to ensure that job logs (which may contain sensitive conversation data) require manual review before merging, while other changes can still be auto-merged.

Commit changes with message "config: exclude logs from auto-merge for privacy"