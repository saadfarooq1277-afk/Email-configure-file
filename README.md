# Email Analyzer V5 — Optimized Clickable Links

Fixes:
- Gunicorn timeout increased to 120 seconds
- One worker to reduce RAM use
- Hidden links filtered and capped
- Footer, unsubscribe, privacy, tracking and app-store links removed
- Deterministic title-to-link matching
- Frontend handles invalid server responses safely

Upload these files to the GitHub repository root:
- app.py
- requirements.txt
- render.yaml
- README.md
- .gitignore

Then in Render update the Start Command to:
gunicorn --workers 1 --threads 2 --timeout 120 app:app

After commit:
Manual Deploy > Deploy latest commit
