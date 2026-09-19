# Testing

The intended smoke path is:

1. Start with `docker compose up --build`.
2. Open the frontend and sign in with the demo account.
3. Open Diagnose, choose Tomato, and upload a JPG/PNG/WebP image.
4. Confirm the result says `DEMO AI MODE` and shows treatment safety guidance.
5. Search market prices, open buyers/storage/logistics, and create a request.
6. Open My requests and confirm the saved record.
7. Toggle network access in browser developer tools and confirm the offline indicator appears.

Native Python and npm validation should be run in Docker Desktop or a machine with Python 3.11+ and Node 20+ installed.
