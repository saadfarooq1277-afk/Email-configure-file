# Email Analyzer V6 Stable

Why this version is stable:
- Email links are extracted locally, without waiting for Gemini.
- Gemini receives only a short plain-text email excerpt.
- Fast Gemini 2.5 Flash-Lite is used.
- Maximum AI request timeout is 35 seconds.
- If Gemini fails or times out, the app still returns a professional report with all clickable links.
- No web-search tool is used during analysis.
- HTML and large link lists are never sent to Gemini.

Upload all five files to GitHub, commit, then update Render Start Command:

gunicorn --workers 1 --threads 4 --timeout 75 app:app

Then use Manual Deploy > Deploy latest commit.
