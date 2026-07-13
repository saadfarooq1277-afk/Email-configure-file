import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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
        return jsonify({"error": "Email is too long. Please keep it under 30,000 characters."}), 400
    if not os.environ.get("OPENAI_API_KEY"):
        return jsonify({"error": "Server API key is not configured."}), 500

    answer_language = LANGUAGES.get(language, "Urdu")
    prompt = f"""
Analyze the email below and answer in {answer_language}.

EMAIL:
{email_text}

Provide a structured report with:
1. Short summary
2. What the email is about
3. Sender's main request or purpose
4. Required actions and deadlines
5. Important names, companies, products, dates, prices, locations, and contact details
6. Risks, suspicious claims, phishing indicators, contradictions, or missing information
7. Verified public information related to the email topic
8. Official and trustworthy global links relevant to the subject
9. If a product or service is discussed: official website, global sellers/suppliers,
   Saudi Arabia availability when relevant, alternatives, and competitors
10. A clear separation between verified facts, email claims, and assumptions

Do not guess. Do not expose private data unnecessarily. Use web search only for public
verification and relevant official links. Warn the user before following payment,
login, password-reset, attachment, or unknown-domain links.
"""

    try:
        response = client.responses.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-5-mini"),
            tools=[{"type": "web_search"}],
            input=prompt,
        )
        return jsonify({"result": response.output_text})
    except Exception as exc:
        return jsonify({"error": f"Analysis failed: {str(exc)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
