Fix the event handler crash-loop issue. The container now has `server.js` but crashes with error: `TypeError: routesManifest.dataRoutes is not iterable`.

Investigation needed:
1. Examine `templates/server.js` and `my-agent/server.js` - what is it trying to do with routesManifest?
2. Check if `.next` build artifacts exist in the container
3. Verify if `npm run build` needs to be run
4. Check Next.js version compatibility

Options to fix:
- Update server.js to handle missing/different routesManifest structure
- Ensure Next.js build runs in Dockerfile before starting
- Or simplify: just use `next start` directly instead of the custom server if WebSocket proxy isn't critical

Document findings and implement the fix in the Dockerfile and/or server.js.