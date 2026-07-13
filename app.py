import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

LANGUAGES = {
    "ur": "Urdu",
    "en": "English",
    "ar": "Arabic",
}

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    email_text = (data.get("email_text") or "").strip()
    language = data.get("language", "ur")

    if not email_text:
        return jsonify({"error": "Please paste the email text."}), 400

    if len(email_text) > 30000:
        return jsonify({"error": "Email is too long. Keep it under 30,000 characters."}), 400

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY is not configured on the server."}), 500

    answer_language = LANGUAGES.get(language, "Urdu")
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    prompt = f"""
You are a careful email-analysis assistant.

Analyze the email below and answer in {answer_language}.

EMAIL:
{email_text}

Create a structured report containing:

1. Short summary
2. What the email is about
3. Sender's main request or purpose
4. Required actions and deadlines
5. Important names, companies, products, dates, prices, locations, and contact details
6. Risks, contradictions, suspicious claims, phishing indicators, or missing information
7. Public facts that can be verified online
8. Relevant official and trustworthy global links
9. If a product or service is discussed:
   - official website
   - global sellers or suppliers
   - Saudi Arabia availability when relevant
   - alternatives and competitors
10. Separate clearly:
   - claims made inside the email
   - independently verified public facts
   - assumptions or uncertain points

Do not guess. Do not reveal private information unnecessarily.
Warn the user before following payment, password-reset, login, attachment,
or unknown-domain links.
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            ),
        )
        result = response.text or "No analysis was returned."
        return jsonify({"result": result})
    except Exception as exc:
        return jsonify({"error": f"Analysis failed: {str(exc)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
