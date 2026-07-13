import json
import os
import re
from difflib import SequenceMatcher
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
:root{
  --primary:#6d28d9;--primary2:#4f46e5;--bg:#f4f6fb;--card:#fff;
  --text:#172033;--muted:#667085;--line:#e5e7eb;--success:#16a34a;
  --warning:#d97706;--danger:#dc2626;--shadow:0 12px 34px rgba(31,41,55,.09)
}
*{box-sizing:border-box}
body{margin:0;font-family:Arial,sans-serif;background:var(--bg);color:var(--text)}
.hero{background:linear-gradient(135deg,#11184b,#32106d);color:#fff;padding:20px 0;position:sticky;top:0;z-index:20}
.hero-inner{max-width:1180px;margin:auto;padding:0 20px;display:flex;justify-content:space-between;align-items:center;gap:16px}
.brand{display:flex;align-items:center;gap:14px}
.logo{width:48px;height:48px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,#3b82f6,#8b5cf6);font-size:24px}
.brand h1{margin:0;font-size:22px}.brand p{margin:4px 0 0;color:#dbeafe;font-size:13px}
.btn{border:0;border-radius:11px;padding:11px 16px;font-weight:700;cursor:pointer}
.btn-primary{background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff}
.btn-light{background:#fff;color:#111827}.btn-soft{background:#eef2ff;color:#4338ca}
.container{max-width:1180px;margin:28px auto;padding:0 20px 50px}
.card,.meta-strip,.sidebar-card,.report-card{background:#fff;border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow)}
.card{padding:24px}.head{display:flex;justify-content:space-between;align-items:start;gap:16px}.head h2{margin:0}.head p{color:var(--muted)}
select,textarea{font:inherit}select{padding:10px;border:1px solid var(--line);border-radius:10px}
textarea{width:100%;min-height:230px;margin-top:16px;padding:16px;border:1px solid #d1d5db;border-radius:14px;resize:vertical;line-height:1.6}
textarea:focus{outline:3px solid #ddd6fe;border-color:#7c3aed}
.actions{display:flex;gap:10px;margin-top:14px}.status{min-height:24px;margin-top:12px;color:#4f46e5;font-weight:700}.status.error{color:var(--danger)}
.paste-info{margin-top:10px;padding:10px 12px;border-radius:10px;background:#f0fdf4;color:#166534;font-size:13px;display:none}
.hidden{display:none!important}
.meta-strip{margin-top:22px;padding:18px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.meta-box{padding:14px;border-radius:14px;background:#fafbff}.meta-label{font-size:11px;text-transform:uppercase;color:var(--muted);font-weight:800}.meta-value{font-weight:900;margin-top:5px;word-break:break-word}
.layout{display:grid;grid-template-columns:280px 1fr;gap:20px;margin-top:20px;align-items:start}
.sidebar{position:sticky;top:112px;display:grid;gap:16px}.sidebar-card{padding:18px}.sidebar-card h3{margin:0 0 14px;color:#6d28d9}
.toc a{display:flex;gap:9px;align-items:center;padding:8px;text-decoration:none;color:#334155;border-radius:8px}.toc a:hover{background:#f3f0ff;color:#6d28d9}
.num{width:22px;height:22px;border-radius:7px;display:grid;place-items:center;background:#7c3aed;color:#fff;font-size:11px;font-weight:800}
.report{display:grid;gap:16px}.report-card{padding:20px}.section-title{display:flex;gap:10px;align-items:center;padding-bottom:12px;border-bottom:1px solid var(--line);margin-bottom:14px}.section-title h2{margin:0;font-size:19px}
.badge{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;font-weight:800}
.section-body{line-height:1.75;color:#344054}
.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.fact{padding:14px;border:1px solid var(--line);border-radius:14px;text-align:center}.fact .label{font-size:12px;color:var(--muted);font-weight:700}.fact .value{font-size:17px;font-weight:900;margin-top:6px}
.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:14px}table{width:100%;border-collapse:collapse;min-width:900px}th,td{padding:12px;border-bottom:1px solid var(--line);text-align:start;font-size:13px}th{background:#f8f7ff;color:#4338ca}
.click-link{color:#1d4ed8;text-decoration:none;font-weight:800}.click-link:hover{text-decoration:underline}
.open-btn{display:inline-block;background:#7c3aed;color:#fff!important;text-decoration:none;padding:7px 10px;border-radius:8px;font-size:12px;font-weight:800}
.link-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.link-card{padding:13px;border:1px solid var(--line);border-radius:12px;color:#1d4ed8;text-decoration:none;font-weight:800}.link-card small{display:block;color:var(--muted);font-weight:400;margin-top:5px}
.actions-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.action{padding:14px;border:1px solid var(--line);border-radius:14px}.action strong{display:block;color:#4338ca;margin-bottom:5px}
.notice{padding:12px 14px;border-radius:12px;background:#fff7ed;color:#9a3412;border:1px solid #fed7aa;margin-top:12px;font-size:13px}
@media(max-width:900px){.layout{grid-template-columns:1fr}.sidebar{position:static;grid-template-columns:1fr 1fr}.meta-strip,.facts{grid-template-columns:1fr 1fr}}
@media(max-width:620px){.hero-inner,.head{flex-direction:column}.meta-strip,.facts,.sidebar,.link-grid,.actions-grid{grid-template-columns:1fr}.container{padding:0 12px 30px}}
@media print{.hero,.card,.status,.paste-info{display:none!important}.layout{grid-template-columns:240px 1fr}.sidebar{position:static}.report-card,.sidebar-card,.meta-strip{box-shadow:none}}
</style>
</head>
<body>
<header class="hero">
  <div class="hero-inner">
    <div class="brand"><div class="logo">✉</div><div><h1>AI EMAIL ANALYZER</h1><p>Fast professional analysis with smart clickable links</p></div></div>
    <div><button class="btn btn-light" id="newBtn">＋ New Analysis</button> <button class="btn btn-primary" id="printBtn">⬇ Download Report</button></div>
  </div>
</header>

<main class="container">
<section class="card">
  <div class="head">
    <div><h2>Analyze an Email</h2><p>Copy the complete email directly from Gmail or Outlook and paste it below.</p></div>
    <select id="language"><option value="en">English</option><option value="ur">اردو</option><option value="ar">العربية</option></select>
  </div>
  <textarea id="emailText" placeholder="Paste the complete email here..."></textarea>
  <div class="paste-info" id="pasteInfo"></div>
  <div class="notice">For clickable article or job links, copy directly from Gmail/Outlook. Pasting through Notepad removes hidden links.</div>
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
        <a href="#summary"><span class="num">1</span>Summary</a>
        <a href="#about"><span class="num">2</span>About</a>
        <a href="#facts"><span class="num">3</span>Key Information</a>
        <a href="#items"><span class="num">4</span>Clickable Items</a>
        <a href="#actions"><span class="num">5</span>Actions</a>
        <a href="#links"><span class="num">6</span>All Links</a>
      </nav></section>
      <section class="sidebar-card"><h3>LINK STATUS</h3><div id="linkStatus" class="section-body">—</div></section>
    </aside>

    <section class="report">
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
let pastedHtml="";
let capturedLinks=[];

function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}
function validUrl(u){try{const x=new URL(u);return x.protocol==="http:"||x.protocol==="https:"}catch{return false}}
function linkify(value,url){
  const text=esc(value||"—");
  return validUrl(url)?`<a class="click-link" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${text}</a>`:text;
}

$("emailText").addEventListener("paste",e=>{
  const html=e.clipboardData?.getData("text/html")||"";
  if(html){
    pastedHtml=html;
    const doc=new DOMParser().parseFromString(html,"text/html");
    capturedLinks=[...doc.querySelectorAll("a[href]")].map(a=>({text:(a.textContent||"").trim(),url:a.href})).filter(x=>validUrl(x.url));
    $("pasteInfo").style.display="block";
    $("pasteInfo").textContent=`Captured ${capturedLinks.length} link(s). The server will automatically keep only relevant links.`;
  }else{
    pastedHtml="";
    capturedLinks=[];
    $("pasteInfo").style.display="block";
    $("pasteInfo").textContent="No hidden hyperlinks were found. Visible URLs can still be used.";
  }
});

function renderFacts(arr){
  $("factsGrid").innerHTML="";
  (arr?.length?arr:[{label:"Information",value:"Not provided"}]).forEach(x=>{
    const d=document.createElement("div");d.className="fact";
    d.innerHTML=`<div class="label">${esc(x.label)}</div><div class="value">${linkify(x.value,x.url)}</div>`;
    $("factsGrid").appendChild(d);
  });
}

function renderItems(items){
  const area=$("itemsArea");area.innerHTML="";
  if(!items?.length){area.innerHTML='<div class="section-body">No structured items found.</div>';return}
  const keys=["title","company","author","type","location","price_or_salary","status"];
  let h='<div class="table-wrap"><table><thead><tr>';
  keys.forEach(k=>h+=`<th>${esc(k.replaceAll("_"," "))}</th>`);
  h+='<th>Open</th></tr></thead><tbody>';
  items.forEach(it=>{
    const url=it.url||"";
    h+="<tr>";
    keys.forEach(k=>h+=`<td>${linkify(it[k],url)}</td>`);
    h+=`<td>${validUrl(url)?`<a class="open-btn" href="${esc(url)}" target="_blank" rel="noopener noreferrer">Open ↗</a>`:"Not available"}</td></tr>`;
  });
  h+="</tbody></table></div>";area.innerHTML=h;
}

function renderLinks(links){
  $("linksGrid").innerHTML="";
  const good=(links||[]).filter(x=>validUrl(x.url));
  $("linkStatus").textContent=`${good.length} relevant clickable link(s) are available.`;
  if(!good.length){$("linksGrid").innerHTML='<div class="section-body">No clickable links were available.</div>';return}
  good.forEach(l=>{
    const a=document.createElement("a");a.className="link-card";a.href=l.url;a.target="_blank";a.rel="noopener noreferrer";
    a.innerHTML=`${esc(l.title||l.text||"Open link")}<small>${esc(l.description||l.url)}</small>`;
    $("linksGrid").appendChild(a);
  });
}

function renderActions(arr){
  $("actionsGrid").innerHTML="";
  (arr||[]).forEach(a=>{
    const d=document.createElement("div");d.className="action";
    d.innerHTML=`<strong>${linkify(a.title,a.url)}</strong><span>${linkify(a.detail,a.url)}</span>`;
    $("actionsGrid").appendChild(d);
  });
}

$("analyzeBtn").onclick=async()=>{
  const email_text=$("emailText").value.trim();
  if(!email_text){$("status").className="status error";$("status").textContent="Please paste the email first.";return}
  $("analyzeBtn").disabled=true;$("status").className="status";$("status").textContent="Analyzing email and matching relevant links. This may take up to one minute...";
  try{
    const r=await fetch("/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
      email_text,
      email_html:pastedHtml,
      captured_links:capturedLinks,
      language:$("language").value
    })});
    const raw=await r.text();
    let d;
    try{d=JSON.parse(raw)}catch{throw new Error("The server returned an invalid response. Please retry after a few seconds.")}
    if(!r.ok)throw new Error(d.error||"Analysis failed");
    const m=d.metadata||{};
    $("mSubject").textContent=m.subject||"—";$("mDate").textContent=m.date||"—";$("mSender").textContent=m.sender||"—";$("mImportance").textContent=m.importance||"—";
    $("summaryText").textContent=d.short_summary||"—";$("aboutText").textContent=d.what_email_is_about||"—";
    renderFacts(d.key_information);renderItems(d.items);renderActions(d.recommended_actions);renderLinks(d.links);
    $("reportRoot").classList.remove("hidden");$("status").textContent="";
    $("reportRoot").scrollIntoView({behavior:"smooth"});
  }catch(e){$("status").className="status error";$("status").textContent=e.message}
  finally{$("analyzeBtn").disabled=false}
};

$("clearBtn").onclick=$("newBtn").onclick=()=>location.reload();
$("printBtn").onclick=()=>window.print();
</script>
</body>
</html>
"""

STOP_WORDS = {
    "unsubscribe","privacy","terms","help center","preferences","settings",
    "app store","google play","download the app","view in browser","manage email",
    "weekly digest","careers","cookie","tracking","pixel","facebook","twitter",
    "instagram","linkedin","medium.com/me","notifications"
}

def clean_url(url: str) -> str:
    url = (url or "").strip()
    try:
        p = urlparse(url)
        return url if p.scheme in ("http","https") and p.netloc else ""
    except Exception:
        return ""

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

def is_irrelevant(text: str, url: str) -> bool:
    joined = f"{text} {url}".lower()
    return any(word in joined for word in STOP_WORDS)

def visible_urls_from_text(text: str):
    found = re.findall(r'https?://[^\s<>"\']+', text or "")
    return [{"text": u, "url": u} for u in found]

def parse_relevant_links(html: str, frontend_links):
    candidates = []
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            text = " ".join(a.get_text(" ", strip=True).split())
            url = clean_url(a.get("href"))
            if url:
                candidates.append({"text": text or url, "url": url})
    for x in frontend_links or []:
        url = clean_url(x.get("url"))
        if url:
            candidates.append({"text": (x.get("text") or url).strip(), "url": url})

    dedup = []
    seen = set()
    for x in candidates:
        if x["url"] in seen or is_irrelevant(x["text"], x["url"]):
            continue
        seen.add(x["url"])
        dedup.append(x)

    # Prefer links with useful anchor text, then cap to prevent timeout/OOM.
    dedup.sort(key=lambda x: (len(normalize(x["text"])) < 6, len(x["url"]) > 500, -len(x["text"])))
    return dedup[:35]

def extract_json(text: str):
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        m = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not m:
            raise ValueError("Gemini did not return valid JSON.")
        return json.loads(m.group(0))

def similarity(a: str, b: str) -> float:
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return 0.0
    seq = SequenceMatcher(None, na, nb).ratio()
    sa, sb = set(na.split()), set(nb.split())
    overlap = len(sa & sb) / max(1, len(sa | sb))
    contains = 1.0 if na in nb or nb in na else 0.0
    return max(seq, overlap, contains)

def best_link_for_item(item, links):
    fields = [item.get("title",""), item.get("company",""), item.get("author","")]
    best, score = "", 0.0
    for link in links:
        for field in fields:
            s = similarity(field, link["text"])
            if s > score:
                score, best = s, link["url"]
    return best if score >= 0.48 else ""

@app.get("/")
def home():
    return render_template_string(HTML)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    email_text = (payload.get("email_text") or "").strip()
    email_html = payload.get("email_html") or ""
    language = LANGUAGES.get(payload.get("language"), "English")

    if not email_text:
        return jsonify({"error":"Please paste the email text."}),400
    if len(email_text) > 40000:
        email_text = email_text[:40000]

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error":"GEMINI_API_KEY is not configured."}),500

    links = parse_relevant_links(email_html, payload.get("captured_links") or [])
    for x in visible_urls_from_text(email_text):
        if x["url"] not in {l["url"] for l in links} and not is_irrelevant(x["text"], x["url"]):
            links.append(x)
    links = links[:35]

    prompt = f"""
Analyze the email below and answer in {language}.
Return ONLY valid JSON. No markdown or code fences.

Use this structure:
{{
  "metadata": {{"subject":"","sender":"","date":"","importance":"Low, Medium, or High"}},
  "short_summary":"",
  "what_email_is_about":"",
  "key_information":[{{"label":"","value":"","url":""}}],
  "items":[{{"title":"","company":"","author":"","type":"","location":"","price_or_salary":"","status":"","url":""}}],
  "recommended_actions":[{{"title":"","detail":"","url":""}}],
  "links":[{{"title":"","url":"","description":""}}]
}}

Rules:
- Extract every meaningful article, job, product, service, offer, or event as an item.
- Use only URLs from the provided extracted-links list.
- Match an item's title/author/company to the best URL.
- Do not invent URLs.
- Keep summary concise.
- Maximum 20 items.
- Maximum 8 key information cards.
- Maximum 8 recommended actions.

EMAIL:
{email_text}

RELEVANT LINKS EXTRACTED DIRECTLY FROM EMAIL:
{json.dumps(links, ensure_ascii=False)}
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL","gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1)
        )
        result = extract_json(response.text)

        # Deterministic URL matching after Gemini response.
        for item in result.get("items") or []:
            current = clean_url(item.get("url"))
            if not current:
                item["url"] = best_link_for_item(item, links)

        # Ensure every relevant extracted link appears in the link section.
        output_links = result.get("links") or []
        existing = {clean_url(x.get("url")) for x in output_links if isinstance(x,dict)}
        for link in links:
            if link["url"] not in existing:
                output_links.append({
                    "title": link["text"] or "Open email link",
                    "url": link["url"],
                    "description": "Link extracted directly from the pasted email"
                })
        result["links"] = output_links[:40]
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error":f"Analysis failed: {exc}"}),500

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
