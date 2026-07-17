#!/usr/bin/env python3
"""Enhanced AppAtlas viewer.

Consumes per-screen structured records (`<section>/screens.json`) + thumbnails
(`_artifact/thumbs/**`) + section specs (`<section>/spec.md`) and emits a single
self-contained HTML:

  - auto-built tree (section -> page -> subtab -> modal)
  - Mobbin-style faceted tag rail (page types / flows / patterns / states) + counts
  - per-screen structure panel (pageType, features, elements, states, tags)
  - semantic links (typed edges) rendered as clickable in/out lists
  - a Flows graph view (nodes = screens, edges = links, layered per flow)

Usage: python3 _artifact/build_atlas.py  -> writes _artifact/atlas.html
"""
import base64, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THUMBS = os.path.join(ROOT, "_artifact", "thumbs")
OUT = os.path.join(ROOT, "_artifact", "atlas.html")

SECTION_TITLES = {
    "01-onboarding": "Onboarding", "02-pricing-paywall": "Pricing & Paywall",
    "03-dashboard": "Dashboard", "04-actions": "Actions", "05-prompt-explorer": "Prompt Explorer",
    "06-mcp-and-api": "MCP & API", "07-monitoring": "Monitoring", "08-sources": "Sources",
    "09-content-automation": "Content Automation", "10-agent-analytics": "Agent Analytics",
    "11-brand-hub": "Brand Hub", "12-settings": "Org Settings", "13-misc": "App Shell",
}

def stem(fn): return re.sub(r"\.(jpg|jpeg|png|gif)$", "", fn, flags=re.I)

def load_records():
    recs, warnings = [], []
    for sec in sorted(SECTION_TITLES):
        p = os.path.join(ROOT, sec, "screens.json")
        if not os.path.exists(p):
            continue
        try:
            data = json.load(open(p))
        except Exception as e:
            warnings.append(f"{sec}/screens.json parse error: {e}"); continue
        for r in data:
            r.setdefault("section", sec)
            r.setdefault("sectionTitle", SECTION_TITLES.get(sec, sec))
            if "screenshot" not in r or "id" not in r:
                warnings.append(f"{sec}: record missing id/screenshot: {r.get('title','?')}"); continue
            thumb = os.path.join(THUMBS, sec, r["screenshot"])
            if not os.path.exists(thumb):
                warnings.append(f"{sec}: thumb missing for {r['screenshot']}"); continue
            with open(thumb, "rb") as f:
                r["d"] = base64.b64encode(f.read()).decode()
            recs.append(r)
    return recs, warnings

def load_specs():
    specs = {}
    for sec in SECTION_TITLES:
        p = os.path.join(ROOT, sec, "spec.md")
        if os.path.exists(p):
            specs[sec] = open(p).read()
    return specs

def prune_links(recs, warnings):
    ids = {r["id"] for r in recs}
    for r in recs:
        good = []
        for l in r.get("links", []) or []:
            if l.get("to") in ids:
                good.append(l)
            else:
                warnings.append(f"{r['id']}: dangling link -> {l.get('to')}")
        r["links"] = good
    return recs

