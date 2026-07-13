import json
import os
import re
from flask import Flask, jsonify, render_template_string, request
from google import genai
from google.genai import types

app = Flask(__name__)

LANGUAGES = {
    "ur": "Urdu",
    "en": "English",
    "ar": "Arabic",
}

HTML = r"""
<!doctype html>
<html lang="ur" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>AI Email Analyzer</title>
  <style>
    :root{
      --primary:#6d28d9;
      --primary2:#2563eb;
      --bg:#f5f7fb;
      --card:#ffffff;
      --text:#172033;
      --muted:#667085;
      --line:#e6eaf0;
      --success:#16a34a;
      --warning:#d97706;
      --danger:#dc2626;
      --shadow:0 12px 35px rgba(31,41,55,.09);
    }
    *{box-sizing:border-box}
    html{scroll-behavior:smooth}
    body{
      margin:0;
      font-family:Inter,Arial,sans-serif;
      background:var(--bg);
      color:var(--text);
    }
    .hero{
      background:linear-gradient(135deg,#111a4d,#27105c 58%,#4c1d95);
      color:#fff;
      padding:20px 0;
      box-shadow:0 6px 20px rgba(15,23,42,.2);
      position:sticky;
      top:0;
      z-index:20;
    }
    .hero-inner{
      max-width:1180px;
      margin:auto;
      padding:0 20px;
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:16px;
    }
    .brand{display:flex;align-items:center;gap:14px}
    .logo{
      width:48px;height:48px;border-radius:14px;
      display:grid;place-items:center;
      background:linear-gradient(135deg,#3b82f6,#8b5cf6);
      font-size:25px;
      box-shadow:0 8px 20px rgba(59,130,246,.35);
    }
    .brand h1{margin:0;font-size:22px}
    .brand p{margin:3px 0 0;color:#dbeafe;font-size:13px}
    .top-actions{display:flex;gap:10px;flex-wrap:wrap}
    .btn{
      border:0;border-radius:11px;padding:11px 16px;
      font-weight:700;cursor:pointer;font-size:14px;
    }
    .btn-light{background:#fff;color:#1e293b}
    .btn-primary{background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff}
    .btn-soft{background:#eef2ff;color:#4338ca}
    .container{max-width:1180px;margin:28px auto;padding:0 20px 50px}
    .input-card,.report-card,.sidebar-card,.meta-strip{
      background:var(--card);border:1px solid var(--line);
      border-radius:18px;box-shadow:var(--shadow);
    }
    .input-card{padding:24px}
    .input-head{display:flex;justify-content:space-between;align-items:center;gap:15px}
    .input-head h2{margin:0;font-size:22px}
    .input-head p{margin:6px 0 0;color:var(--muted)}
    select{
      border:1px solid var(--line);border-radius:10px;padding:10px 13px;
      background:#fff;font-weight:700;
    }
    textarea{
      width:100%;min-height:230px;margin-top:18px;
      border:1px solid #d7dce5;border-radius:14px;
      padding:16px;font:inherit;line-height:1.65;resize:vertical;
      background:#fbfcff;
    }
    textarea:focus{outline:3px solid #ddd6fe;border-color:#7c3aed}
    .input-actions{display:flex;gap:10px;margin-top:15px;flex-wrap:wrap}
    .status{margin-top:14px;min-height:24px;font-weight:700;color:#4f46e5}
    .status.error{color:var(--danger)}
    .hidden{display:none!important}
    .meta-strip{
      margin-top:22px;padding:18px;
      display:grid;grid-template-columns:repeat(4,1fr);gap:14px;
    }
    .meta-box{
      display:flex;align-items:center;gap:12px;
      padding:12px;border-radius:14px;background:#fafbff;
    }
    .meta-icon{
      width:44px;height:44px;border-radius:12px;
      display:grid;place-items:center;font-size:20px;
      background:#eef2ff;
    }
    .meta-label{font-size:11px;color:var(--muted);text-transform:uppercase;font-weight:800}
    .meta-value{font-size:16px;font-weight:800;margin-top:4px;word-break:break-word}
    .layout{display:grid;grid-template-columns:280px 1fr;gap:20px;margin-top:20px;align-items:start}
    .sidebar{position:sticky;top:112px;display:grid;gap:16px}
    .sidebar-card{padding:18px}
    .sidebar-card h3{
      margin:0 0 14px;color:#6d28d9;font-size:15px;
      display:flex;align-items:center;gap:8px;
    }
    .toc a{
      display:flex;align-items:center;gap:9px;
      padding:9px 8px;border-radius:9px;
      text-decoration:none;color:#334155;font-size:13px;
    }
    .toc a:hover{background:#f3f0ff;color:#6d28d9}
    .num{
      width:22px;height:22px;border-radius:7px;
      display:grid;place-items:center;background:#7c3aed;color:#fff;font-size:11px;font-weight:800;
      flex:0 0 auto;
    }
    .overview-row{
      display:grid;grid-template-columns:78px 1fr;gap:9px;
      padding:9px 0;border-bottom:1px solid var(--line);font-size:13px;
    }
    .overview-row:last-child{border-bottom:0}
    .overview-key{font-weight:800;color:#344054}
    .overview-val{color:#475467;word-break:break-word}
    .report{display:grid;gap:16px}
    .report-card{padding:20px;overflow:hidden}
    .section-title{
      display:flex;align-items:center;gap:11px;
      margin-bottom:13px;padding-bottom:12px;border-bottom:1px solid var(--line);
    }
    .section-title h2{margin:0;font-size:19px}
    .section-badge{
      width:30px;height:30px;border-radius:9px;
      display:grid;place-items:center;
      color:#fff;background:linear-gradient(135deg,#7c3aed,#4f46e5);
      font-weight:800;
    }
    .section-body{line-height:1.75;color:#344054;font-size:15px}
    .facts-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
    .fact{
      border:1px solid var(--line);border-radius:14px;padding:15px;text-align:center;
      background:linear-gradient(180deg,#fff,#fafaff);
    }
    .fact .label{font-size:12px;color:var(--muted);font-weight:700}
    .fact .value{font-size:18px;font-weight:900;margin-top:7px;color:#111827}
    .list-clean{list-style:none;padding:0;margin:0;display:grid;gap:10px}
    .list-clean li{
      padding:12px 14px;border-radius:12px;background:#f8fafc;
      border:1px solid #edf0f4;line-height:1.55;
    }
    .success-list li::before{content:"✓";color:var(--success);font-weight:900;margin-inline-end:9px}
    .risk-list li::before{content:"⚠";color:var(--warning);font-weight:900;margin-inline-end:9px}
    .actions-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
    .action-box{
      padding:15px;border-radius:14px;border:1px solid #e3e8f1;background:#fbfcff;
    }
    .action-box strong{display:block;color:#4338ca;margin-bottom:5px}
    .links-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
    .link-card{
      display:block;text-decoration:none;padding:13px;border:1px solid var(--line);
      border-radius:12px;background:#fff;color:#1d4ed8;font-weight:800;
      word-break:break-word;
    }
    .link-card small{display:block;color:var(--muted);font-weight:400;margin-top:5px}
    .item-link{
      color:#4f46e5;font-weight:800;text-decoration:none;
      border-bottom:1px dashed #8b5cf6;
    }
    .item-link:hover{color:#6d28d9;border-bottom-style:solid}
    .open-link-btn{
      display:inline-flex;align-items:center;gap:6px;white-space:nowrap;
      padding:7px 11px;border-radius:9px;text-decoration:none;
      background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;
      font-size:12px;font-weight:800;box-shadow:0 5px 12px rgba(79,70,229,.18);
    }
    .open-link-btn:hover{filter:brightness(1.06)}
    .no-link{color:var(--muted);font-size:12px}
    .table-wrap{overflow:auto;border:1px solid var(--line);border-radius:14px}
    table{width:100%;border-collapse:collapse;min-width:720px}
    th,td{padding:12px 13px;text-align:start;border-bottom:1px solid var(--line);font-size:13px}
    th{background:#f8f7ff;color:#4338ca;font-weight:900}
    tr:last-child td{border-bottom:0}
    .pill{
      display:inline-block;padding:5px 9px;border-radius:999px;
      font-size:11px;font-weight:800;background:#eef2ff;color:#4338ca;
    }
    .footer-note{text-align:center;color:var(--muted);font-size:12px;margin-top:22px}
    @media(max-width:900px){
      .layout{grid-template-columns:1fr}
      .sidebar{position:static;grid-template-columns:1fr 1fr}
      .meta-strip{grid-template-columns:1fr 1fr}
      .facts-grid{grid-template-columns:1fr 1fr}
    }
    @media(max-width:620px){
      .hero-inner,.input-head{align-items:flex-start;flex-direction:column}
      .top-actions{width:100%}
      .top-actions .btn{flex:1}
      .meta-strip,.sidebar,.facts-grid,.actions-grid,.links-grid{grid-template-columns:1fr}
      .container{padding:0 12px 30px}
      .input-card{padding:18px}
      .brand h1{font-size:18px}
    }
    @media print{
      .hero,.input-card,.top-actions,.status,.footer-note{display:none!important}
      body{background:#fff}
      .container{max-width:none;margin:0;padding:0}
      .meta-strip,.report-card,.sidebar-card{box-shadow:none;break-inside:avoid}
      .layout{grid-template-columns:240px 1fr}
      .sidebar{position:static}
    }
  </style>
</head>
<body>
  <header class="hero">
    <div class="hero-inner">
      <div class="brand">
        <div class="logo">✉</div>
        <div>
          <h1>AI EMAIL ANALYZER</h1>
          <p id="subtitle">Professional Email Analysis Report</p>
        </div>
      </div>
      <div class="top-actions">
        <button class="btn btn-light" id="newBtn">＋ New Analysis</button>
        <button class="btn btn-primary" id="printBtn">⬇ Download Report</button>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="input-card">
      <div class="input-head">
        <div>
          <h2 id="inputTitle">ای میل کا تجزیہ کریں</h2>
          <p id="inputDesc">ای میل کا مکمل متن پیسٹ کریں۔ نتیجہ professional report کی شکل میں آئے گا۔</p>
        </div>
        <select id="language">
          <option value="ur">اردو</option>
          <option value="en">English</option>
          <option value="ar">العربية</option>
        </select>
      </div>

      <textarea id="emailText" maxlength="30000" placeholder="ای میل یہاں پیسٹ کریں..."></textarea>

      <div class="input-actions">
        <button class="btn btn-primary" id="analyzeBtn">تجزیہ کریں</button>
        <button class="btn btn-soft" id="clearBtn">صاف کریں</button>
      </div>
      <div id="status" class="status"></div>
    </section>

    <section id="reportRoot" class="hidden">
      <div class="meta-strip">
        <div class="meta-box">
          <div class="meta-icon">✉</div>
          <div><div class="meta-label">Email Subject</div><div class="meta-value" id="metaSubject">—</div></div>
        </div>
        <div class="meta-box">
          <div class="meta-icon">📅</div>
          <div><div class="meta-label">Received Date</div><div class="meta-value" id="metaDate">—</div></div>
        </div>
        <div class="meta-box">
          <div class="meta-icon">👤</div>
          <div><div class="meta-label">Sender</div><div class="meta-value" id="metaSender">—</div></div>
        </div>
        <div class="meta-box">
          <div class="meta-icon">⭐</div>
          <div><div class="meta-label">Importance</div><div class="meta-value" id="metaImportance">—</div></div>
        </div>
      </div>

      <div class="layout">
        <aside class="sidebar">
          <section class="sidebar-card">
            <h3>☷ TABLE OF CONTENTS</h3>
            <nav class="toc">
              <a href="#summary"><span class="num">1</span>Short Summary</a>
              <a href="#about"><span class="num">2</span>What the Email Is About</a>
              <a href="#purpose"><span class="num">3</span>Sender's Purpose</a>
              <a href="#facts"><span class="num">4</span>Key Information</a>
              <a href="#items"><span class="num">5</span>Items / Opportunities</a>
              <a href="#risks"><span class="num">6</span>Risks & Red Flags</a>
              <a href="#actions"><span class="num">7</span>Recommended Actions</a>
              <a href="#links"><span class="num">8</span>Useful Links</a>
            </nav>
          </section>

          <section class="sidebar-card">
            <h3>▤ EMAIL OVERVIEW</h3>
            <div class="overview-row"><div class="overview-key">From</div><div class="overview-val" id="ovFrom">—</div></div>
            <div class="overview-row"><div class="overview-key">To</div><div class="overview-val" id="ovTo">—</div></div>
            <div class="overview-row"><div class="overview-key">Date</div><div class="overview-val" id="ovDate">—</div></div>
            <div class="overview-row"><div class="overview-key">Type</div><div class="overview-val" id="ovType">—</div></div>
            <div class="overview-row"><div class="overview-key">Priority</div><div class="overview-val"><span class="pill" id="ovPriority">—</span></div></div>
          </section>
        </aside>

        <section class="report">
          <article class="report-card" id="summary">
            <div class="section-title"><span class="section-badge">1</span><h2>Short Summary</h2></div>
            <div class="section-body" id="summaryText"></div>
          </article>

          <article class="report-card" id="about">
            <div class="section-title"><span class="section-badge">2</span><h2>What the Email Is About</h2></div>
            <div class="section-body" id="aboutText"></div>
          </article>

          <article class="report-card" id="purpose">
            <div class="section-title"><span class="section-badge">3</span><h2>Sender's Main Purpose</h2></div>
            <div class="section-body" id="purposeText"></div>
          </article>

          <article class="report-card" id="facts">
            <div class="section-title"><span class="section-badge">4</span><h2>Key Information</h2></div>
            <div class="facts-grid" id="factsGrid"></div>
          </article>

          <article class="report-card" id="items">
            <div class="section-title"><span class="section-badge">5</span><h2>Items / Opportunities</h2></div>
            <div id="itemsArea"></div>
          </article>

          <article class="report-card" id="risks">
            <div class="section-title"><span class="section-badge">6</span><h2>Risks, Missing Information & Red Flags</h2></div>
            <ul class="list-clean risk-list" id="risksList"></ul>
          </article>

          <article class="report-card" id="actions">
            <div class="section-title"><span class="section-badge">7</span><h2>Recommended Actions</h2></div>
            <div class="actions-grid" id="actionsGrid"></div>
          </article>

          <article class="report-card" id="links">
            <div class="section-title"><span class="section-badge">8</span><h2>Official & Useful Links</h2></div>
            <div class="links-grid" id="linksGrid"></div>
          </article>
        </section>
      </div>

      <div class="footer-note">AI-generated analysis may contain inaccuracies. Verify important information before taking action.</div>
    </section>
  </main>

<script>
const $ = id => document.getElementById(id);

const ui = {
  ur:{
    dir:"rtl", subtitle:"پروفیشنل ای میل تجزیاتی رپورٹ",
    inputTitle:"ای میل کا تجزیہ کریں",
    inputDesc:"ای میل کا مکمل متن پیسٹ کریں۔ نتیجہ professional report کی شکل میں آئے گا۔",
    placeholder:"ای میل یہاں پیسٹ کریں...",
    analyze:"تجزیہ کریں", clear:"صاف کریں",
    working:"تجزیہ اور ویب تصدیق جاری ہے...",
    empty:"براہِ کرم ای میل کا متن پیسٹ کریں۔"
  },
  en:{
    dir:"ltr", subtitle:"Professional Email Analysis Report",
    inputTitle:"Analyze an Email",
    inputDesc:"Paste the complete email. The result will appear as a structured professional report.",
    placeholder:"Paste the complete email here...",
    analyze:"Analyze Email", clear:"Clear",
    working:"Analyzing and checking public information...",
    empty:"Please paste the email text."
  },
  ar:{
    dir:"rtl", subtitle:"تقرير احترافي لتحليل البريد الإلكتروني",
    inputTitle:"تحليل البريد الإلكتروني",
    inputDesc:"ألصق نص البريد الكامل. ستظهر النتيجة كتقرير احترافي منظم.",
    placeholder:"ألصق البريد الكامل هنا...",
    analyze:"تحليل البريد", clear:"مسح",
    working:"جارٍ التحليل والتحقق من المعلومات العامة...",
    empty:"يرجى لصق نص البريد الإلكتروني."
  }
};

function setLanguage(){
  const lang=$("language").value, t=ui[lang];
  document.documentElement.lang=lang;
  document.documentElement.dir=t.dir;
  $("subtitle").textContent=t.subtitle;
  $("inputTitle").textContent=t.inputTitle;
  $("inputDesc").textContent=t.inputDesc;
  $("emailText").placeholder=t.placeholder;
  $("analyzeBtn").textContent=t.analyze;
  $("clearBtn").textContent=t.clear;
}

function textOrDash(value){
  return value && String(value).trim() ? value : "—";
}

function escapeHtml(value){
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  })[ch]);
}

function renderList(target, values, fallback){
  target.innerHTML="";
  const arr=Array.isArray(values) && values.length ? values : [fallback];
  arr.forEach(v=>{
    const li=document.createElement("li");
    li.textContent=textOrDash(v);
    target.appendChild(li);
  });
}

function renderFacts(facts){
  $("factsGrid").innerHTML="";
  const list=Array.isArray(facts) && facts.length ? facts : [{label:"Information",value:"Not available"}];
  list.slice(0,8).forEach(f=>{
    const div=document.createElement("div");
    div.className="fact";
    div.innerHTML=`<div class="label">${escapeHtml(textOrDash(f.label))}</div><div class="value">${escapeHtml(textOrDash(f.value))}</div>`;
    $("factsGrid").appendChild(div);
  });
}

function safeHttpUrl(value){
  try{
    const url=new URL(String(value||"").trim());
    return (url.protocol==="http:" || url.protocol==="https:") ? url.href : "";
  }catch(_){ return ""; }
}

function renderItems(items){
  const area=$("itemsArea");
  area.innerHTML="";
  if(!Array.isArray(items) || !items.length){
    area.innerHTML='<div class="section-body">No structured items or opportunities were found in this email.</div>';
    return;
  }

  const preferred=["title","company","location","price_or_salary","status","type"];
  const allKeys=[];
  items.forEach(item=>Object.keys(item||{}).forEach(k=>{
    if(!["url","link","item_url"].includes(k) && !allKeys.includes(k)) allKeys.push(k);
  }));
  const shown=[...preferred.filter(k=>allKeys.includes(k)),...allKeys.filter(k=>!preferred.includes(k))].slice(0,7);
  const hasAnyLink=items.some(item=>safeHttpUrl(item?.url || item?.link || item?.item_url));

  let html='<div class="table-wrap"><table><thead><tr>';
  shown.forEach(k=>html+=`<th>${escapeHtml(k.replaceAll("_"," "))}</th>`);
  if(hasAnyLink) html+='<th>Link</th>';
  html+='</tr></thead><tbody>';

  items.forEach(item=>{
    const itemUrl=safeHttpUrl(item?.url || item?.link || item?.item_url);
    html+='<tr>';
    shown.forEach(k=>{
      let val=item?.[k];
      if(Array.isArray(val)) val=val.join(", ");
      const clean=escapeHtml(textOrDash(val));
      if(k==="title" && itemUrl){
        html+=`<td><a class="item-link" href="${escapeHtml(itemUrl)}" target="_blank" rel="noopener noreferrer">${clean}</a></td>`;
      }else{
        html+=`<td>${clean}</td>`;
      }
    });
    if(hasAnyLink){
      html+=itemUrl
        ? `<td><a class="open-link-btn" href="${escapeHtml(itemUrl)}" target="_blank" rel="noopener noreferrer">Open ↗</a></td>`
        : '<td><span class="no-link">Not available</span></td>';
    }
    html+='</tr>';
  });
  html+='</tbody></table></div>';
  area.innerHTML=html;
}

function renderActions(actions){
  $("actionsGrid").innerHTML="";
  const list=Array.isArray(actions) && actions.length ? actions : [{title:"Review the email",detail:"Verify the key information before taking action."}];
  list.forEach(a=>{
    const div=document.createElement("div");
    div.className="action-box";
    div.innerHTML=`<strong>${escapeHtml(textOrDash(a.title))}</strong><span>${escapeHtml(textOrDash(a.detail))}</span>`;
    $("actionsGrid").appendChild(div);
  });
}

function renderLinks(links){
  $("linksGrid").innerHTML="";
  const valid=(Array.isArray(links)?links:[]).filter(x=>x && x.url);
  if(!valid.length){
    $("linksGrid").innerHTML='<div class="section-body">No verified public links were available.</div>';
    return;
  }
  valid.forEach(l=>{
    const a=document.createElement("a");
    a.className="link-card";
    a.href=l.url;
    a.target="_blank";
    a.rel="noopener noreferrer";
    a.innerHTML=`${escapeHtml(textOrDash(l.title))}<small>${escapeHtml(textOrDash(l.description || l.url))}</small>`;
    $("linksGrid").appendChild(a);
  });
}

function renderReport(data){
  const m=data.metadata||{};
  $("metaSubject").textContent=textOrDash(m.subject);
  $("metaDate").textContent=textOrDash(m.date);
  $("metaSender").textContent=textOrDash(m.sender);
  $("metaImportance").textContent=textOrDash(m.importance);

  $("ovFrom").textContent=textOrDash(m.sender);
  $("ovTo").textContent=textOrDash(m.recipient);
  $("ovDate").textContent=textOrDash(m.date);
  $("ovType").textContent=textOrDash(m.email_type);
  $("ovPriority").textContent=textOrDash(m.importance);

  $("summaryText").textContent=textOrDash(data.short_summary);
  $("aboutText").textContent=textOrDash(data.what_email_is_about);
  $("purposeText").textContent=textOrDash(data.sender_purpose);

  renderFacts(data.key_information);
  renderItems(data.items);
  renderList($("risksList"),data.risks,"No major risk was identified, but important details should still be verified.");
  renderActions(data.recommended_actions);
  renderLinks(data.links);

  $("reportRoot").classList.remove("hidden");
  setTimeout(()=>$("reportRoot").scrollIntoView({behavior:"smooth",block:"start"}),150);
}

$("language").addEventListener("change",setLanguage);
$("printBtn").onclick=()=>window.print();
$("newBtn").onclick=()=>{
  $("emailText").value="";
  $("reportRoot").classList.add("hidden");
  window.scrollTo({top:0,behavior:"smooth"});
};
$("clearBtn").onclick=()=>{
  $("emailText").value="";
  $("status").textContent="";
  $("reportRoot").classList.add("hidden");
};

$("analyzeBtn").onclick=async()=>{
  const email_text=$("emailText").value.trim();
  const language=$("language").value;
  const t=ui[language];

  if(!email_text){
    $("status").className="status error";
    $("status").textContent=t.empty;
    return;
  }

  $("analyzeBtn").disabled=true;
  $("status").className="status";
  $("status").textContent=t.working;
  $("reportRoot").classList.add("hidden");

  try{
    const response=await fetch("/analyze",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({email_text,language})
    });
    const data=await response.json();
    if(!response.ok) throw new Error(data.error||"Analysis failed");
    renderReport(data);
    $("status").textContent="";
  }catch(err){
    $("status").className="status error";
    $("status").textContent=err.message;
  }finally{
    $("analyzeBtn").disabled=false;
  }
};

setLanguage();
</script>
</body>
</html>
"""

