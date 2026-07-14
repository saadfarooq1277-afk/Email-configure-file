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

LANGUAGES = {"en": "English", "ur": "Urdu", "ar": "Arabic"}

HTML = r"""
<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Enterprise Email Analyzer</title>
<style>
:root{
 --navy:#101847;--purple:#6d28d9;--blue:#2563eb;--bg:#f3f6fb;--card:#fff;
 --text:#172033;--muted:#667085;--line:#e4e9f0;--green:#16a34a;--amber:#d97706;
 --red:#dc2626;--shadow:0 14px 40px rgba(31,41,55,.10)
}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font-family:Arial,sans-serif;background:var(--bg);color:var(--text)}
header{background:linear-gradient(135deg,#0e1744,#28105f 60%,#4c1d95);color:#fff;padding:20px 0;position:sticky;top:0;z-index:20;box-shadow:0 8px 25px rgba(15,23,42,.22)}
.header-inner{max-width:1220px;margin:auto;padding:0 20px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{display:flex;align-items:center;gap:14px}.logo{width:50px;height:50px;border-radius:15px;display:grid;place-items:center;background:linear-gradient(135deg,#3b82f6,#8b5cf6);font-size:25px}
.brand h1{margin:0;font-size:23px}.brand p{margin:4px 0 0;color:#dbeafe;font-size:13px}
.btn{border:0;border-radius:11px;padding:11px 16px;font-weight:800;cursor:pointer}.btn-primary{background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff}.btn-white{background:#fff;color:#111827}.btn-soft{background:#eef2ff;color:#4338ca}
.wrap{max-width:1220px;margin:28px auto;padding:0 20px 50px}
.card,.meta-strip,.sidebar-card,.section-card{background:#fff;border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow)}
.input-card{padding:24px}.input-top{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}
.input-top h2{margin:0;font-size:23px}.input-top p{margin:6px 0 0;color:var(--muted);line-height:1.65}
select{padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#fff;font-weight:700}
textarea{width:100%;min-height:240px;margin-top:17px;padding:16px;border:1px solid #cfd7e2;border-radius:14px;font:inherit;line-height:1.65;resize:vertical;background:#fbfcff}
textarea:focus{outline:3px solid #ddd6fe;border-color:#7c3aed}
.controls{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap}.status{min-height:24px;margin-top:12px;color:#4f46e5;font-weight:800}.status.error{color:var(--red)}
.capture{display:none;margin-top:10px;padding:10px 12px;border-radius:10px;background:#ecfdf3;color:#166534;font-size:13px}
.hidden{display:none!important}
.meta-strip{margin-top:22px;padding:18px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.meta{padding:15px;border-radius:14px;background:linear-gradient(180deg,#fff,#fafbff)}.meta-label{font-size:11px;color:var(--muted);text-transform:uppercase;font-weight:900}.meta-value{font-size:16px;font-weight:900;margin-top:6px;word-break:break-word}
.layout{display:grid;grid-template-columns:285px 1fr;gap:20px;margin-top:20px;align-items:start}.sidebar{position:sticky;top:112px;display:grid;gap:16px}
.sidebar-card{padding:18px}.sidebar-card h3{margin:0 0 14px;color:var(--purple);font-size:15px}.toc a{display:flex;align-items:center;gap:9px;padding:9px 8px;border-radius:9px;text-decoration:none;color:#344054;font-size:13px}.toc a:hover{background:#f3f0ff;color:var(--purple)}
.num{width:23px;height:23px;border-radius:7px;display:grid;place-items:center;background:var(--purple);color:#fff;font-size:11px;font-weight:900}
.overview-row{display:grid;grid-template-columns:76px 1fr;gap:9px;padding:9px 0;border-bottom:1px solid var(--line);font-size:13px}.overview-row:last-child{border-bottom:0}.ov-key{font-weight:900}.ov-value{color:#475467;word-break:break-word}
.report{display:grid;gap:16px}.section-card{padding:20px}.section-title{display:flex;align-items:center;gap:11px;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:14px}.section-title h2{margin:0;font-size:19px}
.badge{width:31px;height:31px;border-radius:9px;display:grid;place-items:center;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;font-weight:900}
.body{line-height:1.8;color:#344054;font-size:15px;white-space:pre-wrap}.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.info{border:1px solid var(--line);border-radius:14px;padding:15px;text-align:center;background:#fbfcff}.info .label{font-size:12px;color:var(--muted);font-weight:800}.info .value{font-size:17px;font-weight:900;margin-top:7px}
.list{list-style:none;margin:0;padding:0;display:grid;gap:10px}.list li{padding:12px 14px;border-radius:12px;background:#f8fafc;border:1px solid #edf0f4;line-height:1.6}.list li::before{content:"✓";color:var(--green);font-weight:900;margin-inline-end:9px}.risks li::before{content:"⚠";color:var(--amber)}
.actions-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.action{padding:15px;border:1px solid var(--line);border-radius:14px;background:#fbfcff}.action strong{display:block;color:#4338ca;margin-bottom:6px}
.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:14px}table{width:100%;border-collapse:collapse;min-width:760px}th,td{padding:12px 13px;text-align:start;border-bottom:1px solid var(--line);font-size:13px}th{background:#f8f7ff;color:#4338ca;font-weight:900}
.click{color:#1d4ed8;text-decoration:none;font-weight:900}.click:hover{text-decoration:underline}.open{display:inline-block;padding:7px 10px;border-radius:8px;background:var(--purple);color:#fff!important;text-decoration:none;font-size:12px;font-weight:900}
.links{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.link-card{display:block;padding:13px;border:1px solid var(--line);border-radius:12px;text-decoration:none;color:#1d4ed8;font-weight:900;background:#fff}.link-card small{display:block;margin-top:5px;color:var(--muted);font-weight:400;word-break:break-all}
.ai-note{display:none;padding:11px 13px;border-radius:11px;background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;margin-bottom:14px;font-size:13px}
.score{height:10px;border-radius:999px;background:#e5e7eb;overflow:hidden;margin-top:8px}.score span{display:block;height:100%;background:linear-gradient(90deg,#22c55e,#f59e0b,#ef4444)}
.footer{text-align:center;color:var(--muted);font-size:12px;margin-top:22px}
@media(max-width:920px){.layout{grid-template-columns:1fr}.sidebar{position:static;grid-template-columns:1fr 1fr}.meta-strip,.grid4{grid-template-columns:1fr 1fr}}
@media(max-width:620px){.header-inner,.input-top{flex-direction:column}.meta-strip,.grid4,.sidebar,.links,.actions-grid{grid-template-columns:1fr}.wrap{padding:0 12px 30px}.brand h1{font-size:19px}}
@media print{header,.input-card,.status,.capture{display:none!important}.layout{grid-template-columns:240px 1fr}.sidebar{position:static}.section-card,.sidebar-card,.meta-strip{box-shadow:none}}
</style>
</head>
<body>
<header><div class="header-inner">
<div class="brand"><div class="logo">✉</div><div><h1>AI EMAIL ANALYZER</h1><p>Enterprise email intelligence report</p></div></div>
<div><button class="btn btn-white" id="newBtn">＋ New Analysis</button> <button class="btn btn-primary" id="printBtn">⬇ Download Report</button></div>
</div></header>

<main class="wrap">
<section class="card input-card">
<div class="input-top"><div><h2>Analyze Your Email</h2><p>Paste the complete email directly from Gmail or Outlook. The analyzer removes Gmail interface text and focuses on the real message.</p></div>
<select id="language"><option value="en">English</option><option value="ur">اردو</option><option value="ar">العربية</option></select></div>
<textarea id="emailText" placeholder="Paste the complete email here..."></textarea>
<div class="capture" id="capture"></div>
<div class="controls"><button class="btn btn-primary" id="analyzeBtn">Analyze Email</button><button class="btn btn-soft" id="clearBtn">Clear</button></div>
<div id="status" class="status"></div>
</section>

<section id="reportRoot" class="hidden">
<div class="meta-strip">
<div class="meta"><div class="meta-label">Subject</div><div class="meta-value" id="mSubject">—</div></div>
<div class="meta"><div class="meta-label">Date</div><div class="meta-value" id="mDate">—</div></div>
<div class="meta"><div class="meta-label">Sender</div><div class="meta-value" id="mSender">—</div></div>
<div class="meta"><div class="meta-label">Importance</div><div class="meta-value" id="mImportance">—</div></div>
</div>

<div class="layout">
<aside class="sidebar">
<section class="sidebar-card"><h3>TABLE OF CONTENTS</h3><nav class="toc">
<a href="#summary"><span class="num">1</span>Executive Summary</a>
<a href="#purpose"><span class="num">2</span>Sender Purpose</a>
<a href="#points"><span class="num">3</span>Key Points</a>
<a href="#info"><span class="num">4</span>Key Information</a>
<a href="#items"><span class="num">5</span>Clickable Items</a>
<a href="#risk"><span class="num">6</span>Risk Assessment</a>
<a href="#actions"><span class="num">7</span>Recommended Actions</a>
<a href="#links"><span class="num">8</span>All Links</a>
</nav></section>
<section class="sidebar-card"><h3>EMAIL OVERVIEW</h3>
<div class="overview-row"><div class="ov-key">From</div><div class="ov-value" id="ovFrom">—</div></div>
<div class="overview-row"><div class="ov-key">Type</div><div class="ov-value" id="ovType">—</div></div>
<div class="overview-row"><div class="ov-key">Links</div><div class="ov-value" id="ovLinks">—</div></div>
<div class="overview-row"><div class="ov-key">AI Model</div><div class="ov-value" id="ovModel">—</div></div>
</section>
</aside>

<section class="report">
<div class="ai-note" id="aiNote">AI enhancement was unavailable. A cleaned professional report was generated locally from the actual email message.</div>

<article class="section-card" id="summary"><div class="section-title"><span class="badge">1</span><h2>Executive Summary</h2></div><div class="body" id="summaryText"></div></article>
<article class="section-card" id="purpose"><div class="section-title"><span class="badge">2</span><h2>Sender's Main Purpose</h2></div><div class="body" id="purposeText"></div></article>
<article class="section-card" id="points"><div class="section-title"><span class="badge">3</span><h2>Key Points</h2></div><ul class="list" id="pointsList"></ul></article>
<article class="section-card" id="info"><div class="section-title"><span class="badge">4</span><h2>Key Information</h2></div><div class="grid4" id="infoGrid"></div></article>
<article class="section-card" id="items"><div class="section-title"><span class="badge">5</span><h2>Clickable Articles / Jobs / Products</h2></div><div id="itemsArea"></div></article>
<article class="section-card" id="risk"><div class="section-title"><span class="badge">6</span><h2>Risk & Scam Assessment</h2></div><div class="grid4" id="riskGrid"></div><ul class="list risks" id="risksList" style="margin-top:14px"></ul></article>
<article class="section-card" id="actions"><div class="section-title"><span class="badge">7</span><h2>Recommended Actions</h2></div><div class="actions-grid" id="actionsGrid"></div></article>
<article class="section-card" id="links"><div class="section-title"><span class="badge">8</span><h2>All Available Links</h2></div><div class="links" id="linksGrid"></div></article>
</section>
</div>
<div class="footer">AI-generated information may contain inaccuracies. Verify important details before taking action.</div>
</section>
</main>

<script>
const $=id=>document.getElementById(id);
let emailHtml="", capturedLinks=[];
function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}
function validUrl(u){try{let x=new URL(u);return x.protocol==="http:"||x.protocol==="https:"}catch{return false}}
function linkify(v,u){return validUrl(u)?`<a class="click" href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(v||"Open")}</a>`:esc(v||"—")}

$("emailText").addEventListener("paste",e=>{
 emailHtml=e.clipboardData?.getData("text/html")||"";
 if(emailHtml){
  let doc=new DOMParser().parseFromString(emailHtml,"text/html");
  capturedLinks=[...doc.querySelectorAll("a[href]")].map(a=>({text:(a.textContent||"").trim(),url:a.href})).filter(x=>validUrl(x.url));
  $("capture").style.display="block";$("capture").textContent=`Captured ${capturedLinks.length} hidden link(s) from the pasted email.`;
 }else{
  capturedLinks=[];$("capture").style.display="block";$("capture").textContent="No hidden links were detected. Visible URLs will still be included.";
 }
});

function renderList(id,arr,fallback){
 let el=$(id);el.innerHTML="";
 (arr?.length?arr:[fallback]).forEach(v=>{let li=document.createElement("li");li.textContent=v||fallback;el.appendChild(li)})
}
function renderInfo(arr){
 $("infoGrid").innerHTML="";
 (arr?.length?arr:[{label:"Information",value:"Not provided"}]).slice(0,8).forEach(x=>{
  let d=document.createElement("div");d.className="info";d.innerHTML=`<div class="label">${esc(x.label)}</div><div class="value">${linkify(x.value,x.url)}</div>`;$("infoGrid").appendChild(d)
 })
}
function renderRisk(data){
 $("riskGrid").innerHTML="";
 [
  {label:"Scam probability",value:`${data.scam_probability??0}%`},
  {label:"Risk level",value:data.risk_level||"Low"},
  {label:"Suspicious links",value:String(data.suspicious_links??0)},
  {label:"Verification",value:data.verification_status||"Recommended"}
 ].forEach(x=>{let d=document.createElement("div");d.className="info";d.innerHTML=`<div class="label">${esc(x.label)}</div><div class="value">${esc(x.value)}</div>`;$("riskGrid").appendChild(d)})
}
function renderItems(arr){
 $("itemsArea").innerHTML="";
 if(!arr?.length){$("itemsArea").innerHTML='<div class="body">No article, job, product or offer link was detected.</div>';return}
 let h='<div class="table-wrap"><table><thead><tr><th>Title</th><th>Category</th><th>Source</th><th>Open</th></tr></thead><tbody>';
 arr.forEach(x=>h+=`<tr><td>${linkify(x.title,x.url)}</td><td>${linkify(x.category,x.url)}</td><td>${linkify(x.source,x.url)}</td><td>${validUrl(x.url)?`<a class="open" href="${esc(x.url)}" target="_blank" rel="noopener noreferrer">Open ↗</a>`:"Not available"}</td></tr>`);
 $("itemsArea").innerHTML=h+"</tbody></table></div>"
}
function renderActions(arr){
 $("actionsGrid").innerHTML="";
 (arr||[]).forEach(x=>{let d=document.createElement("div");d.className="action";d.innerHTML=`<strong>${esc(x.title)}</strong><span>${esc(x.detail)}</span>`;$("actionsGrid").appendChild(d)})
}
function renderLinks(arr){
 $("linksGrid").innerHTML="";
 let good=(arr||[]).filter(x=>validUrl(x.url));
 if(!good.length){$("linksGrid").innerHTML='<div class="body">No clickable links were found.</div>';return}
 good.forEach(x=>{let a=document.createElement("a");a.className="link-card";a.href=x.url;a.target="_blank";a.rel="noopener noreferrer";a.innerHTML=`${esc(x.title||"Open link")}<small>${esc(x.url)}</small>`;$("linksGrid").appendChild(a)})
}

$("analyzeBtn").onclick=async()=>{
 let email_text=$("emailText").value.trim();
 if(!email_text){$("status").className="status error";$("status").textContent="Please paste the email first.";return}
 $("analyzeBtn").disabled=true;$("status").className="status";$("status").textContent="Creating enterprise report...";
 try{
  let r=await fetch("/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email_text,email_html:emailHtml,captured_links:capturedLinks,language:$("language").value})});
  let raw=await r.text(),d;try{d=JSON.parse(raw)}catch{throw new Error("The server response was interrupted. Please retry.")}
  if(!r.ok)throw new Error(d.error||"Analysis failed");
  let m=d.metadata||{};
  $("mSubject").textContent=m.subject||"—";$("mDate").textContent=m.date||"—";$("mSender").textContent=m.sender||"—";$("mImportance").textContent=m.importance||"—";
  $("ovFrom").textContent=m.sender||"—";$("ovType").textContent=m.email_type||"General Email";$("ovLinks").textContent=(d.links||[]).length;$("ovModel").textContent=d.model_used||"Local Analyzer";
  $("summaryText").textContent=d.executive_summary||"—";$("purposeText").textContent=d.sender_purpose||"—";
  $("aiNote").style.display=d.ai_fallback?"block":"none";
  renderList("pointsList",d.key_points,"Review the email content carefully.");
  renderInfo(d.key_information);renderItems(d.items);renderRisk(d.risk_assessment||{});
  renderList("risksList",d.risks,"No major risk was automatically detected. Verify important details.");
  renderActions(d.recommended_actions);renderLinks(d.links);
  $("reportRoot").classList.remove("hidden");$("status").textContent="";$("reportRoot").scrollIntoView({behavior:"smooth"})
 }catch(e){$("status").className="status error";$("status").textContent=e.message}
 finally{$("analyzeBtn").disabled=false}
};
$("clearBtn").onclick=$("newBtn").onclick=()=>location.reload();$("printBtn").onclick=()=>window.print();
</script>
</body>
</html>
"""

