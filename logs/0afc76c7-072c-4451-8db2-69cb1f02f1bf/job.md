Investigate why the event handler container is crash-looping:

1. Check Docker container status: `docker ps -a` to see all containers and their states
2. Get event handler logs: `docker logs thepopebot-event-handler` (get last 100 lines)
3. Check recent commits to event handler code — look at git history for files in the event handler directory
4. Review the event handler's package.json, Dockerfile, and startup configuration
5. Look for syntax errors, missing dependencies, or configuration issues
6. Document findings in `debug/event-handler-crash-$(date +%Y%m%d).md` with:
   - Error logs
   - Recent changes that might have caused it
   - Root cause analysis
   - Proposed fix

If you can identify the issue, attempt a fix and verify the container can start successfully.