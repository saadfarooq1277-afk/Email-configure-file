import json
import os
import re
from html import unescape
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template_string, request
from google import genai
from google.genai import types

app = Flask(__name__)

LANGUAGES = {"ur": "Urdu", "en": "English", "ar": "Arabic"}

HTML = r"""
<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Email Analyzer</title>
<style>
:root{--primary:#6d28d9;--primary2:#4f46e5;--bg:#f4f6fb;--card:#fff;--text:#172033;--muted:#667085;--line:#e5e7eb;--success:#16a34a;--danger:#dc2626;--shadow:0 12px 34px rgba(31,41,55,.09)}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font-family:Arial,sans-serif;background:var(--bg);color:var(--text)}
.hero{background:linear-gradient(135deg,#11184b,#32106d);color:#fff;padding:20px 0;position:sticky;top:0;z-index:20}
.hero-inner{max-width:1180px;margin:auto;padding:0 20px;display:flex;justify-content:space-between;align-items:center;gap:16px}
.brand{display:flex;align-items:center;gap:14px}.logo{width:48px;height:48px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,#3b82f6,#8b5cf6);font-size:24px}
.brand h1{margin:0;font-size:22px}.brand p{margin:4px 0 0;color:#dbeafe;font-size:13px}
.btn{border:0;border-radius:11px;padding:11px 16px;font-weight:700;cursor:pointer}.btn-primary{background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff}.btn-light{background:#fff;color:#111827}.btn-soft{background:#eef2ff;color:#4338ca}
.container{max-width:1180px;margin:28px auto;padding:0 20px 50px}
.card,.meta-strip,.sidebar-card,.report-card{background:#fff;border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow)}
.card{padding:24px}.head{display:flex;justify-content:space-between;align-items:start;gap:16px}.head h2{margin:0}.head p{color:var(--muted)}
select,textarea{font:inherit}select{padding:10px;border:1px solid var(--line);border-radius:10px}
textarea{width:100%;min-height:230px;margin-top:16px;padding:16px;border:1px solid #d1d5db;border-radius:14px;resize:vertical;line-height:1.6}
textarea:focus{outline:3px solid #ddd6fe;border-color:#7c3aed}
.actions{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap}.status{min-height:24px;margin-top:12px;color:#4f46e5;font-weight:700}.status.error{color:var(--danger)}
.paste-info{margin-top:10px;padding:10px 12px;border-radius:10px;background:#f0fdf4;color:#166534;font-size:13px;display:none}.hidden{display:none!important}
.meta-strip{margin-top:22px;padding:18px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.meta-box{padding:14px;border-radius:14px;background:#fafbff}.meta-label{font-size:11px;text-transform:uppercase;color:var(--muted);font-weight:800}.meta-value{font-weight:900;margin-top:5px;word-break:break-word}
.layout{display:grid;grid-template-columns:280px 1fr;gap:20px;margin-top:20px;align-items:start}.sidebar{position:sticky;top:112px;display:grid;gap:16px}.sidebar-card{padding:18px}.sidebar-card h3{margin:0 0 14px;color:#6d28d9}
.toc a{display:flex;gap:9px;align-items:center;padding:8px;text-decoration:none;color:#334155;border-radius:8px}.toc a:hover{background:#f3f0ff;color:#6d28d9}.num{width:22px;height:22px;border-radius:7px;display:grid;place-items:center;background:#7c3aed;color:#fff;font-size:11px;font-weight:800}
.report{display:grid;gap:16px}.report-card{padding:20px}.section-title{display:flex;gap:10px;align-items:center;padding-bottom:12px;border-bottom:1px solid var(--line);margin-bottom:14px}.section-title h2{margin:0;font-size:19px}.badge{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;font-weight:800}
.section-body{line-height:1.75;color:#344054}.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.fact{padding:14px;border:1px solid var(--line);border-radius:14px;text-align:center}.fact .label{font-size:12px;color:var(--muted);font-weight:700}.fact .value{font-size:17px;font-weight:900;margin-top:6px}
.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:14px}table{width:100%;border-collapse:collapse;min-width:760px}th,td{padding:12px;border-bottom:1px solid var(--line);text-align:start;font-size:13px}th{background:#f8f7ff;color:#4338ca}
.click-link{color:#1d4ed8;text-decoration:none;font-weight:800}.click-link:hover{text-decoration:underline}.open-btn{display:inline-block;background:#7c3aed;color:#fff!important;text-decoration:none;padding:7px 10px;border-radius:8px;font-size:12px;font-weight:800}
.link-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.link-card{padding:13px;border:1px solid var(--line);border-radius:12px;color:#1d4ed8;text-decoration:none;font-weight:800}.link-card small{display:block;color:var(--muted);font-weight:400;margin-top:5px;word-break:break-all}
.actions-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.action{padding:14px;border:1px solid var(--line);border-radius:14px}.action strong{display:block;color:#4338ca;margin-bottom:5px}
.fallback{background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;padding:11px 13px;border-radius:11px;margin-bottom:14px;display:none}
@media(max-width:900px){.layout{grid-template-columns:1fr}.sidebar{position:static;grid-template-columns:1fr 1fr}.meta-strip,.facts{grid-template-columns:1fr 1fr}}
@media(max-width:620px){.hero-inner,.head{flex-direction:column}.meta-strip,.facts,.sidebar,.link-grid,.actions-grid{grid-template-columns:1fr}.container{padding:0 12px 30px}}
@media print{.hero,.card,.status,.paste-info{display:none!important}.layout{grid-template-columns:240px 1fr}.sidebar{position:static}.report-card,.sidebar-card,.meta-strip{box-shadow:none}}
</style>
</head>
<body>
<header class="hero"><div class="hero-inner">
<div class="brand"><div class="logo">✉</div><div><h1>AI EMAIL ANALYZER</h1><p>Professional structured report with clickable links</p></div></div>
<div><button class="btn btn-light" id="newBtn">＋ New Analysis</button> <button class="btn btn-primary" id="printBtn">⬇ Download Report</button></div>
</div></header>

<main class="container">
<section class="card">
<div class="head"><div><h2>Analyze an Email</h2><p>Copy directly from Gmail or Outlook. The app captures and preserves hidden links.</p></div>
<select id="language"><option value="en">English</option><option value="ur">اردو</option><option value="ar">العربية</option></select></div>
<textarea id="emailText" placeholder="Paste the complete email here..."></textarea>
<div class="paste-info" id="pasteInfo"></div>
<div class="actions"><button class="btn btn-primary" id="analyzeBtn">Analyze Email</button><button class="btn btn-soft" id="clearBtn">Clear</button></div>
<div id="status" class="status"></div>
</section>

<section id="reportRoot" class="hidden">
<div class="meta-strip">
<div class="meta-box"><div class="meta-label">Subject</div><div class="meta-value" id="mSubject">—</div></div>
<div class="meta-box"><div class="meta-label">Date</div><div class="meta-value" id="mDate">—</div></div>
<div class="meta-box"><div class="meta-label">Sender</div><div class="meta-value" id="mSender">—</div></div>
<div class="meta-box"><div class="meta-label">Importance</div><div class="meta-value" id="mImportance">—</div></div>
</div>

<div class="layout">
<aside class="sidebar">
<section class="sidebar-card"><h3>TABLE OF CONTENTS</h3><nav class="toc">
<a href="#summary"><span class="num">1</span>Summary</a><a href="#about"><span class="num">2</span>About</a>
<a href="#facts"><span class="num">3</span>Key Information</a><a href="#items"><span class="num">4</span>Clickable Items</a>
<a href="#actions"><span class="num">5</span>Actions</a><a href="#links"><span class="num">6</span>All Links</a>
</nav></section>
<section class="sidebar-card"><h3>LINK STATUS</h3><div id="linkStatus" class="section-body">—</div></section>
</aside>

<section class="report">
<div class="fallback" id="fallbackNote">A complete local summary was generated because the AI enhancement was unavailable.</div>
<article class="report-card" id="summary"><div class="section-title"><span class="badge">1</span><h2>Short Summary</h2></div><div class="section-body" id="summaryText"></div></article>
<article class="report-card" id="about"><div class="section-title"><span class="badge">2</span><h2>What the Email Is About</h2></div><div class="section-body" id="aboutText"></div></article>
<article class="report-card" id="facts"><div class="section-title"><span class="badge">3</span><h2>Key Information</h2></div><div class="facts" id="factsGrid"></div></article>
<article class="report-card" id="items"><div class="section-title"><span class="badge">4</span><h2>Clickable Articles / Jobs / Products</h2></div><div id="itemsArea"></div></article>
<article class="report-card" id="actions"><div class="section-title"><span class="badge">5</span><h2>Recommended Actions</h2></div><div class="actions-grid" id="actionsGrid"></div></article>
<article class="report-card" id="links"><div class="section-title"><span class="badge">6</span><h2>All Available Links</h2></div><div class="link-grid" id="linksGrid"></div></article>
</section>
</div>
</section>
</main>

<script>
const $=id=>document.getElementById(id);
let pastedHtml="", capturedLinks=[];
function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}
function validUrl(u){try{let x=new URL(u);return x.protocol==="http:"||x.protocol==="https:"}catch{return false}}
function linkify(v,u){return validUrl(u)?`<a class="click-link" href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(v||"Open")}</a>`:esc(v||"—")}

$("emailText").addEventListener("paste",e=>{
 const html=e.clipboardData?.getData("text/html")||"";
 pastedHtml=html;
 if(html){
  const doc=new DOMParser().parseFromString(html,"text/html");
  capturedLinks=[...doc.querySelectorAll("a[href]")].map(a=>({text:(a.textContent||"").trim(),url:a.href})).filter(x=>validUrl(x.url));
  $("pasteInfo").style.display="block";$("pasteInfo").textContent=`Captured ${capturedLinks.length} hidden link(s) from the email.`;
 }else{
  capturedLinks=[];$("pasteInfo").style.display="block";$("pasteInfo").textContent="No hidden hyperlinks were found. Visible URLs will still be detected.";
 }
});

function renderFacts(a){$("factsGrid").innerHTML="";(a?.length?a:[{label:"Information",value:"Not provided"}]).forEach(x=>{let d=document.createElement("div");d.className="fact";d.innerHTML=`<div class="label">${esc(x.label)}</div><div class="value">${linkify(x.value,x.url)}</div>`;$("factsGrid").appendChild(d)})}
function renderItems(a){
 $("itemsArea").innerHTML="";
 if(!a?.length){$("itemsArea").innerHTML='<div class="section-body">No article, job, product, or offer links were found.</div>';return}
 let h='<div class="table-wrap"><table><thead><tr><th>Title</th><th>Category</th><th>Source</th><th>Open</th></tr></thead><tbody>';
 a.forEach(x=>{h+=`<tr><td>${linkify(x.title,x.url)}</td><td>${linkify(x.category,x.url)}</td><td>${linkify(x.source,x.url)}</td><td>${validUrl(x.url)?`<a class="open-btn" href="${esc(x.url)}" target="_blank" rel="noopener noreferrer">Open ↗</a>`:"Not available"}</td></tr>`});
 h+="</tbody></table></div>";$("itemsArea").innerHTML=h;
}
function renderActions(a){$("actionsGrid").innerHTML="";(a||[]).forEach(x=>{let d=document.createElement("div");d.className="action";d.innerHTML=`<strong>${esc(x.title)}</strong><span>${esc(x.detail)}</span>`;$("actionsGrid").appendChild(d)})}
function renderLinks(a){$("linksGrid").innerHTML="";let good=(a||[]).filter(x=>validUrl(x.url));$("linkStatus").textContent=`${good.length} clickable link(s) available.`;if(!good.length){$("linksGrid").innerHTML='<div class="section-body">No clickable links found.</div>';return}good.forEach(x=>{let el=document.createElement("a");el.className="link-card";el.href=x.url;el.target="_blank";el.rel="noopener noreferrer";el.innerHTML=`${esc(x.title||"Open link")}<small>${esc(x.url)}</small>`;$("linksGrid").appendChild(el)})}

$("analyzeBtn").onclick=async()=>{
 let email_text=$("emailText").value.trim();
 if(!email_text){$("status").className="status error";$("status").textContent="Please paste the email first.";return}
 $("analyzeBtn").disabled=true;$("status").className="status";$("status").textContent="Analyzing…";
 try{
  let r=await fetch("/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email_text,email_html:pastedHtml,captured_links:capturedLinks,language:$("language").value})});
  let raw=await r.text(),d;try{d=JSON.parse(raw)}catch{throw new Error("Server response was interrupted. Please retry.")}
  if(!r.ok)throw new Error(d.error||"Analysis failed");
  let m=d.metadata||{};$("mSubject").textContent=m.subject||"—";$("mDate").textContent=m.date||"—";$("mSender").textContent=m.sender||"—";$("mImportance").textContent=m.importance||"—";
  $("summaryText").textContent=d.short_summary||"—";$("aboutText").textContent=d.what_email_is_about||"—";
  $("fallbackNote").style.display=d.ai_fallback?"block":"none";
  renderFacts(d.key_information);renderItems(d.items);renderActions(d.recommended_actions);renderLinks(d.links);
  $("reportRoot").classList.remove("hidden");$("status").textContent="";$("reportRoot").scrollIntoView({behavior:"smooth"});
 }catch(e){$("status").className="status error";$("status").textContent=e.message}
 finally{$("analyzeBtn").disabled=false}
};
$("clearBtn").onclick=$("newBtn").onclick=()=>location.reload();$("printBtn").onclick=()=>window.print();
</script>
</body>
</html>
"""

