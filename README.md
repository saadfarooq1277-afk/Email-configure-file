# Gemini Email Analyzer

## Render deployment

1. Upload all files and folders to your GitHub repository root.
2. In Render, connect the repository as a Web Service.
3. Use:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Add Environment Variable:
   - Key: `GEMINI_API_KEY`
   - Value: your private Gemini API key
5. Deploy.

Do not place your API key inside app.py, HTML, JavaScript, GitHub, screenshots, or chat messages.