GMAIL_NOISE = (
 "using gmail with screen readers","enable desktop notifications for gmail","ok no thanks",
 "skip to content","inbox","starred","snoozed","sent","drafts","more","meet","new meeting",
 "join a meeting","hangouts","search mail","settings","google apps","account"
)
FOOTER_NOISE = (
 "unsubscribe","privacy policy","terms of service","download the app","sent by",
 "manage preferences","view in browser","switch to the weekly digest"
)
IGNORE_LINKS = (
 "unsubscribe","privacy","terms","preferences","settings","app store","google play",
 "view in browser","manage email","cookie","tracking","pixel","facebook","twitter",
 "instagram","linkedin","download app"
)

def clean(s):
    return " ".join(unescape(s or "").split()).strip()

def clean_email_text(text):
    out=[]
    for line in (text or "").splitlines():
        line=clean(line)
        low=line.lower()
        if not line: continue
        if any(low == x or low.startswith(x) for x in GMAIL_NOISE): continue
        if any(x in low for x in FOOTER_NOISE): continue
        if re.fullmatch(r"\d+\s+of\s+\d+",low): continue
        out.append(line)
    return "\n".join(out)

def valid_url(u):
    try:
        p=urlparse((u or "").strip())
        return (u or "").strip() if p.scheme in ("http","https") and p.netloc else ""
    except Exception:
        return ""