IGNORE = (
    "unsubscribe","privacy","terms","help","preferences","settings","app store",
    "google play","view in browser","manage email","cookie","tracking","pixel",
    "facebook","twitter","instagram","linkedin","download app"
)

def valid_url(url):
    try:
        p=urlparse((url or "").strip())
        return (url or "").strip() if p.scheme in ("http","https") and p.netloc else ""
    except Exception:
        return ""

def clean_text(s):
    return " ".join(unescape(s or "").split()).strip()

def irrelevant(text,url):
    s=f"{text} {url}".lower()
    return any(x in s for x in IGNORE)

def classify(text,url):
    s=f"{text} {url}".lower()
    if any(x in s for x in ("job","career","apply","vacancy","position")): return "Job"
    if any(x in s for x in ("article","read","story","post","medium.com")): return "Article"
    if any(x in s for x in ("product","shop","buy","price","store")): return "Product"
    if any(x in s for x in ("event","register","webinar","meeting")): return "Event"
    return "Link"

def source_name(url):
    try:
        host=urlparse(url).netloc.lower().replace("www.","")
        return host
    except Exception:
        return "Website"

def extract_links(html,frontend,text):
    candidates=[]
    if html:
        soup=BeautifulSoup(html,"html.parser")
        for a in soup.find_all("a",href=True):
            u=valid_url(a.get("href")); t=clean_text(a.get_text(" ",strip=True))
            if u:candidates.append((t or u,u))
    for x in frontend or []:
        u=valid_url(x.get("url"));t=clean_text(x.get("text"))
        if u:candidates.append((t or u,u))
    for u in re.findall(r'https?://[^\s<>"\']+',text or ""):
        candidates.append((u,u))
    out=[];seen=set()
    for t,u in candidates:
        if u in seen or irrelevant(t,u):continue
        seen.add(u)
        # Avoid meaningless empty/tracking anchors.
        if len(t)<3 and len(u)>350:continue
        out.append({"title":t[:180] or source_name(u),"url":u,"category":classify(t,u),"source":source_name(u)})
    return out[:50]

