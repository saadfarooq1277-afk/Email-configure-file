import os
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

LANGUAGES = {"ur": "Urdu", "en": "English", "ar": "Arabic"}

HTML = r'''<!doctype html>
<html lang="ur" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Email Analyzer</title>
  <style>
    *{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:#eef2f7;color:#172033}
    .wrap{max-width:860px;margin:0 auto;padding:28px 16px}.card{background:#fff;border-radius:22px;padding:28px;box-shadow:0 16px 45px rgba(30,41,59,.12)}
    .header,.actions,.resultHead{display:flex;align-items:center;justify-content:space-between;gap:12px}.badge{font-size:12px;font-weight:700;letter-spacing:1px;color:#2563eb}
    h1{margin:5px 0 0;font-size:30px}h2{margin:0}p{line-height:1.7;color:#526075}label{display:block;font-weight:700;margin:18px 0 8px}
    select,textarea,button{font:inherit}select{padding:10px 12px;border:1px solid #d6dce6;border-radius:10px;background:#fff}
    textarea{width:100%;min-height:260px;padding:16px;border:1px solid #ccd5e1;border-radius:14px;resize:vertical;line-height:1.6}
    textarea:focus{outline:2px solid #bfdbfe;border-color:#2563eb}.actions{justify-content:flex-start;margin-top:16px}
    button{border:0;border-radius:11px;padding:12px 20px;background:#1d4ed8;color:#fff;font-weight:700;cursor:pointer}button:disabled{opacity:.55;cursor:not-allowed}
    .secondary{background:#e8edf5;color:#23314a}.small{padding:8px 13px}.status{min-height:24px;margin-top:14px;color:#1d4ed8}
    .result{margin-top:18px;padding:20px;border-radius:15px;background:#f7f9fc;border:1px solid #e1e7ef}pre{white-space:pre-wrap;word-wrap:break-word;font-family:Arial,sans-serif;line-height:1.75;margin-bottom:0}
    .hidden{display:none}.privacy{font-size:13px;margin-bottom:0}.error{color:#b91c1c}@media(max-width:600px){.card{padding:20px}.header{align-items:flex-start}h1{font-size:25px}}
  </style>
</head>
<body>
  <main class="wrap"><section class="card">
    <div class="header"><div><span class="badge">GEMINI AI EMAIL TOOL</span><h1 id="title">ای میل اینالائزر</h1></div>
      <select id="language"><option value="ur">اردو</option><option value="en">English</option><option value="ar">العربية</option></select></div>
    <p id="intro">ای میل کا مکمل متن پیسٹ کریں۔ یہ ٹول اسی ویب سائٹ پر سمری، ضروری ایکشن، خطرات اور متعلقہ عالمی لنکس دکھائے گا۔</p>
    <label id="emailLabel" for="emailText">ای میل کا متن</label><textarea id="emailText" maxlength="30000" placeholder="ای میل یہاں پیسٹ کریں..."></textarea>
    <div class="actions"><button id="analyzeBtn">تجزیہ کریں</button><button id="clearBtn" class="secondary">صاف کریں</button></div>
    <div id="status" class="status"></div>
    <section id="resultBox" class="result hidden"><div class="resultHead"><h2 id="resultTitle">تجزیہ</h2><button id="copyBtn" class="secondary small">کاپی</button></div><pre id="result"></pre></section>
    <p id="privacy" class="privacy">پاس ورڈ، OTP، بینک تفصیلات یا شناختی نمبر پیسٹ نہ کریں۔</p>
  </section></main>
<script>
const text={
ur:{dir:"rtl",title:"ای میل اینالائزر",intro:"ای میل کا مکمل متن پیسٹ کریں۔ یہ ٹول اسی ویب سائٹ پر سمری، ضروری ایکشن، خطرات اور متعلقہ عالمی لنکس دکھائے گا۔",label:"ای میل کا متن",ph:"ای میل یہاں پیسٹ کریں...",analyze:"تجزیہ کریں",clear:"صاف کریں",working:"تجزیہ اور ویب تصدیق جاری ہے...",result:"تجزیہ",copy:"کاپی",copied:"کاپی ہوگیا",privacy:"پاس ورڈ، OTP، بینک تفصیلات یا شناختی نمبر پیسٹ نہ کریں۔",empty:"براہِ کرم ای میل کا متن پیسٹ کریں۔"},
en:{dir:"ltr",title:"Email Analyzer",intro:"Paste the complete email. This tool shows the summary, required actions, risks, and relevant global links on this website.",label:"Email text",ph:"Paste the email here...",analyze:"Analyze",clear:"Clear",working:"Analyzing and checking public information...",result:"Analysis",copy:"Copy",copied:"Copied",privacy:"Do not paste passwords, OTPs, bank details, or identity numbers.",empty:"Please paste the email text."},
ar:{dir:"rtl",title:"محلل البريد الإلكتروني",intro:"ألصق نص البريد الكامل. تعرض الأداة الملخص والإجراءات المطلوبة والمخاطر والروابط العالمية على نفس الموقع.",label:"نص البريد الإلكتروني",ph:"ألصق البريد هنا...",analyze:"تحليل",clear:"مسح",working:"جارٍ التحليل والتحقق من المعلومات العامة...",result:"التحليل",copy:"نسخ",copied:"تم النسخ",privacy:"لا تلصق كلمات المرور أو رموز OTP أو بيانات البنك أو أرقام الهوية.",empty:"يرجى لصق نص البريد الإلكتروني."}}
const $=id=>document.getElementById(id);
function applyLang(){const l=$("language").value,t=text[l];document.documentElement.lang=l;document.documentElement.dir=t.dir;$("title").textContent=t.title;$("intro").textContent=t.intro;$("emailLabel").textContent=t.label;$("emailText").placeholder=t.ph;$("analyzeBtn").textContent=t.analyze;$("clearBtn").textContent=t.clear;$("resultTitle").textContent=t.result;$("copyBtn").textContent=t.copy;$("privacy").textContent=t.privacy}
$("language").addEventListener("change",applyLang);
$("clearBtn").onclick=()=>{$("emailText").value="";$("resultBox").classList.add("hidden");$("status").textContent=""};
$("copyBtn").onclick=async()=>{await navigator.clipboard.writeText($("result").textContent);$("copyBtn").textContent=text[$("language").value].copied};
$("analyzeBtn").onclick=async()=>{const email_text=$("emailText").value.trim(),language=$("language").value,t=text[language];if(!email_text){$("status").textContent=t.empty;$("status").className="status error";return}$("analyzeBtn").disabled=true;$("status").className="status";$("status").textContent=t.working;$("resultBox").classList.add("hidden");try{const r=await fetch("/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email_text,language})});const d=await r.json();if(!r.ok)throw new Error(d.error||"Request failed");$("result").textContent=d.result;$("resultBox").classList.remove("hidden");$("status").textContent=""}catch(e){$("status").className="status error";$("status").textContent=e.message}finally{$("analyzeBtn").disabled=false}};
applyLang();
</script>
</body></html>'''

@app.get("/")
def home():
    return render_template_string(HTML)

@app.get("/health")
def health():
    return {"status": "ok"}

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
        return jsonify({"error": "GEMINI_API_KEY is not configured on Render."}), 500
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
9. If a product or service is discussed: official website, global sellers or suppliers, Saudi Arabia availability when relevant, alternatives, and competitors
10. Clearly separate claims inside the email, independently verified public facts, and assumptions or uncertain points

Do not guess. Do not reveal private information unnecessarily. Warn the user before following payment, password-reset, login, attachment, or unknown-domain links.
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
        return jsonify({"result": response.text or "No analysis was returned."})
    except Exception as exc:
        return jsonify({"error": f"Analysis failed: {str(exc)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