def host(u):
    try: return urlparse(u).netloc.lower().replace("www.","")
    except Exception: return "Website"

def irrelevant_link(t,u):
    s=f"{t} {u}".lower()
    return any(x in s for x in IGNORE_LINKS)

def category(t,u):
    s=f"{t} {u}".lower()
    if any(x in s for x in ("job","career","apply","vacancy","position")): return "Job"
    if any(x in s for x in ("article","read","story","post","medium.com","newsletter")): return "Article"
    if any(x in s for x in ("product","shop","buy","price","store")): return "Product"
    if any(x in s for x in ("event","webinar","register","meeting")): return "Event"
    return "Link"

def extract_links(html,front,text):
    data=[]
    if html:
        soup=BeautifulSoup(html,"html.parser")
        for a in soup.find_all("a",href=True):
            u=valid_url(a.get("href"));t=clean(a.get_text(" ",strip=True))
            if u:data.append((t or host(u),u))
    for x in front or []:
        u=valid_url(x.get("url"));t=clean(x.get("text"))
        if u:data.append((t or host(u),u))
    for u in re.findall(r'https?://[^\s<>"\']+',text or ""):
        data.append((u,u))
    out=[];seen=set()
    for t,u in data:
        if u in seen or irrelevant_link(t,u):continue
        seen.add(u)
        if len(t)<3 and len(u)>300:continue
        out.append({"title":t[:180],"url":u,"category":category(t,u),"source":host(u)})
    return out[:40]