def local_metadata(text):
    lines=[clean_text(x) for x in (text or "").splitlines() if clean_text(x)]
    subject="Not provided";sender="Not provided";date="Not provided"
    for line in lines[:40]:
        low=line.lower()
        if low.startswith("subject:"):subject=line.split(":",1)[1].strip()
        elif low.startswith("from:"):sender=line.split(":",1)[1].strip()
        elif low.startswith("date:") or low.startswith("sent:"):date=line.split(":",1)[1].strip()
    if subject=="Not provided" and lines:subject=lines[0][:160]
    return {"subject":subject,"sender":sender,"date":date,"importance":"Medium"}

def important_sentences(text, limit=7):
    raw = re.split(r'(?<=[.!?])\s+|\n+', text or "")
    out = []
    blocked = ("unsubscribe", "privacy policy", "terms of service", "download the app", "sent by")
    for sentence in raw:
        sentence = clean_text(sentence)
        if len(sentence) < 25 or any(x in sentence.lower() for x in blocked):
            continue
        if sentence not in out:
            out.append(sentence)
        if len(out) >= limit:
            break
    return out


def fallback_report(text, links, lang):
    metadata = local_metadata(text)
    count = len(links)
    points = important_sentences(text, 7)
    first = points[0] if points else "The email contains information that should be reviewed."
    second = points[1] if len(points) > 1 else first
    if lang == "Urdu":
        summary = f"یہ ای میل بنیادی طور پر اس موضوع سے متعلق ہے: {first} اس میں {count} قابلِ کلک متعلقہ لنکس بھی موجود ہیں۔"
        about = f"ای میل میں دی گئی اہم معلومات کا خلاصہ یہ ہے: {second}"
        risks = ["نامعلوم یا غیر متوقع لنکس کھولنے سے پہلے domain چیک کریں۔","Payment، login، password reset یا personal information request کی تصدیق کریں۔"]
        actions = [{"title":"اہم معلومات چیک کریں","detail":"تاریخ، قیمت، تنخواہ، deadline اور sender کی تفصیلات verify کریں۔"},{"title":"متعلقہ لنکس کھولیں","detail":"نیچے موجود article، job، product یا offer links استعمال کریں۔"}]
    elif lang == "Arabic":
        summary = f"يتعلق هذا البريد أساساً بالموضوع التالي: {first} ويحتوي على {count} روابط ذات صلة قابلة للنقر."
        about = f"أهم المعلومات الواردة في البريد: {second}"
        risks = ["تحقق من النطاق قبل فتح الروابط غير المعروفة أو غير المتوقعة.","تحقق من أي طلب للدفع أو تسجيل الدخول أو البيانات الشخصية."]
        actions = [{"title":"مراجعة المعلومات المهمة","detail":"تحقق من التواريخ والأسعار والمواعيد وبيانات المرسل."},{"title":"فتح الروابط ذات الصلة","detail":"استخدم روابط المقالات أو الوظائف أو المنتجات أدناه."}]
    else:
        summary = f"This email is mainly about: {first} It also contains {count} relevant clickable link(s)."
        about = f"The main information communicated in the email is: {second}"
        risks = ["Check the domain before opening unknown or unexpected links.","Verify any payment, login, password-reset, or personal-information request."]
        actions = [{"title":"Review key details","detail":"Verify dates, prices, salaries, deadlines and sender information."},{"title":"Open relevant items","detail":"Use the clickable article, job, product or offer links below."}]
    return {"metadata":metadata,"short_summary":summary,"what_email_is_about":about,"key_information":[{"label":"Email topic","value":first[:90],"url":""},{"label":"Clickable links","value":str(count),"url":""},{"label":"Email length","value":f"{len(text):,} characters","url":""},{"label":"Priority","value":metadata.get("importance","Medium"),"url":""}],"recommended_actions":actions,"risks":risks,"key_points":points[:5] or [first],"ai_fallback":True}