def main():
    recs, warnings = load_records()
    if not recs:
        print("No screens.json records found. Run the enrichment pass first.")
        print("Sections looked at:", ", ".join(SECTION_TITLES))
        return
    recs = prune_links(recs, warnings)
    specs = load_specs()

    # facet counts
    def bump(d, k): d[k] = d.get(k, 0) + 1
    pt, fl, tg, st = {}, {}, {}, {}
    for r in recs:
        bump(pt, r.get("pageType", "other"))
        for x in r.get("flows", []) or []: bump(fl, x)
        for x in r.get("tags", []) or []: bump(tg, x)
        for x in r.get("states", []) or []: bump(st, x)
    facets = {
        "Page types": sorted(pt.items(), key=lambda kv: (-kv[1], kv[0])),
        "Flows": sorted(fl.items(), key=lambda kv: (-kv[1], kv[0])),
        "Patterns": sorted(tg.items(), key=lambda kv: (-kv[1], kv[0])),
        "States": sorted(st.items(), key=lambda kv: (-kv[1], kv[0])),
    }

    # strip image out of the JSON payload we hand JS for logic; keep a separate id->dataURI map
    imgs = {r["id"]: r["d"] for r in recs}
    lean = []
    for r in recs:
        lean.append({k: r[k] for k in r if k != "d"})

    def js(o): return json.dumps(o, ensure_ascii=True).replace("</", "<\\/")

    total, nsec = len(recs), len({r["section"] for r in recs})
    ntags = len(tg) + len(pt) + len(fl)
    nflows = len(fl)
    nlinks = sum(len(r.get("links", []) or []) for r in recs)

    page = TEMPLATE
    page = page.replace("__SCREENS__", js(lean))
    page = page.replace("__IMGS__", js(imgs))
    page = page.replace("__SPECS__", js(specs))
    page = page.replace("__FACETS__", js(facets))
    page = page.replace("__TITLES__", js(SECTION_TITLES))
    page = page.replace("__TOTAL__", str(total)).replace("__NSEC__", str(nsec))
    page = page.replace("__NTAGS__", str(ntags)).replace("__NFLOWS__", str(nflows))
    page = page.replace("__NLINKS__", str(nlinks))

    with open(OUT, "w") as f:
        f.write(page)
    print(f"wrote {OUT}: {os.path.getsize(OUT)/1e6:.1f} MB, {total} screens, {nlinks} links, {ntags} tags")
    if warnings:
        print(f"{len(warnings)} warning(s):")
        for w in warnings[:25]:
            print("  -", w)