def metadata(text):
    ls=[clean(x) for x in text.splitlines() if clean(x)]
    subject=sender=date="Not provided";email_type="General Email"
    for line in ls[:80]:
        low=line.lower()
        if low.startswith("subject:"):subject=clean(line.split(":",1)[1])
        elif low.startswith("from:"):sender=clean(line.split(":",1)[1])
        elif low.startswith("date:") or low.startswith("sent:"):date=clean(line.split(":",1)[1])
    if subject=="Not provided" and ls:subject=ls[0][:160]
    joined=" ".join(ls).lower()
    if "job" in joined or "vacancy" in joined:email_type="Job Alert / Recruitment"
    elif "invoice" in joined or "payment" in joined:email_type="Invoice / Payment"
    elif "order" in joined or "shipment" in joined:email_type="Order / Delivery"
    elif "newsletter" in joined or "article" in joined:email_type="Newsletter / Articles"
    elif "meeting" in joined or "appointment" in joined:email_type="Meeting / Appointment"
    importance="High" if any(x in joined for x in ("urgent","immediately","deadline","final notice","payment due")) else "Medium"
    return {"subject":subject,"sender":sender,"date":date,"importance":importance,"email_type":email_type}

def useful_sentences(text,limit=8):
    raw=re.split(r'(?<=[.!?])\s+|\n+',text)
    out=[]
    for s in raw:
        s=clean(s)
        if len(s)<28:continue
        low=s.lower()
        if any(x in low for x in GMAIL_NOISE+FOOTER_NOISE):continue
        if s not in out:out.append(s)
        if len(out)>=limit:break
    return out

