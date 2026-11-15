"""Multi-agency planning document repository: search with citations and filters.

Run:  uvicorn app.main:app --reload     then open http://localhost:8000
Optional local model for written answers: set OLLAMA_MODEL (e.g. llama3.2) with Ollama running.
"""
import json, os, re, sqlite3, urllib.request
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from . import index, conflicts, provisions
from .glossary import GLOSSARY, STOP

ROOT = Path(__file__).resolve().parent
if not index.DB.exists():
    index.build()
app = FastAPI(title="Multi-Agency Planning Document Platform")

def db():
    con = sqlite3.connect(index.DB); con.row_factory = sqlite3.Row
    return con

def build_match(q: str):
    """Turn a plain question into an FTS query: key terms OR-ed, plus Hindi equivalents."""
    ql = re.sub(r"[^\w\s.\-ऀ-ॿ]", " ", q.lower())
    terms, used = [], set()
    for phrase in sorted(GLOSSARY, key=len, reverse=True):          # longest phrases first
        if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", ql):
            terms.append(phrase); terms += GLOSSARY[phrase]; used.update(phrase.split())
    for w in re.findall(r"[\wऀ-ॿ][\w.\-ऀ-ॿ]*", ql):
        w = w.strip(".-")
        if w and w not in STOP and w not in used and len(w) > 1:
            terms.append(w)
    seen, out = set(), []
    for t in terms:
        if t not in seen:
            seen.add(t); out.append('"' + t.replace('"', "") + '"')
    return " OR ".join(out), [t.strip('"') for t in out]

def region_sql(region):
    """A region also takes in the documents that apply to every region inside it (state-wide, NCR-wide)."""
    if not region:
        return "", []
    return (" and (" + " or ".join("d.region = ?" for _ in region) + " or d.region like '%(all regions)')", list(region))

def filters(body, jurisdiction, sector, status, doc_type, region=None):
    sql, args = [], []
    for col, vals in (("body", body), ("jurisdiction", jurisdiction), ("sector", sector),
                      ("status", status), ("doc_type", doc_type)):
        if vals:
            sql.append("(" + " or ".join(f"d.{col} like ?" for _ in vals) + ")")
            args += [f"%{v}%" for v in vals]
    rs, ra = region_sql(region)
    return ((" and " + " and ".join(sql)) if sql else "") + rs, args + ra

@app.get("/api/docs")
def docs():
    con = db()
    rows = [dict(r) for r in con.execute("select * from docs order by body, title")]
    facets = {}
    for col in ("region", "body", "jurisdiction", "sector", "doc_type", "status", "language"):
        vals = set()
        for r in rows:
            vals.update(v.strip() for v in r[col].split(";") if v.strip())
        facets[col] = sorted(vals)
    return {"docs": rows, "facets": facets}

@app.get("/api/search")
def search(q: str, body: list[str] = Query(None), jurisdiction: list[str] = Query(None),
           sector: list[str] = Query(None), status: list[str] = Query(None),
           doc_type: list[str] = Query(None), limit: int = 30, region: list[str] = Query(None)):
    match, terms = build_match(q)
    if not match:
        return {"query": q, "terms": [], "results": []}
    fsql, fargs = filters(body, jurisdiction, sector, status or ["core", "adjacent", "reference"], doc_type, region)
    con = db()
    rows = con.execute(
        "select p.doc_id, p.page, snippet(passages, 2, '<mark>', '</mark>', ' … ', 40) as snippet, "
        "bm25(passages) as score, d.title, d.body, d.jurisdiction, d.sector, d.doc_type, d.year, d.language, "
        "d.method, d.file, d.status "
        "from passages p join docs d on d.doc_id = p.doc_id "
        f"where passages match ? {fsql} order by score limit ?", [match, *fargs, limit * 6]).fetchall()
    per_doc, results = {}, []
    for r in rows:                      # at most 4 passages per document, so several bodies show up
        if per_doc.get(r["doc_id"], 0) < 4 and len(results) < limit:
            per_doc[r["doc_id"]] = per_doc.get(r["doc_id"], 0) + 1
            results.append(dict(r) | {"citation": f"{r['title']} ({r['body']}), PDF page {r['page']}"})
    return {"query": q, "terms": terms, "results": results}

@app.get("/api/page")
def page(doc_id: str, page: int):
    r = db().execute("select p.text, d.title, d.body, d.file, d.method from passages p join docs d on d.doc_id=p.doc_id "
                     "where p.doc_id=? and p.page=?", (doc_id, page)).fetchone()
    return dict(r) if r else {"text": ""}

@app.get("/api/answer")
def answer(q: str, body: list[str] = Query(None), jurisdiction: list[str] = Query(None),
           sector: list[str] = Query(None)):
    """Written answer from a local Ollama model, grounded in the top passages. Off unless OLLAMA_MODEL is set."""
    model = os.environ.get("OLLAMA_MODEL")
    if not model:
        return {"enabled": False}
    hits = search(q, body, jurisdiction, sector, None, None, 8)["results"]
    con = db()
    ctx = []
    for i, h in enumerate(hits, 1):
        t = con.execute("select text from passages where doc_id=? and page=?", (h["doc_id"], h["page"])).fetchone()[0]
        ctx.append(f"[{i}] {h['citation']}\n{t[:2500]}")
    prompt = ("Answer the question using only the numbered passages. Cite passage numbers like [1] after each claim. "
              "If the passages do not answer it, say so. Some passages are in Hindi; answer in English.\n\n"
              + "\n\n".join(ctx) + f"\n\nQuestion: {q}\nAnswer:")
    try:
        req = urllib.request.Request(os.environ.get("OLLAMA_URL", "http://localhost:11434") + "/api/generate",
                                     data=json.dumps({"model": model, "prompt": prompt, "stream": False}).encode(),
                                     headers={"Content-Type": "application/json"})
        text = json.loads(urllib.request.urlopen(req, timeout=300).read())["response"]
        return {"enabled": True, "answer": text, "sources": [h["citation"] for h in hits]}
    except Exception as e:
        return {"enabled": True, "error": str(e)}