TEMPLATE = r"""<title>AppAtlas viewer</title>
<style>
:root{
  --bg:#0D1216;--panel:#151C22;--panel2:#101720;--ink:#ECEFF2;--muted:#93A0AC;--line:#232E37;
  --accent:#EC4E86;--accent-ink:#1A0710;--chip:#1A2129;--good:#3FB27F;--warn:#E0A44B;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;--mono:ui-monospace,"SF Mono",Menlo,monospace;
}
@media (prefers-color-scheme: light){:root{
  --bg:#F3F4F2;--panel:#FFF;--panel2:#FAFAF8;--ink:#151A1E;--muted:#586069;--line:#E1E4E1;
  --accent:#C42367;--accent-ink:#FFF;--chip:#EEF1EE;--good:#1E8E5A;--warn:#9A6314;
}}
:root[data-theme=dark]{--bg:#0D1216;--panel:#151C22;--panel2:#101720;--ink:#ECEFF2;--muted:#93A0AC;--line:#232E37;--accent:#EC4E86;--accent-ink:#1A0710;--chip:#1A2129;}
:root[data-theme=light]{--bg:#F3F4F2;--panel:#FFF;--panel2:#FAFAF8;--ink:#151A1E;--muted:#586069;--line:#E1E4E1;--accent:#C42367;--accent-ink:#FFF;--chip:#EEF1EE;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}
.mono{font-family:var(--mono)}
a{color:var(--accent);text-decoration:none} a:hover{text-decoration:underline}
header.top{padding:18px 22px 14px;border-bottom:1px solid var(--line)}
header.top h1{margin:0 0 4px;font-size:19px;letter-spacing:-.02em}
header.top p{margin:0;color:var(--muted);font-size:13px;max-width:80ch}
.stats{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.stat{background:var(--chip);border:1px solid var(--line);border-radius:6px;padding:3px 10px;font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.stat b{color:var(--ink)}
.layout{display:grid;grid-template-columns:250px 220px 1fr;min-height:calc(100vh - 84px)}
@media(max-width:1000px){.layout{grid-template-columns:1fr}.rail,.facets{display:none}}
.rail,.facets{border-right:1px solid var(--line);padding:14px 10px 60px;overflow-y:auto;max-height:calc(100vh - 84px);position:sticky;top:0}
.rail h2,.facets h2{font-size:10.5px;text-transform:uppercase;letter-spacing:.09em;color:var(--muted);margin:6px 8px;font-weight:600}
.tnode{display:block;width:100%;text-align:left;background:none;border:0;color:var(--ink);font:inherit;font-size:13px;padding:4px 8px;border-radius:6px;cursor:pointer}
.tnode:hover{background:var(--chip)} .tnode.on{background:var(--accent);color:var(--accent-ink)}
.tnode .n{float:right;color:var(--muted);font-size:11px;font-variant-numeric:tabular-nums}
.tnode.on .n{color:inherit;opacity:.8}
details.tg{margin:1px 0} details.tg>summary{list-style:none;cursor:pointer} details.tg>summary::-webkit-details-marker{display:none}
details.tg>summary .tnode::before{content:"\25B8";display:inline-block;width:13px;color:var(--muted);transition:transform .12s}
details.tg[open]>summary .tnode::before{transform:rotate(90deg)}
.tkids{margin-left:14px;border-left:1px solid var(--line);padding-left:3px}
.fgroup{margin-bottom:14px}
.chiprow{display:flex;flex-wrap:wrap;gap:5px;padding:0 6px}
.fchip{font-family:var(--mono);font-size:11px;background:var(--chip);border:1px solid var(--line);border-radius:6px;padding:3px 7px;cursor:pointer;color:var(--ink);display:inline-flex;gap:5px;align-items:center}
.fchip:hover{border-color:var(--accent)} .fchip.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.fchip .c{opacity:.6;font-size:10px} .fchip.on .c{opacity:.85}
main{min-width:0;padding:0 20px 80px}
.toolbar{position:sticky;top:0;z-index:5;background:var(--bg);padding:12px 0 10px;border-bottom:1px solid var(--line);display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.toolbar input{flex:1 1 200px;max-width:320px;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:7px 11px;font:inherit;font-size:13px}
.toolbar input:focus{outline:2px solid var(--accent);outline-offset:1px}
.vtabs{display:flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.vtabs button{background:var(--panel);border:0;color:var(--muted);font:inherit;font-size:13px;font-weight:500;padding:7px 14px;cursor:pointer}
.vtabs button.on{background:var(--accent);color:var(--accent-ink)}
.count{margin-left:auto;color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
.active{display:flex;gap:6px;flex-wrap:wrap;align-items:center;padding:10px 0 0;min-height:0}
.active .lbl{font-size:12px;color:var(--muted)}
.pill{font-family:var(--mono);font-size:11px;background:var(--accent);color:var(--accent-ink);border:0;border-radius:6px;padding:3px 8px;cursor:pointer}
.pill.clear{background:var(--chip);color:var(--ink);border:1px solid var(--line)}
.grid{margin-top:14px;display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;cursor:zoom-in;transition:border-color .12s}
.card:hover{border-color:var(--accent)}
.card img{display:block;width:100%;height:auto;background:#fff}
.card .cap{padding:8px 10px;border-top:1px solid var(--line)}
.card .cap .t{font-size:12.5px;font-weight:600;letter-spacing:-.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card .cap .m{display:flex;gap:5px;flex-wrap:wrap;margin-top:5px}
.tag{font-family:var(--mono);font-size:10px;background:var(--chip);border:1px solid var(--line);border-radius:4px;padding:1px 5px;color:var(--muted)}
.tag.pt{color:var(--accent);border-color:var(--accent)}
/* detail */
.sheet{position:fixed;inset:0;z-index:50;display:none}
.sheet.open{display:block}
.sheet .bg{position:absolute;inset:0;background:rgba(8,11,14,.7)}
.sheet .panel{position:absolute;top:0;right:0;bottom:0;width:min(720px,94vw);background:var(--bg);border-left:1px solid var(--line);overflow-y:auto;box-shadow:-20px 0 60px rgba(0,0,0,.4)}
.sheet .panel .hd{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:14px 20px;display:flex;align-items:center;gap:10px;z-index:2}
.sheet .panel .hd h3{margin:0;font-size:16px;letter-spacing:-.01em;flex:1}
.sheet .x{background:var(--chip);border:1px solid var(--line);border-radius:7px;color:var(--ink);font:inherit;padding:5px 10px;cursor:pointer}
.sheet .bd{padding:18px 20px 60px}
.sheet .bd img{width:100%;border:1px solid var(--line);border-radius:10px;display:block;margin-bottom:16px}
.kv{display:grid;grid-template-columns:110px 1fr;gap:6px 12px;font-size:13px;margin-bottom:16px}
.kv .k{color:var(--muted)}
.sec-h{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:18px 0 8px;font-weight:600}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.el{border:1px solid var(--line);border-radius:8px;overflow:hidden}
.el .r{display:grid;grid-template-columns:110px 150px 1fr;gap:10px;padding:8px 12px;border-top:1px solid var(--line);font-size:12.5px}
.el .r:first-child{border-top:0}
.el .r .ty{font-family:var(--mono);font-size:11px;color:var(--accent)}
.el .r .lb{font-weight:600}
.el .r .bh{color:var(--muted)}
.lk{display:flex;flex-direction:column;gap:6px}
.lk a{display:flex;align-items:center;gap:9px;border:1px solid var(--line);border-radius:8px;padding:8px 11px;color:var(--ink);text-decoration:none;background:var(--panel)}
.lk a:hover{border-color:var(--accent);text-decoration:none}
.lk .et{font-family:var(--mono);font-size:10px;color:var(--accent-ink);background:var(--accent);border-radius:4px;padding:1px 6px}
.lk .via{color:var(--muted);font-size:12px;margin-left:auto}
.lk img{width:52px;height:34px;object-fit:cover;object-position:top;border-radius:4px;border:1px solid var(--line)}
.specbox{margin-top:10px}.specbox summary{cursor:pointer;color:var(--accent);font-size:13px}
.specbox pre{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px 14px;white-space:pre-wrap;font-size:11.5px;max-height:340px;overflow:auto}
/* flows graph */
.flows{margin-top:16px;display:flex;flex-direction:column;gap:14px}
.flow{border:1px solid var(--line);border-radius:12px;background:var(--panel2);overflow:hidden}
.flow>summary{list-style:none;cursor:pointer;padding:12px 16px;display:flex;align-items:center;gap:10px;font-weight:600}
.flow>summary::-webkit-details-marker{display:none}
.flow>summary .fn{font-family:var(--mono);font-size:11px;color:var(--muted);margin-left:auto}
.flow .canvas{overflow-x:auto;padding:8px 12px 16px}
.gnode{position:absolute;width:150px;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden;cursor:pointer;transition:border-color .12s}
.gnode:hover{border-color:var(--accent)}
.gnode img{width:100%;height:60px;object-fit:cover;object-position:top;display:block}
.gnode .gl{padding:5px 7px;font-size:11px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-top:1px solid var(--line)}
.gwrap{position:relative}
.gwrap svg{position:absolute;inset:0;pointer-events:none;overflow:visible}
.gwrap path{fill:none;stroke:var(--line);stroke-width:1.5}
.empty{color:var(--muted);padding:40px;text-align:center}
</style>

<header class="top">
  <h1>AppAtlas &mdash; <span id="appname">app atlas</span></h1>
  <p>Structured walkthrough: an auto-built tree, faceted Mobbin-style tags, per-screen structure and features, and semantic links between screens. Filter by tree node or tag; open any screen for its full read; switch to Flows for the graph.</p>
  <div class="stats">
    <span class="stat"><b>__TOTAL__</b> screens</span>
    <span class="stat"><b>__NSEC__</b> sections</span>
    <span class="stat"><b>__NTAGS__</b> tags</span>
    <span class="stat"><b>__NFLOWS__</b> flows</span>
    <span class="stat"><b>__NLINKS__</b> links</span>
  </div>
</header>

<div class="layout">
  <nav class="rail" id="tree"><h2>App structure</h2></nav>
  <aside class="facets" id="facets"><h2>Filter by tag</h2></aside>
  <main>
    <div class="toolbar">
      <div class="vtabs"><button data-v="gallery" class="on">Gallery</button><button data-v="flows">Flows</button></div>
      <input id="q" type="search" placeholder="Search screens, tags, features...">
      <span class="count" id="count"></span>
    </div>
    <div class="active" id="active"></div>
    <div id="galleryView"><div class="grid" id="grid"></div></div>
    <div id="flowsView" style="display:none"><div class="flows" id="flows"></div></div>
  </main>
</div>

<div class="sheet" id="sheet"><div class="bg" id="sheetbg"></div><div class="panel"><div class="hd"><h3 id="sh-title"></h3><button class="x" id="sh-x">Close</button></div><div class="bd" id="sh-bd"></div></div></div>

<script>
const SCREENS=__SCREENS__, IMG=__IMGS__, SPECS=__SPECS__, FACETS=__FACETS__, TITLES=__TITLES__;
const byId={}; SCREENS.forEach(s=>byId[s.id]=s);
// incoming links
const incoming={}; SCREENS.forEach(s=>(s.links||[]).forEach(l=>{(incoming[l.to]=incoming[l.to]||[]).push({from:s.id,type:l.type,via:l.via})}));
const el=(t,c,h)=>{const e=document.createElement(t);if(c)e.className=c;if(h!=null)e.innerHTML=h;return e};

// ---- state ----
let view="gallery";
let tree=null;                 // {section,page,subtab}
const sel={"Page types":new Set(),"Flows":new Set(),"Patterns":new Set(),"States":new Set()};
const FKEY={"Page types":s=>[s.pageType],"Flows":s=>s.flows||[],"Patterns":s=>s.tags||[],"States":s=>s.states||[]};

// ---- tree ----
function buildTree(){
  const t=document.getElementById("tree");
  const secs={};
  SCREENS.forEach(s=>{
    const sc=secs[s.section]=secs[s.section]||{title:s.sectionTitle,pages:{},n:0}; sc.n++;
    const pg=sc.pages[s.page||"—"]=sc.pages[s.page||"—"]||{subs:{},n:0}; pg.n++;
    const key=s.modal?("modal: "+s.modal):(s.subtab||"");
    if(key){const sb=pg.subs[key]=pg.subs[key]||0; pg.subs[key]++;}
  });
  Object.keys(secs).sort().forEach(secId=>{
    const sc=secs[secId];
    const d=el("details","tg"); const sm=el("summary");
    sm.appendChild(mkNode(sc.title,sc.n,()=>setTree({section:secId})));
    d.appendChild(sm);
    const kids=el("div","tkids");
    Object.keys(sc.pages).forEach(pgName=>{
      const pg=sc.pages[pgName]; const subKeys=Object.keys(pg.subs);
      if(subKeys.length){
        const pd=el("details","tg"); const ps=el("summary");
        ps.appendChild(mkNode(pgName,pg.n,()=>setTree({section:secId,page:pgName})));
        pd.appendChild(ps); const pk=el("div","tkids");
        subKeys.forEach(sk=>pk.appendChild(mkNode(sk,pg.subs[sk],()=>setTree({section:secId,page:pgName,subtab:sk}))));
        pd.appendChild(pk); kids.appendChild(pd);
      } else {
        kids.appendChild(mkNode(pgName,pg.n,()=>setTree({section:secId,page:pgName})));
      }
    });
    d.appendChild(kids); t.appendChild(d);
  });
}
function mkNode(label,n,fn){
  const b=el("button","tnode",label+' <span class="n">'+n+'</span>');
  b.dataset.k=label; b.onclick=e=>{e.stopPropagation();e.preventDefault();fn();}; return b;
}
function setTree(t){
  const same=tree&&t&&tree.section===t.section&&tree.page===t.page&&tree.subtab===t.subtab;
  tree=same?null:t; render();
}

// ---- facets ----
function buildFacets(){
  const host=document.getElementById("facets");
  Object.keys(FACETS).forEach(g=>{
    if(!FACETS[g].length)return;
    const wrap=el("div","fgroup"); wrap.appendChild(el("h2",null,g));
    const row=el("div","chiprow");
    FACETS[g].forEach(([val,c])=>{
      const chip=el("button","fchip",val+' <span class="c">'+c+'</span>'); chip.dataset.g=g; chip.dataset.v=val;
      chip.onclick=()=>{sel[g].has(val)?sel[g].delete(val):sel[g].add(val);render();};
      row.appendChild(chip);
    });
    wrap.appendChild(row); host.appendChild(wrap);
  });
}

// ---- filtering ----
function matchTree(s){return !tree || (s.section===tree.section && (!tree.page||s.page===tree.page) && (!tree.subtab || (tree.subtab.startsWith("modal: ")? ("modal: "+(s.modal||""))===tree.subtab : s.subtab===tree.subtab)));}
function matchFacets(s){
  for(const g of Object.keys(sel)){ if(!sel[g].size)continue; const vals=FKEY[g](s)||[]; if(!vals.some(v=>sel[g].has(v)))return false; }
  return true;
}
function matchQ(s,q){ if(!q)return true; const hay=(s.title+" "+s.section+" "+(s.pageType||"")+" "+(s.flows||[]).join(" ")+" "+(s.tags||[]).join(" ")+" "+(s.features||[]).join(" ")+" "+(s.summary||"")).toLowerCase(); return hay.includes(q); }
function filtered(){ const q=document.getElementById("q").value.trim().toLowerCase(); return SCREENS.filter(s=>matchTree(s)&&matchFacets(s)&&matchQ(s,q)); }

// ---- render ----
function render(){
  document.querySelectorAll(".fchip").forEach(c=>c.classList.toggle("on",sel[c.dataset.g].has(c.dataset.v)));
  document.querySelectorAll(".tnode").forEach(b=>b.classList.remove("on"));
  const fs=filtered();
  document.getElementById("count").textContent=fs.length+" / "+SCREENS.length+" screens";
  renderActive();
  if(view==="gallery")renderGallery(fs); else renderFlows(fs);
}
function renderActive(){
  const a=document.getElementById("active"); a.innerHTML="";
  const items=[];
  if(tree)items.push({label:"tree: "+(tree.subtab||tree.page||TITLES[tree.section]||tree.section),clear:()=>{tree=null;render();}});
  Object.keys(sel).forEach(g=>sel[g].forEach(v=>items.push({label:v,clear:()=>{sel[g].delete(v);render();}})));
  if(!items.length)return;
  a.appendChild(el("span","lbl","Active:"));
  items.forEach(it=>{const p=el("button","pill",it.label+" ×");p.onclick=it.clear;a.appendChild(p);});
  const c=el("button","pill clear","Clear all");c.onclick=()=>{tree=null;Object.keys(sel).forEach(g=>sel[g].clear());render();};a.appendChild(c);
}
function tagChips(s){
  const out=[]; if(s.pageType)out.push('<span class="tag pt">'+s.pageType+'</span>');
  (s.tags||[]).slice(0,3).forEach(t=>out.push('<span class="tag">'+t+'</span>')); return out.join("");
}
function renderGallery(fs){
  const g=document.getElementById("grid"); g.innerHTML="";
  if(!fs.length){g.innerHTML='<div class="empty">No screens match these filters.</div>';return;}
  const frag=document.createDocumentFragment();
  fs.forEach(s=>{
    const c=el("figure","card");
    c.innerHTML='<img loading="lazy" src="data:image/jpeg;base64,'+IMG[s.id]+'" alt="'+esc(s.title)+'"><div class="cap"><div class="t">'+esc(s.title)+'</div><div class="m">'+tagChips(s)+'</div></div>';
    c.onclick=()=>openSheet(s.id); frag.appendChild(c);
  });
  g.appendChild(frag);
}
function esc(x){return (x||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}

// ---- detail sheet ----
function openSheet(id){
  const s=byId[id]; if(!s)return;
  document.getElementById("sh-title").textContent=s.title;
  const bd=document.getElementById("sh-bd");
  let h='<img src="data:image/jpeg;base64,'+IMG[id]+'" alt="'+esc(s.title)+'">';
  h+='<div class="kv">';
  h+='<div class="k">Section</div><div>'+esc(s.sectionTitle||s.section)+'</div>';
  if(s.page)h+='<div class="k">Page</div><div>'+esc(s.page)+(s.subtab?(' &middot; '+esc(s.subtab)):'')+(s.modal?(' &middot; modal: '+esc(s.modal)):'')+'</div>';
  h+='<div class="k">Page type</div><div><span class="tag pt">'+esc(s.pageType||'other')+'</span></div>';
  if((s.flows||[]).length)h+='<div class="k">Flows</div><div class="chips">'+s.flows.map(f=>'<span class="tag">'+esc(f)+'</span>').join('')+'</div>';
  if((s.states||[]).length)h+='<div class="k">States</div><div class="chips">'+s.states.map(f=>'<span class="tag">'+esc(f)+'</span>').join('')+'</div>';
  if(s.route)h+='<div class="k">Route</div><div class="mono" style="font-size:12px">'+esc(s.route)+'</div>';
  h+='</div>';
  if(s.summary)h+='<p style="color:var(--muted);margin:0 0 4px">'+esc(s.summary)+'</p>';
  if((s.features||[]).length){h+='<div class="sec-h">Features</div><div class="chips">'+s.features.map(f=>'<span class="tag">'+esc(f)+'</span>').join('')+'</div>';}
  if((s.tags||[]).length){h+='<div class="sec-h">Pattern tags</div><div class="chips">'+s.tags.map(f=>'<button class="tag" style="cursor:pointer" onclick="jumpTag(\''+f.replace(/'/g,"")+'\')">'+esc(f)+'</button>').join('')+'</div>';}
  if((s.elements||[]).length){
    h+='<div class="sec-h">Elements</div><div class="el">';
    s.elements.forEach(e=>{h+='<div class="r"><div class="ty">'+esc(e.type||'')+'</div><div class="lb">'+esc(e.label||'')+'</div><div class="bh">'+esc(e.behavior||'')+'</div></div>';});
    h+='</div>';
  }
  const outs=s.links||[], ins=incoming[id]||[];
  if(outs.length){h+='<div class="sec-h">Links out</div><div class="lk">'+outs.map(l=>linkRow(l.to,l.type,l.via)).join('')+'</div>';}
  if(ins.length){h+='<div class="sec-h">Reached from</div><div class="lk">'+ins.map(l=>linkRow(l.from,l.type,l.via)).join('')+'</div>';}
  if(SPECS[s.section]){h+='<details class="specbox"><summary>Section behavior spec</summary><pre>'+esc(SPECS[s.section])+'</pre></details>';}
  bd.innerHTML=h; bd.scrollTop=0;
  document.getElementById("sheet").classList.add("open");
}
function linkRow(tid,type,via){const t=byId[tid];if(!t)return '';return '<a href="#" onclick="openSheet(\''+tid.replace(/'/g,"")+'\');return false"><img src="data:image/jpeg;base64,'+IMG[tid]+'"><span class="et">'+esc(type||'')+'</span><span>'+esc(t.title)+'</span>'+(via?'<span class="via">'+esc(via)+'</span>':'')+'</a>';}
function jumpTag(t){document.getElementById("sheet").classList.remove("open");Object.keys(sel).forEach(g=>sel[g].clear());tree=null;if(FACETS["Patterns"].some(x=>x[0]===t))sel["Patterns"].add(t);setView("gallery");render();}
document.getElementById("sh-x").onclick=()=>document.getElementById("sheet").classList.remove("open");
document.getElementById("sheetbg").onclick=()=>document.getElementById("sheet").classList.remove("open");
addEventListener("keydown",e=>{if(e.key==="Escape")document.getElementById("sheet").classList.remove("open");});

// ---- flows graph ----
function renderFlows(fs){
  const host=document.getElementById("flows"); host.innerHTML="";
  const ids=new Set(fs.map(s=>s.id));
  // group by flow; screens without flow -> grouped by section
  const groups={};
  fs.forEach(s=>{const keys=(s.flows&&s.flows.length)?s.flows:["section:"+s.section];keys.forEach(k=>{(groups[k]=groups[k]||[]).push(s);});});
  const order=Object.keys(groups).sort((a,b)=>groups[b].length-groups[a].length);
  if(!order.length){host.innerHTML='<div class="empty">No screens match these filters.</div>';return;}
  order.forEach((g,gi)=>{
    const nodes=groups[g];
    const d=el("details","flow"); if(gi<2)d.open=true;
    const label=g.startsWith("section:")?("Section: "+(TITLES[g.slice(8)]||g.slice(8))):g;
    const sm=el("summary",null,'<span>'+esc(label)+'</span><span class="fn">'+nodes.length+' screens</span>'); d.appendChild(sm);
    const canvas=el("div","canvas"); const wrap=layoutGraph(nodes,ids); canvas.appendChild(wrap); d.appendChild(canvas);
    host.appendChild(d);
  });
}
function layoutGraph(nodes,visibleIds){
  const idset=new Set(nodes.map(n=>n.id));
  // edges within this group (ignore back/related for depth layering)
  const adj={},pre={},indeg={}; nodes.forEach(n=>{adj[n.id]=[];pre[n.id]=[];indeg[n.id]=0;});
  nodes.forEach(n=>(n.links||[]).forEach(l=>{if(idset.has(l.to)&&l.type!=="back"&&l.type!=="related"&&l.type!=="expands"){adj[n.id].push(l.to);pre[l.to].push(n.id);indeg[l.to]=(indeg[l.to]||0)+1;}}));
  // depth = longest path FROM an entry (indeg 0) node, so flow reads left -> right
  const depth={};
  function dfs(id,stk){if(depth[id]!=null)return depth[id];if(stk.has(id))return 0;stk.add(id);let d=0;pre[id].forEach(u=>{d=Math.max(d,1+dfs(u,stk));});stk.delete(id);return depth[id]=d;}
  nodes.forEach(n=>{if(depth[n.id]==null)dfs(n.id,new Set());});
  // normalize so min depth root sits at 0 already; group by depth
  const cols={}; nodes.forEach(n=>{const dd=depth[n.id]||0;(cols[dd]=cols[dd]||[]).push(n);});
  const COLW=196,ROWH=104,PADX=8,PADY=8; let maxRow=0;
  const pos={}; Object.keys(cols).forEach(dd=>{cols[dd].forEach((n,i)=>{pos[n.id]={x:PADX+dd*COLW,y:PADY+i*ROWH};maxRow=Math.max(maxRow,i);});});
  const W=PADX*2+(Math.max(...Object.keys(cols).map(Number))+1)*COLW, H=PADY*2+(maxRow+1)*ROWH;
  const wrap=el("div","gwrap"); wrap.style.width=W+"px"; wrap.style.height=H+"px";
  // edges svg
  const NS="http://www.w3.org/2000/svg"; const svg=document.createElementNS(NS,"svg"); svg.setAttribute("width",W);svg.setAttribute("height",H);
  nodes.forEach(n=>(n.links||[]).forEach(l=>{ if(!pos[n.id]||!pos[l.to])return; const a=pos[n.id],b=pos[l.to]; const x1=a.x+150,y1=a.y+38,x2=b.x,y2=b.y+38; const p=document.createElementNS(NS,"path"); const mx=(x1+x2)/2; p.setAttribute("d","M"+x1+" "+y1+" C"+mx+" "+y1+" "+mx+" "+y2+" "+x2+" "+y2); if(l.type==="related"||l.type==="back"||l.type==="expands")p.setAttribute("stroke-dasharray","4 4"); svg.appendChild(p); }));
  wrap.appendChild(svg);
  nodes.forEach(n=>{const g=el("div","gnode");g.style.left=pos[n.id].x+"px";g.style.top=pos[n.id].y+"px";g.innerHTML='<img src="data:image/jpeg;base64,'+IMG[n.id]+'"><div class="gl">'+esc(n.title)+'</div>';g.onclick=()=>openSheet(n.id);wrap.appendChild(g);});
  return wrap;
}

// ---- view switch ----
function setView(v){view=v;document.querySelectorAll(".vtabs button").forEach(b=>b.classList.toggle("on",b.dataset.v===v));document.getElementById("galleryView").style.display=v==="gallery"?"":"none";document.getElementById("flowsView").style.display=v==="flows"?"":"none";render();}
document.querySelectorAll(".vtabs button").forEach(b=>b.onclick=()=>setView(b.dataset.v));
document.getElementById("q").addEventListener("input",render);

// derive app name from sections/specs title if available
(function(){const anyspec=Object.values(SPECS)[0]||"";const m=anyspec.match(/app\.[a-z0-9.-]+/i);document.getElementById("appname").textContent=m?m[0]:"app atlas";})();
buildTree();buildFacets();render();
</script>
"""

if __name__ == "__main__":
    main()