def local_report(text,links,lang):
    m=metadata(text);sent=useful_sentences(text);first=sent[0] if sent else m["subject"];second=sent[1] if len(sent)>1 else first
    count=len(links);joined=text.lower()
    suspicious=sum(1 for x in links if any(k in x["url"].lower() for k in ("bit.ly","tinyurl","redirect","track","click")))
    scam=min(85,10+suspicious*12+(15 if any(x in joined for x in ("password","otp","bank account","wire transfer","gift card")) else 0))
    risk_level="High" if scam>=60 else "Medium" if scam>=30 else "Low"
    if lang=="ur":
        summary=f"یہ ای میل بنیادی طور پر اس موضوع سے متعلق ہے: {first} اس میں {count} قابلِ کلک متعلقہ لنکس موجود ہیں۔"
        purpose=f"بھیجنے والے کا بنیادی مقصد یہ معلومات پہنچانا یا آپ سے متعلقہ کارروائی کروانا ہے: {second}"
        risks=["نامعلوم domain کھولنے سے پہلے اس کی تصدیق کریں۔","Payment، login، OTP یا ذاتی معلومات کی درخواست کو آزادانہ طور پر verify کریں۔"]
        actions=[{"title":"اہم تفصیلات verify کریں","detail":"Sender، تاریخ، قیمت، تنخواہ، deadline اور official website چیک کریں۔"},{"title":"متعلقہ لنکس کھولیں","detail":"نیچے موجود article، job، product یا offer links استعمال کریں۔"}]
    elif lang=="ar":
        summary=f"يتعلق هذا البريد أساساً بالموضوع التالي: {first} ويحتوي على {count} روابط ذات صلة قابلة للنقر."
        purpose=f"الغرض الرئيسي للمرسل هو إيصال هذه المعلومات أو طلب الإجراء التالي: {second}"
        risks=["تحقق من النطاق قبل فتح الروابط غير المعروفة.","تحقق بشكل مستقل من طلبات الدفع أو تسجيل الدخول أو رمز OTP أو البيانات الشخصية."]
        actions=[{"title":"التحقق من التفاصيل","detail":"تحقق من المرسل والتاريخ والسعر والموعد والموقع الرسمي."},{"title":"فتح الروابط ذات الصلة","detail":"استخدم روابط المقالات أو الوظائف أو المنتجات أدناه."}]
    else:
        summary=f"This email is mainly about: {first} It contains {count} relevant clickable link(s)."
        purpose=f"The sender's main purpose is to communicate this information or request the following action: {second}"
        risks=["Verify the domain before opening unknown or unexpected links.","Independently verify requests for payment, login credentials, OTPs or personal information."]
        actions=[{"title":"Verify key details","detail":"Check the sender, date, price, salary, deadline and official website."},{"title":"Open relevant items","detail":"Use the clickable article, job, product or offer links below."}]
    return {
      "metadata":m,"executive_summary":summary,"sender_purpose":purpose,
      "key_points":sent[:5] or [first],
      "key_information":[
        {"label":"Email type","value":m["email_type"],"url":""},
        {"label":"Clickable links","value":str(count),"url":""},
        {"label":"Message length","value":f"{len(text):,} characters","url":""},
        {"label":"Priority","value":m["importance"],"url":""}
      ],
      "risk_assessment":{"scam_probability":scam,"risk_level":risk_level,"suspicious_links":suspicious,"verification_status":"Recommended"},
      "risks":risks,"recommended_actions":actions,"ai_fallback":True,"model_used":"Local Analyzer"
    }

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
    raw=(p.get("email_text") or "").strip()
    if not raw:return jsonify({"error":"Please paste the email text."}),400
    text=clean_email_text(raw)[:50000]
    lang_code=p.get("language","en")
    links=extract_links(p.get("email_html") or "",p.get("captured_links") or [],text)
    result=local_report(text,links,lang_code)

    api=os.environ.get("GEMINI_API_KEY")
    if api:
        prompt=f"""Return ONLY valid JSON in {LANGUAGES.get(lang_code,"English")}.
Analyze the email professionally. Ignore Gmail interface text.
JSON structure:
{{"metadata":{{"subject":"","sender":"","date":"","importance":"Low, Medium, or High","email_type":""}},
"executive_summary":"","sender_purpose":"","key_points":[""],
"key_information":[{{"label":"","value":"","url":""}}],
"risk_assessment":{{"scam_probability":0,"risk_level":"Low, Medium, or High","suspicious_links":0,"verification_status":""}},
"risks":[""],"recommended_actions":[{{"title":"","detail":""}}]}}
Maximum 5 key points, 6 information items, 4 risks and 5 actions.
EMAIL:
{text[:9000]}"""
        model_candidates=[]
        configured=os.environ.get("GEMINI_MODEL","").strip()
        if configured:model_candidates.append(configured)
        model_candidates += ["gemini-3.1-flash-lite-preview","gemini-2.5-flash-lite","gemini-2.0-flash"]
        seen=set()
        for model in model_candidates:
            if model in seen:continue
            seen.add(model)
            try:
                client=genai.Client(api_key=api,http_options=types.HttpOptions(timeout=20000))
                response=client.models.generate_content(
                    model=model,contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,max_output_tokens=1300,response_mime_type="application/json"
                    )
                )
                ai=extract_json(response.text)
                for key in ("metadata","executive_summary","sender_purpose","key_points","key_information","risk_assessment","risks","recommended_actions"):
                    if ai.get(key):result[key]=ai[key]
                result["ai_fallback"]=False
                result["model_used"]=model
                break
            except Exception:
                continue

    result["items"]=links[:30]
    result["links"]=[{"title":x["title"],"url":x["url"],"description":x["category"]} for x in links]
    return jsonify(result)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