def extract_json(text: str) -> dict:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))

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
    visible_urls = re.findall(r'https?://[^\s<>"\']+', email_text)
    visible_urls_text = "\n".join(dict.fromkeys(url.rstrip(').,;]') for url in visible_urls)) or "No visible URLs detected"

    prompt = f"""
Analyze the email below carefully and answer in {answer_language}.

Return ONLY valid JSON. Do not use markdown or code fences.

Use this exact JSON structure:
{{
  "metadata": {{
    "subject": "",
    "sender": "",
    "recipient": "",
    "date": "",
    "email_type": "",
    "importance": "Low, Medium, or High"
  }},
  "short_summary": "",
  "what_email_is_about": "",
  "sender_purpose": "",
  "key_information": [
    {{"label": "", "value": ""}}
  ],
  "items": [
    {{
      "title": "",
      "company": "",
      "location": "",
      "price_or_salary": "",
      "type": "",
      "status": "",
      "url": ""
    }}
  ],
  "risks": [""],
  "recommended_actions": [
    {{"title": "", "detail": ""}}
  ],
  "links": [
    {{"title": "", "url": "", "description": ""}}
  ]
}}

Rules:
- Extract metadata only when visible in the email.
- If a value is unavailable, use "Not provided".
- Put products, jobs, services, offers, invoices, appointments, or other repeated entries in "items".
- Keep each item as a simple flat object.
- For every item, copy its exact destination URL from the email into the "url" field when available.
- If the email contains a visible URL related to an item, preserve that exact URL; do not replace it with a homepage.
- If an item has no URL in the email and no verified direct public URL, use an empty string for "url".
- Include 4 to 8 useful key information entries.
- Include practical recommended actions.
- Include only official or trustworthy public links.
- Do not invent URLs. If a trustworthy URL cannot be confirmed, omit it.
- Clearly identify suspicious claims, missing information, phishing indicators, unknown domains, payment requests, login requests, or attachment risks.
- Do not guess.

VISIBLE URLS DETECTED IN THE EMAIL:
{visible_urls_text}

EMAIL:
{email_text}
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2,
            ),
        )
        parsed = extract_json(response.text or "")
        return jsonify(parsed)
    except Exception as exc:
        return jsonify({"error": f"Analysis failed: {str(exc)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
