# Privacy Configuration

## Auto-Merge Exclusions

### Log Files

Job logs in the `/logs` directory are **excluded from auto-merge** and require manual review before merging to the main branch.

**Rationale**: Log files may contain sensitive conversation data, including:
- User messages and chat interactions
- API responses with potentially private information
- Task details and execution traces
- System prompts and agent reasoning

### How It Works

The auto-merge workflow (`.github/workflows/auto-merge.yml`) automatically merges pull requests from `job/*` branches, but includes a specific check that blocks any PR containing changes to the `/logs` directory.

When a PR is blocked due to log file changes, you'll see:
```
BLOCKED (privacy): logs/... - logs require manual review
```

### Configuration

The `ALLOWED_PATHS` repository variable controls which paths can be auto-merged:
- **Default**: `/` (all paths except logs)
- **Logs exception**: Always blocked, regardless of `ALLOWED_PATHS` setting
- **Custom paths**: Set `ALLOWED_PATHS` to a comma-separated list (e.g., `config/,docs/`)

### Manual Review Process

When a job creates or modifies log files:

1. The PR is created automatically
2. Auto-merge is blocked due to privacy protection
3. A maintainer should:
   - Review the log contents for sensitive information
   - Redact or remove sensitive data if needed
   - Manually merge or close the PR

### Disabling Auto-Merge Entirely

To disable auto-merge for all job PRs, set the repository variable:
```
AUTO_MERGE=false
```

This requires manual review of all automated changes, not just logs.
