# Single-File Gemini Email Analyzer

Upload these files directly to the root of your GitHub repository:

- app.py
- requirements.txt
- render.yaml
- README.md
- .gitignore

No templates or static folders are needed.

Render settings:
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Environment Variable: `GEMINI_API_KEY`

After uploading, use **Manual Deploy > Deploy latest commit** in Render.
