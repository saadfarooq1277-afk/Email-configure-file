# Email Analyzer Web App

## What it does
Users paste an email and receive:
- summary
- action items and deadlines
- risk/phishing indicators
- public web verification
- official global links
- product/service alternatives when relevant
- Urdu, English, or Arabic output

## Deploy on Render
1. Create a free GitHub repository and upload all project files.
2. In Render, choose **New > Web Service** and connect the repository.
3. Render should detect `render.yaml`.
4. Add the secret environment variable:
   `OPENAI_API_KEY = your OpenAI API key`
5. Deploy. Render will provide a public URL you can forward.

## Run locally
```bash
pip install -r requirements.txt
set OPENAI_API_KEY=your_key_here
python app.py
```
On macOS/Linux use:
```bash
export OPENAI_API_KEY=your_key_here
python app.py
```

Open http://localhost:5000

## Important
- API usage is billed to the account owning the API key.
- Never put the API key in HTML or JavaScript.
- Add authentication, rate limits, and a privacy notice before broad public use.