def extract_json(s):
    s=(s or "").strip()
    s=re.sub(r"^```(?:json)?\s*","",s,flags=re.I);s=re.sub(r"\s*```$","",s)
    try:return json.loads(s)
    except Exception:
        m=re.search(r"\{.*\}",s,flags=re.S)
        if not m:raise ValueError("Invalid AI response")
        return json.loads(m.group(0))

@app.get("/")
def home():return render_template_string(HTML)

@app.get("/health")
def health():return {"status":"ok"}

@app.post("/analyze")
def analyze():
    p=request.get_json(silent=True) or {}
    text=(p.get("email_text") or "").strip()
    if not text:return jsonify({"error":"Please paste the email text."}),400
    links=extract_links(p.get("email_html") or "",p.get("captured_links") or [],text)
    lang_code=p.get("language","en");lang=LANGUAGES.get(lang_code,"English")
    base=fallback_report(text,links,lang)
    result=base.copy()

    api=os.environ.get("GEMINI_API_KEY")
    if api:
        # Compact prompt only: no HTML and no URL list. Links are handled locally.
        compact=text[:12000]
        prompt=f"""Return ONLY valid JSON in {lang}.
Analyze this email briefly.
JSON:
{{"metadata":{{"subject":"","sender":"","date":"","importance":"Low, Medium, or High"}},"short_summary":"","what_email_is_about":"","key_information":[{{"label":"","value":"","url":""}}],"recommended_actions":[{{"title":"","detail":""}}]}}
Maximum 6 key_information entries and 5 recommended_actions.
EMAIL:
{compact}"""
        try:
            client=genai.Client(
                api_key=api,
                http_options=types.HttpOptions(timeout=18000)
            )
            response=client.models.generate_content(
                model=os.environ.get("GEMINI_MODEL","gemini-2.5-flash-lite"),
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=1100,
                    response_mime_type="application/json"
                )
            )
            ai=extract_json(response.text)
            for key, value in ai.items():
                if value not in (None, "", [], {}):
                    result[key] = value
            result["ai_fallback"] = False
        except Exception:
            # Deliberately keep local fallback so the app still works.
            pass

    result["items"]=links[:30]
    result["links"]=[{"title":x["title"],"url":x["url"],"description":x["category"]} for x in links]
    return jsonify(result)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
