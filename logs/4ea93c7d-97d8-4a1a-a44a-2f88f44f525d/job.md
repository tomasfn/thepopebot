Test job to verify Docker agent functionality:

1. Create a test file at `test-job-output.txt` with the current date/time and a test message
2. Run `uname -a` to check system info
3. Run `node --version` and `npm --version` to verify Node.js is available
4. List the contents of the current directory with `ls -la`
5. Verify the test file exists and read its contents
6. Delete the test file to clean up
7. Report success with a summary of what was tested

This is a basic smoke test to confirm the Docker agent can execute commands, create/read/delete files, and complete a job successfully.