@app.get("/api/provisions")
def find_provisions(q: str, jurisdiction: list[str] = Query(None), sector: list[str] = Query(None),
                    region: list[str] = Query(None)):
    """The exact provision each governing body has on the question, word for word, with document and page."""
    return provisions.find(db(), q, jurisdiction, sector, region)

@app.get("/api/form")
def form():
    regions = sorted({r[0] for r in db().execute("select distinct region from docs") if "(all regions)" not in r[0] and r[0] != "General"})
    return {"regions": regions, "uses": list(provisions.USES), "parameters": list(provisions.PARAMETERS)}

@app.get("/api/rule")
def rule(use: str = "Any", parameter: str = "FAR", region: list[str] = Query(None)):
    """Standard form: region + land use + rule -> what each body provides."""
    return provisions.find(db(), provisions.rule_query(use, parameter), None, None, region)

@app.get("/api/matrix")
def matrix(use: str = "Any", region: list[str] = Query(None)):
    """Which body has a provision on which standard parameter, for one land use."""
    return provisions.matrix(db(), use, region)

@app.get("/api/topics")
def topics():
    return {"topics": list(conflicts.TOPICS), "model": os.environ.get("OLLAMA_MODEL")}

@app.get("/api/compare")
def compare(topic: str, jurisdiction: list[str] = Query(None), sector: list[str] = Query(None),
            region: list[str] = Query(None)):
    """Evidence by body on one topic, the order of precedence, and a suggested resolution and policy clause."""
    return conflicts.compare(db(), search, topic, None, jurisdiction, sector, region)

LEVEL_STANDING = {
    1: "Highest in the order within NCR: no development may violate the Regional Plan (rule R1).",
    2: "State Act: rules, byelaws and plans are made under it (rule R2).",
    3: "State rule, policy or notification: prevails over the building byelaws where they differ (rule R3).",
    4: "State byelaws: apply in every development area of Uttar Pradesh. State sectoral policies prevail over them where they differ (rule R3).",
    5: "Master plan: governs within its own development area and must conform to the Regional Plan (rules R1 and R4).",
    6: "Zonal plan: prepared within the master plan (rule R4).",
    7: "Project document: sets no rules of its own. The project must accord with the master plan (rule R5).",
    9: "Reference only: does not bind.",
}

@app.get("/api/regmatrix")
def regmatrix(category: str = "far", use: str = "all", located: bool = False, authority: str = "",
              in_tod: bool = False, station: list[str] = Query(None)):
    """Click-to-compare matrix: the document cards that apply at a location, for one planning parameter."""
    reg = json.loads((index.ROOT / "data" / "regulations.json").read_text(encoding="utf-8"))
    docs = {r["doc_id"]: dict(r) for r in db().execute("select * from docs")}
    station = station or []
    def applies(scope, needs_tod):
        if not located:
            return True
        if needs_tod and not in_tod:
            return False
        if not scope or scope in ("state", "ncr"):
            return True
        kind, _, val = scope.partition(":")
        if kind == "authority":
            return authority == val
        if kind == "station":
            return bool(set(val.split("|")) & set(station))
        return True
    cards = []
    for c in reg["cards"]:
        if c["category"] != category or not applies(c["scope"], c["requires_tod"]):
            continue
        if use != "all" and c["uses"] and use not in c["uses"]:
            continue
        d = docs[c["doc_id"]]
        level = int(d["level"])
        draft = bool(re.search(r"draft|proposal", d["legal_status"], re.I))
        cards.append(c | {"doc_title": d["title"], "body": d["body"], "file": d["file"], "level": level,
                          "level_label": conflicts.LEVELS.get(level), "legal_status": d["legal_status"], "draft": draft,
                          "standing": LEVEL_STANDING.get(level, ""), "method": d["method"]})
    cards.sort(key=lambda c: (c["level"], c["title"]))
    shown = {c["id"] for c in cards}
    flags = [f for f in reg["flags"] if category in f["categories"] and applies(f.get("scope"), f.get("needs_tod"))
             and (use == "all" or not f.get("uses") or use in f["uses"]) and shown & set(f["cards"])
             and (located or f["kind"] != "unlock")]
    return {"categories": reg["categories"], "uses": reg["uses"], "cards": cards, "flags": flags,
            "rules": {r["rule_id"]: r for r in conflicts.RULES}}

JOB = {"running": False, "log": []}

@app.post("/api/add")
def add_source(url: str, body: str, region: str, jurisdiction: str = "", sector: str = ""):
    """Standard route for a new document: give its link and who issued it; the rest is automatic."""
    import csv, sys, threading
    if JOB["running"]:
        return {"ok": False, "message": "Another document is still being processed."}
    src = index.ROOT / "data" / "sources.csv"
    with open(src, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow([url, "", body, region, jurisdiction, sector])
    def work():
        JOB.update(running=True, log=[])
        try:
            sys.path.insert(0, str(index.ROOT / "pipeline"))
            import auto
            if auto.run(JOB["log"].append):
                index.build()
        except Exception as e:
            JOB["log"].append(f"failed: {e}")
        JOB["running"] = False
    threading.Thread(target=work, daemon=True).start()
    return {"ok": True}

@app.get("/api/add/status")
def add_status():
    return JOB

@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")

app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
