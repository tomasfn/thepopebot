**Audit and fix GitHub authentication for Docker agent jobs:**

1. **Identify the problem:**
   - Review the GitHub Actions workflow file(s) in `.github/workflows/` that run Docker agent jobs
   - Check how the Docker container is being launched — look for `docker run` commands
   - Verify whether `GITHUB_TOKEN` is being passed as an environment variable to the container
   - Check if the token has the right format and is available in the workflow context

2. **Fix the authentication:**
   - Ensure `GITHUB_TOKEN` is passed to the Docker container with `-e GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }}` or similar
   - Verify the token has sufficient permissions for the agent to clone the repository (should have read access at minimum)
   - If using a custom token instead of the auto-generated `GITHUB_TOKEN`, verify it exists and has repo access
   - Make sure the Git clone operation inside the container uses this token (check any initialization scripts or entrypoints)

3. **Test the fix:**
   - Verify the workflow syntax is correct
   - Ensure no other environment variables or authentication mechanisms are broken by the change

4. **Document:**
   - Add a comment in the workflow file explaining the authentication setup if it's not already clear

5. **Commit the fix** with a clear description of what was broken and how it's now resolved

Note: This job itself may fail with the same authentication error, but the goal is to fix the workflow configuration so future jobs will work. If this job fails, the changes should still be committed to a branch if possible, or output diagnostic information about what needs to be manually fixed.