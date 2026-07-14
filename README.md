# Email Analyzer V8 Enterprise

Main improvements:
- Removes Gmail interface noise before analysis.
- Tries multiple Gemini models automatically.
- Displays the Gemini model that worked.
- Always provides a professional local report if Gemini is unavailable.
- Includes executive summary, sender purpose, key points, risks, scam probability, actions and clickable links.

Upload all five files to GitHub:
- app.py
- requirements.txt
- render.yaml
- README.md
- .gitignore

Render Start Command:
gunicorn --workers 1 --threads 4 --timeout 70 app:app

Environment:
GEMINI_API_KEY = your private Gemini API key
GEMINI_MODEL = gemini-3.1-flash-lite-preview

Then use Manual Deploy > Deploy latest commit.
