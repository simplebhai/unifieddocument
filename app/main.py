"""Multi-agency planning document repository: search with citations and filters.

Run:  uvicorn app.main:app --reload     then open http://localhost:8000
Optional local model for written answers: set OLLAMA_MODEL (e.g. llama3.2) with Ollama running.
"""
import json, os, re, sqlite3, urllib.request
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from . import index
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

def filters(body, jurisdiction, sector, status, doc_type):
    sql, args = [], []
    for col, vals in (("body", body), ("jurisdiction", jurisdiction), ("sector", sector),
                      ("status", status), ("doc_type", doc_type)):
        if vals:
            sql.append("(" + " or ".join(f"d.{col} like ?" for _ in vals) + ")")
            args += [f"%{v}%" for v in vals]
    return (" and " + " and ".join(sql)) if sql else "", args

@app.get("/api/docs")
def docs():
    con = db()
    rows = [dict(r) for r in con.execute("select * from docs order by body, title")]
    facets = {}
    for col in ("body", "jurisdiction", "sector", "doc_type", "status", "language"):
        vals = set()
        for r in rows:
            vals.update(v.strip() for v in r[col].split(";") if v.strip())
        facets[col] = sorted(vals)
    return {"docs": rows, "facets": facets}

@app.get("/api/search")
def search(q: str, body: list[str] = Query(None), jurisdiction: list[str] = Query(None),
           sector: list[str] = Query(None), status: list[str] = Query(None),
           doc_type: list[str] = Query(None), limit: int = 30):
    match, terms = build_match(q)
    if not match:
        return {"query": q, "terms": [], "results": []}
    fsql, fargs = filters(body, jurisdiction, sector, status or ["core", "adjacent", "reference"], doc_type)
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

@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")

app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
