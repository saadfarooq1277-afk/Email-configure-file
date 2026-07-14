import json, os, re
from html import unescape
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template_string, request
from google import genai
from google.genai import types

app = Flask(__name__)
LANGUAGES = {"en":"English","ur":"Urdu","ar":"Arabic"}

HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Email Intelligence Report</title>
<style>
:root{--p:#6d28d9;--bg:#f3f6fb;--t:#172033;--m:#667085;--l:#e5e7eb;--s:0 14px 40px rgba(31,41,55,.1)}
*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:var(--bg);color:var(--t)}
header{background:linear-gradient(135deg,#0e1744,#32106d);color:#fff;padding:20px 0;position:sticky;top:0;z-index:20}
.hi{max-width:1240px;margin:auto;padding:0 20px;display:flex;justify-content:space-between;align-items:center;gap:15px}
.brand{display:flex;gap:14px;align-items:center}.logo{width:52px;height:52px;border-radius:15px;display:grid;place-items:center;background:linear-gradient(135deg,#3b82f6,#8b5cf6);font-size:26px}
h1{margin:0;font-size:23px}.brand p{margin:4px 0 0;color:#dbeafe;font-size:13px}
.btn{border:0;border-radius:11px;padding:11px 16px;font-weight:800;cursor:pointer}.main{background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff}.white{background:#fff;color:#111827}.soft{background:#eef2ff;color:#4338ca}
.wrap{max-width:1240px;margin:28px auto;padding:0 20px 50px}
.card,.meta,.side,.section{background:#fff;border:1px solid var(--l);border-radius:18px;box-shadow:var(--s)}
.input{padding:24px}.top{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}.top h2{margin:0}.top p{color:var(--m);line-height:1.6}
select{padding:10px;border:1px solid var(--l);border-radius:10px}
textarea{width:100%;min-height:240px;margin-top:16px;padding:16px;border:1px solid #cfd7e2;border-radius:14px;font:inherit;line-height:1.6;resize:vertical}
textarea:focus{outline:3px solid #ddd6fe;border-color:#7c3aed}.controls{display:flex;gap:10px;margin-top:14px}.status{min-height:24px;margin-top:12px;color:#4f46e5;font-weight:800}.error{color:#dc2626}
.capture{display:none;margin-top:10px;padding:10px 12px;border-radius:10px;background:#ecfdf3;color:#166534;font-size:13px}.hidden{display:none!important}
.meta{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-top:22px;padding:18px}.mb{padding:14px;border-radius:14px;background:#fafbff}.ml{font-size:11px;color:var(--m);text-transform:uppercase;font-weight:900}.mv{font-weight:900;margin-top:6px;word-break:break-word}
.layout{display:grid;grid-template-columns:290px 1fr;gap:20px;margin-top:20px;align-items:start}.sidebar{position:sticky;top:108px;display:grid;gap:16px}.side{padding:18px}.side h3{margin:0 0 14px;color:var(--p)}
.toc a{display:flex;gap:8px;align-items:center;padding:8px;text-decoration:none;color:#344054;border-radius:8px;font-size:13px}.toc a:hover{background:#f3f0ff}.num{width:23px;height:23px;border-radius:7px;background:var(--p);color:#fff;display:grid;place-items:center;font-size:11px;font-weight:900}
.report{display:grid;gap:16px}.section{padding:20px}.st{display:flex;gap:10px;align-items:center;border-bottom:1px solid var(--l);padding-bottom:12px;margin-bottom:14px}.st h2{margin:0;font-size:19px}.badge{width:31px;height:31px;border-radius:9px;background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;display:grid;place-items:center;font-weight:900}
.body{line-height:1.8;color:#344054;white-space:pre-wrap}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.box{padding:14px;border:1px solid var(--l);border-radius:14px;background:#fbfcff}.box .k{font-size:12px;color:var(--m);font-weight:800}.box .v{font-size:16px;font-weight:900;margin-top:6px;word-break:break-word}
.actions{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.act{padding:14px;border:1px solid var(--l);border-radius:14px}.act strong{display:block;color:#4338ca;margin-bottom:5px}
ul{list-style:none;padding:0;margin:0;display:grid;gap:10px}li{padding:12px;border:1px solid #edf0f4;background:#f8fafc;border-radius:12px;line-height:1.6}li:before{content:"⚠";color:#d97706;font-weight:900;margin-right:8px}
.table{overflow:auto;border:1px solid var(--l);border-radius:14px}table{width:100%;border-collapse:collapse;min-width:800px}th,td{padding:12px;border-bottom:1px solid var(--l);text-align:left;font-size:13px}th{background:#f8f7ff;color:#4338ca}
.a{color:#1d4ed8;text-decoration:none;font-weight:900}.a:hover{text-decoration:underline}.open{display:inline-block;padding:7px 10px;border-radius:8px;background:var(--p);color:#fff!important;text-decoration:none;font-size:12px;font-weight:900}
.links{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.link{display:block;padding:13px;border:1px solid var(--l);border-radius:12px;text-decoration:none;color:#1d4ed8;font-weight:900}.link small{display:block;color:var(--m);font-weight:400;margin-top:5px;word-break:break-all}
.note{display:none;padding:11px 13px;border:1px solid #fed7aa;background:#fff7ed;color:#9a3412;border-radius:11px;margin-bottom:14px}
@media(max-width:980px){.layout{grid-template-columns:1fr}.sidebar{position:static}.meta,.grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:640px){.hi,.top{flex-direction:column}.meta,.grid,.links,.actions{grid-template-columns:1fr}.wrap{padding:0 12px 30px}}
@media print{header,.input,.status,.capture{display:none!important}.layout{grid-template-columns:240px 1fr}.sidebar{position:static}.section,.side,.meta{box-shadow:none}}
</style></head><body>
<header><div class="hi"><div class="brand"><div class="logo">✉</div><div><h1>EMAIL INTELLIGENCE REPORT</h1><p>Professional analysis, sender intelligence and clickable evidence</p></div></div><div><button class="btn white" id="new">＋ New</button> <button class="btn main" id="print">⬇ Download</button></div></div></header>
<main class="wrap">
<section class="card input"><div class="top"><div><h2>Analyze Your Email</h2><p>Paste directly from Gmail or Outlook. The report includes summary, analysis, email details, sender details, risks, actions and all clickable links.</p></div><select id="lang"><option value="en">English</option><option value="ur">اردو</option><option value="ar">العربية</option></select></div>
<textarea id="text" placeholder="Paste the complete email here..."></textarea><div class="capture" id="capture"></div><div class="controls"><button class="btn main" id="analyze">Generate Professional Report</button><button class="btn soft" id="clear">Clear</button></div><div id="status" class="status"></div></section>

<section id="root" class="hidden">
<div class="meta"><div class="mb"><div class="ml">Subject</div><div class="mv" id="subject">—</div></div><div class="mb"><div class="ml">Sender</div><div class="mv" id="sender">—</div></div><div class="mb"><div class="ml">Date</div><div class="mv" id="date">—</div></div><div class="mb"><div class="ml">Email Type</div><div class="mv" id="type">—</div></div><div class="mb"><div class="ml">Priority</div><div class="mv" id="priority">—</div></div></div>
<div class="layout"><aside class="sidebar"><section class="side"><h3>REPORT CONTENTS</h3><nav class="toc">
<a href="#s1"><span class="num">1</span>Executive Summary</a><a href="#s2"><span class="num">2</span>Detailed Analysis</a><a href="#s3"><span class="num">3</span>Email Information</a><a href="#s4"><span class="num">4</span>Sender Information</a><a href="#s5"><span class="num">5</span>Important Details</a><a href="#s6"><span class="num">6</span>Clickable Items</a><a href="#s7"><span class="num">7</span>Risk Assessment</a><a href="#s8"><span class="num">8</span>Recommended Actions</a><a href="#s9"><span class="num">9</span>All Links</a>
</nav></section></aside>
<section class="report"><div class="note" id="note">AI enhancement was unavailable. A professional local report was generated from the email.</div>
<article class="section" id="s1"><div class="st"><span class="badge">1</span><h2>Executive Summary</h2></div><div class="body" id="summary"></div></article>
<article class="section" id="s2"><div class="st"><span class="badge">2</span><h2>Detailed Email Analysis</h2></div><div class="body" id="analysis"></div></article>
<article class="section" id="s3"><div class="st"><span class="badge">3</span><h2>Email Information</h2></div><div class="grid" id="emailInfo"></div></article>
<article class="section" id="s4"><div class="st"><span class="badge">4</span><h2>Sender Information</h2></div><div class="grid" id="senderInfo"></div></article>
<article class="section" id="s5"><div class="st"><span class="badge">5</span><h2>Important Names, Companies, Dates, Prices & Locations</h2></div><div class="grid" id="entities"></div></article>
<article class="section" id="s6"><div class="st"><span class="badge">6</span><h2>Clickable Articles / Jobs / Products / Offers</h2></div><div id="items"></div></article>
<article class="section" id="s7"><div class="st"><span class="badge">7</span><h2>Risk, Red Flags & Verification</h2></div><div class="grid" id="riskGrid"></div><ul id="risks" style="margin-top:14px"></ul></article>
<article class="section" id="s8"><div class="st"><span class="badge">8</span><h2>Recommended Actions</h2></div><div class="actions" id="actions"></div></article>
<article class="section" id="s9"><div class="st"><span class="badge">9</span><h2>All Available Links</h2></div><div class="links" id="links"></div></article>
</section></div></section></main>
<script>
const $=id=>document.getElementById(id);let html="",clip=[];
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
function ok(u){try{let x=new URL(u);return x.protocol==="http:"||x.protocol==="https:"}catch{return false}}
function linked(v,u){return ok(u)?`<a class="a" href="${esc(u)}" target="_blank">${esc(v||"Open")}</a>`:esc(v||"—")}
$("text").addEventListener("paste",e=>{html=e.clipboardData?.getData("text/html")||"";if(html){let d=new DOMParser().parseFromString(html,"text/html");clip=[...d.querySelectorAll("a[href]")].map(a=>({text:(a.textContent||"").trim(),url:a.href})).filter(x=>ok(x.url));$("capture").style.display="block";$("capture").textContent=`Captured ${clip.length} hidden link(s).`}else{clip=[];$("capture").style.display="block";$("capture").textContent="No hidden links found. Visible URLs will still work."}});
function cards(id,a){let e=$(id);e.innerHTML="";(a?.length?a:[{label:"Information",value:"Not provided"}]).slice(0,12).forEach(x=>{let d=document.createElement("div");d.className="box";d.innerHTML=`<div class="k">${esc(x.label)}</div><div class="v">${linked(x.value,x.url)}</div>`;e.appendChild(d)})}
function items(a){$("items").innerHTML="";if(!a?.length){$("items").innerHTML='<div class="body">No clickable item was detected.</div>';return}let h='<div class="table"><table><tr><th>Title</th><th>Category</th><th>Source</th><th>Details</th><th>Open</th></tr>';a.forEach(x=>h+=`<tr><td>${linked(x.title,x.url)}</td><td>${linked(x.category,x.url)}</td><td>${linked(x.source,x.url)}</td><td>${esc(x.details||"—")}</td><td>${ok(x.url)?`<a class="open" href="${esc(x.url)}" target="_blank">Open ↗</a>`:"Not available"}</td></tr>`);$("items").innerHTML=h+"</table></div>"}
function actions(a){$("actions").innerHTML="";(a||[]).forEach(x=>{let d=document.createElement("div");d.className="act";d.innerHTML=`<strong>${esc(x.title)}</strong><span>${esc(x.detail)}</span>`;$("actions").appendChild(d)})}
function list(id,a,f){let e=$(id);e.innerHTML="";(a?.length?a:[f]).forEach(v=>{let li=document.createElement("li");li.textContent=v||f;e.appendChild(li)})}
function links(a){$("links").innerHTML="";let g=(a||[]).filter(x=>ok(x.url));if(!g.length){$("links").innerHTML='<div class="body">No links found.</div>';return}g.forEach(x=>{let e=document.createElement("a");e.className="link";e.href=x.url;e.target="_blank";e.innerHTML=`${esc(x.title||"Open link")}<small>${esc(x.url)}</small>`;$("links").appendChild(e)})}
$("analyze").onclick=async()=>{let text=$("text").value.trim();if(!text){$("status").className="status error";$("status").textContent="Please paste the email first.";return}$("analyze").disabled=true;$("status").textContent="Generating professional report...";try{let r=await fetch("/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email_text:text,email_html:html,captured_links:clip,language:$("lang").value})});let raw=await r.text(),d;try{d=JSON.parse(raw)}catch{throw new Error("Server response was interrupted. Please retry.")}if(!r.ok)throw new Error(d.error||"Analysis failed");let m=d.metadata||{};$("subject").textContent=m.subject||"—";$("sender").textContent=m.sender||"—";$("date").textContent=m.date||"—";$("type").textContent=m.email_type||"—";$("priority").textContent=m.importance||"—";$("summary").textContent=d.executive_summary||"—";$("analysis").textContent=d.detailed_analysis||"—";$("note").style.display=d.ai_fallback?"block":"none";cards("emailInfo",d.email_information);cards("senderInfo",d.sender_information);cards("entities",d.important_entities);items(d.items);cards("riskGrid",[{label:"Scam probability",value:`${d.risk_assessment?.scam_probability??0}%`},{label:"Risk level",value:d.risk_assessment?.risk_level||"Low"},{label:"Suspicious links",value:String(d.risk_assessment?.suspicious_links??0)},{label:"Verification",value:d.risk_assessment?.verification_status||"Recommended"}]);list("risks",d.risks,"No major risk detected.");actions(d.recommended_actions);links(d.links);$("root").classList.remove("hidden");$("status").textContent="";$("root").scrollIntoView({behavior:"smooth"})}catch(e){$("status").className="status error";$("status").textContent=e.message}finally{$("analyze").disabled=false}};
$("clear").onclick=$("new").onclick=()=>location.reload();$("print").onclick=()=>window.print();
</script></body></html>"""

IGNORE=("unsubscribe","privacy","terms","preferences","settings","app store","google play","cookie","tracking","pixel","facebook","twitter","instagram","linkedin")

def clean(s): return " ".join(unescape(s or "").split()).strip()
def good(u):
    try:
        p=urlparse((u or "").strip())
        return (u or "").strip() if p.scheme in ("http","https") and p.netloc else ""
    except: return ""
def host(u):
    try:return urlparse(u).netloc.lower().replace("www.","")
    except:return "Website"
def cat(t,u):
    s=f"{t} {u}".lower()
    if any(x in s for x in ("job","career","apply","vacancy","position")):return "Job"
    if any(x in s for x in ("article","read","story","post","medium.com","newsletter")):return "Article"
    if any(x in s for x in ("product","shop","buy","price","store")):return "Product"
    if any(x in s for x in ("event","webinar","register","meeting")):return "Event"
    return "Link"

def get_links(html,front,text):
    data=[]
    if html:
        soup=BeautifulSoup(html,"html.parser")
        for a in soup.find_all("a",href=True):
            u=good(a.get("href"));t=clean(a.get_text(" ",strip=True))
            if u:data.append((t or host(u),u))
    for x in front or []:
        u=good(x.get("url"));t=clean(x.get("text"))
        if u:data.append((t or host(u),u))
    for u in re.findall(r'https?://[^\s<>"\']+',text or ""):data.append((u,u))
    out=[];seen=set()
    for t,u in data:
        if u in seen or any(x in f"{t} {u}".lower() for x in IGNORE):continue
        seen.add(u);out.append({"title":t[:180],"url":u,"category":cat(t,u),"source":host(u),"details":""})
    return out[:40]

def metadata(text):
    ls=[clean(x) for x in text.splitlines() if clean(x)]
    subject=sender=date=recipient="Not provided";typ="General Email"
    for line in ls[:80]:
        low=line.lower()
        if low.startswith("subject:"):subject=clean(line.split(":",1)[1])
        elif low.startswith("from:"):sender=clean(line.split(":",1)[1])
        elif low.startswith("to:"):recipient=clean(line.split(":",1)[1])
        elif low.startswith("date:") or low.startswith("sent:"):date=clean(line.split(":",1)[1])
    if subject=="Not provided" and ls:subject=ls[0][:160]
    alltext=" ".join(ls).lower()
    if "job" in alltext or "vacancy" in alltext:typ="Job Alert / Recruitment"
    elif "invoice" in alltext or "payment" in alltext:typ="Invoice / Payment"
    elif "order" in alltext or "shipment" in alltext:typ="Order / Delivery"
    elif "newsletter" in alltext or "article" in alltext:typ="Newsletter / Articles"
    elif "meeting" in alltext or "appointment" in alltext:typ="Meeting / Appointment"
    imp="High" if any(x in alltext for x in ("urgent","deadline","final notice","payment due")) else "Medium"
    return {"subject":subject,"sender":sender,"recipient":recipient,"date":date,"importance":imp,"email_type":typ}

def local(text,links,lang):
    m=metadata(text);ss=[clean(s) for s in re.split(r'(?<=[.!?])\s+|\n+',text) if len(clean(s))>28][:8]
    first=ss[0] if ss else m["subject"];second=ss[1] if len(ss)>1 else first;c=len(links)
    if lang=="ur":
        summary=f"یہ ای میل بنیادی طور پر اس موضوع سے متعلق ہے: {first}۔ اس میں {c} قابلِ کلک متعلقہ لنکس موجود ہیں۔"
        analysis=f"ای میل کا بنیادی مقصد معلومات فراہم کرنا، متعلقہ مواد دکھانا یا کسی کارروائی کی ترغیب دینا ہے۔ اہم ترین پیغام: {second}"
    elif lang=="ar":
        summary=f"يتعلق البريد أساساً بالموضوع التالي: {first}. ويحتوي على {c} روابط قابلة للنقر."
        analysis=f"الغرض الأساسي هو تقديم المعلومات أو عرض المحتوى أو تشجيع إجراء معين. أهم رسالة: {second}"
    else:
        summary=f"This email is mainly about: {first}. It contains {c} relevant clickable link(s)."
        analysis=f"The email's main purpose is to provide information, present relevant content, or encourage a specific action. The most important message is: {second}"
    sources=", ".join(sorted(set(x["source"] for x in links))[:4]) or "Not identified"
    return {
      "metadata":m,"executive_summary":summary,"detailed_analysis":analysis,
      "email_information":[{"label":"Subject","value":m["subject"],"url":""},{"label":"Date","value":m["date"],"url":""},{"label":"Email type","value":m["email_type"],"url":""},{"label":"Priority","value":m["importance"],"url":""},{"label":"Recipient","value":m["recipient"],"url":""},{"label":"Clickable links","value":str(c),"url":""}],
      "sender_information":[{"label":"Sender","value":m["sender"],"url":""},{"label":"Detected sources","value":sources,"url":""},{"label":"Purpose","value":"Information, promotion, notification, or requested action","url":""},{"label":"Trust status","value":"Verify sender and domain before important action","url":""}],
      "important_entities":[{"label":"Main topic","value":m["subject"],"url":""},{"label":"Date","value":m["date"],"url":""},{"label":"Companies / sources","value":sources,"url":""},{"label":"Locations / prices","value":"Review the email and linked pages for exact details","url":""}],
      "risk_assessment":{"scam_probability":10,"risk_level":"Low","suspicious_links":0,"verification_status":"Recommended"},
      "risks":["Verify the sender domain before opening unknown links.","Confirm payment, login, OTP or personal-information requests independently."],
      "recommended_actions":[{"title":"Review the key message","detail":"Check the subject, sender, dates, prices, salaries, deadlines and locations."},{"title":"Open relevant links","detail":"Use the clickable items and official links below."},{"title":"Verify sender identity","detail":"Compare the sender address and domain with the official organization website."},{"title":"Save the report","detail":"Use the Download button for your records."}],
      "ai_fallback":True,"model_used":"Local Professional Analyzer"
    }

def parse_json(s):
    s=(s or "").strip();s=re.sub(r"^```(?:json)?\s*","",s,flags=re.I);s=re.sub(r"\s*```$","",s)
    try:return json.loads(s)
    except:
        m=re.search(r"\{.*\}",s,flags=re.S)
        if not m:raise ValueError("Invalid AI response")
        return json.loads(m.group(0))

@app.get("/")
def home():return render_template_string(HTML)

@app.post("/analyze")
def analyze():
    p=request.get_json(silent=True) or {};text=(p.get("email_text") or "").strip()
    if not text:return jsonify({"error":"Please paste the email text."}),400
    text=text[:50000];lang=p.get("language","en");links=get_links(p.get("email_html") or "",p.get("captured_links") or [],text);result=local(text,links,lang)
    api=os.environ.get("GEMINI_API_KEY")
    if api:
        prompt = "Return ONLY valid JSON in %s.\nCreate a professional email intelligence report.\nJSON keys: metadata, executive_summary, detailed_analysis, email_information, sender_information, important_entities, risk_assessment, risks, recommended_actions.\nEMAIL:\n%s" % (LANGUAGES.get(lang,"English"), text[:9000])
        for model in [os.environ.get("GEMINI_MODEL","gemini-2.5-flash-lite"),"gemini-2.5-flash-lite","gemini-2.0-flash"]:
            try:
                client=genai.Client(api_key=api,http_options=types.HttpOptions(timeout=22000))
                r=client.models.generate_content(model=model,contents=prompt,config=types.GenerateContentConfig(temperature=.1,max_output_tokens=1600,response_mime_type="application/json"))
                ai=parse_json(r.text)
                for k in ("metadata","executive_summary","detailed_analysis","email_information","sender_information","important_entities","risk_assessment","risks","recommended_actions"):
                    if ai.get(k):result[k]=ai[k]
                result["ai_fallback"]=False;result["model_used"]=model;break
            except:continue
    result["items"]=links[:30];result["links"]=[{"title":x["title"],"url":x["url"]} for x in links]
    return jsonify(result)

if __name__=="__main__":app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
