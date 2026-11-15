"""Compare what different governing bodies say on a topic, and suggest a resolution that follows the Acts.

Works in two modes:
- without a model: side-by-side evidence, figures pulled out by rule, precedence by rule, template clause;
- with a local Ollama model (OLLAMA_MODEL set): the model also judges conflict / alignment and drafts the clause.
The order of precedence always comes from data/precedence.csv, never from the model.
"""
import csv, json, os, re, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVELS = {1: "Regional plan (NCR)", 2: "State Act", 3: "State rules, policies and notifications", 4: "State byelaws",
          5: "Master plan", 6: "Zonal plan", 7: "Project proposal", 9: "Reference / informational"}
TOPICS = {
    "TOD and RRTS influence zones": "TOD transit oriented development RRTS station influence zone mixed use",
    "FAR and density": "FAR floor area ratio density group housing",
    "Industrial and logistics areas": "industrial industry logistics warehousing freight",
    "Green belt and highway buffers": "green belt highway expressway buffer",
    "Population and plan horizon": "population projection 2031 2041",
    "Housing": "housing residential affordable township",
    "Road network and expressways": "road network expressway highway right of way widening",
    "Land-use change and development fees": "land use conversion charges development fee",
    "Water, sewerage and drainage": "water supply sewerage drainage",
}
RULES = list(csv.DictReader(open(ROOT / "data" / "precedence.csv", encoding="utf-8")))
RULE = {r["rule_id"]: r for r in RULES}

FIGURES = [
    ("FAR", r"(?:F\.?A\.?R\.?|floor area ratio|एफ\.?ए\.?आर\.?|तल क्षेत्र(?:फल)? अनुपात)[^.\n।]{0,60}?(\d+(?:\.\d+)?)"),
    ("Density (persons/ha)", r"(\d{2,4})\s*(?:pph|persons? per hectare|व्यक्ति प्रति हे)"),
    ("Width (m)", r"(\d{1,3}(?:\.\d+)?)\s*(?:m\b|mtr|metres?|meters?|मीटर|मी\.)\s*(?:wide|width|green|belt|ROW|चौड़)"),
    ("Population", r"(?:population|जनसंख्या)[^.\n।]{0,50}?(\d[\d,.]*\s*(?:lakh|million|crore|लाख|करोड़))"),
]

def figures(text):
    out = []
    for label, pat in FIGURES:
        for m in re.finditer(pat, text, re.I):
            out.append({"what": label, "value": m.group(1), "context": re.sub(r"\s+", " ", text[max(0, m.start() - 60): m.end() + 40])})
    return out[:6]

def precedence(a, b):
    """Which of two documents prevails. a, b are doc rows (dicts with level, year, legal_status, title, body)."""
    la, lb = int(a["level"]), int(b["level"])
    if 9 in (la, lb):
        return {"prevails": None, "rule": None, "text": "One of these is a reference or informational document and does not bind anyone."}
    hi, lo = (a, b) if la <= lb else (b, a)
    lh, ll = int(hi["level"]), int(lo["level"])
    places = lambda d: {x.strip().lower() for x in re.split(r"[;()]", d["jurisdiction"]) if x.strip()}
    if lh >= 5 and not places(a) & places(b):       # plans and projects for different areas: no hierarchy
        r = RULE["R6"]
        return {"prevails": None, "prevails_title": None, "rule_id": "R6", "text": "These cover different areas. " + r["rule"],
                "rule_source": r["source"], "rule_pages": r["source_page"], "basis": r["basis"], "provisional": False, "note": ""}
    if lh == ll:
        rid = "R7" if lh == 4 else "R6"
        text = RULE[rid]["rule"]
        prev = None
        if lh == 4 and (a["year"] or "0") != (b["year"] or "0"):
            prev = a if (a["year"] or "0") > (b["year"] or "0") else b
    else:
        rid = "R1" if lh == 1 else "R2" if lh == 2 else "R3" if (lh, ll) == (3, 4) else "R4" if (lh, ll) == (5, 6) else "R5" if ll == 7 and lh in (5, 6) else None
        prev = hi if rid else None
        text = RULE[rid]["rule"] if rid else ("No explicit rule on this pair was found in the loaded documents. "
                                              "It needs a planner's or legal review.")
    r = RULE.get(rid, {})
    provisional = bool(prev and re.search(r"draft|proposal|not confirmed", prev["legal_status"], re.I))
    return {"prevails": prev and prev["doc_id"], "prevails_title": prev and f"{prev['title']} ({prev['body']})",
            "rule_id": rid, "text": text, "rule_source": r.get("source"), "rule_pages": r.get("source_page"),
            "basis": r.get("basis"), "provisional": provisional,
            "note": (f"Provisional: the prevailing document is marked '{prev['legal_status']}', so it does not bind yet."
                     if provisional else "")}

def template_clause(topic, a, b, p):
    if p["prevails"]:
        hi, lo = (a, b) if p["prevails"] == a["doc_id"] else (b, a)
        return (f"In respect of {topic}, the {lo['title']} shall be read in conformity with the {hi['title']}. "
                f"Where the two differ, the provision of the {hi['title']} shall apply within {lo['jurisdiction']}, and "
                f"{lo['body']} shall amend the {lo['title']} accordingly, following the amendment procedure of the Act under which it is made.")
    return (f"{a['body']} and {b['body']} shall adopt common norms for {topic} in the areas where their plans meet "
            f"({a['jurisdiction']}; {b['jurisdiction']}). The common norms shall be consistent with the Regional Plan and "
            f"State policy, and each body shall amend its own plan to carry them.")

def ask_model(prompt):
    model = os.environ.get("OLLAMA_MODEL")
    if not model:
        return None
    req = urllib.request.Request(os.environ.get("OLLAMA_URL", "http://localhost:11434") + "/api/generate",
                                 data=json.dumps({"model": model, "prompt": prompt, "stream": False, "format": "json",
                                                  "options": {"temperature": 0.1, "num_ctx": 8192}}).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(json.loads(urllib.request.urlopen(req, timeout=900).read())["response"])

def compare(con, search, topic, query=None, jurisdiction=None, sector=None, region=None):
    q = query or TOPICS.get(topic, topic)
    docs = {r["doc_id"]: dict(r) for r in con.execute("select * from docs")}
    in_region = lambda d: not region or d["region"] in region or "(all regions)" in d["region"]
    bodies = sorted({d["body"] for d in docs.values() if d["status"] in ("core", "adjacent") and in_region(d)})
    evidence = []
    for b in bodies:
        for h in search(q, [b], jurisdiction, sector, ["core", "adjacent"], None, 3, region)["results"]:
            text = con.execute("select text from passages where doc_id=? and page=?", (h["doc_id"], h["page"])).fetchone()[0]
            d = docs[h["doc_id"]]
            evidence.append({"n": len(evidence) + 1, "doc_id": h["doc_id"], "page": h["page"], "body": b, "title": d["title"],
                             "citation": h["citation"], "snippet": h["snippet"], "method": d["method"],
                             "level": LEVELS.get(int(d["level"])), "legal_status": d["legal_status"],
                             "figures": [] if d["doc_type"] == "Map" else figures(text), "_text": text})
    # one precedence statement per pair of documents from different bodies
    seen, pairs = set(), []
    for x in evidence:
        for y in evidence:
            if not x["body"] < y["body"]:
                continue
            p = precedence(docs[x["doc_id"]], docs[y["doc_id"]])
            key = (x["body"], y["body"], p.get("rule_id"), p.get("prevails"))   # one line per pair of bodies and rule
            if key not in seen and "reference" not in p["text"]:
                seen.add(key)
                if True:
                    pairs.append({"a": x["title"], "a_body": x["body"], "b": y["title"], "b_body": y["body"], **p,
                                  "template_clause": template_clause(topic, docs[x["doc_id"]], docs[y["doc_id"]], p) if p.get("rule_id") else None})
    result = {"topic": topic, "query": q, "evidence": [{k: v for k, v in e.items() if k != "_text"} for e in evidence],
              "precedence": pairs, "rules": RULES, "model": os.environ.get("OLLAMA_MODEL"), "findings": None}
    if os.environ.get("OLLAMA_MODEL") and evidence:
        ctx = "\n\n".join(f"[{e['n']}] {e['body']} | {e['title']} | {e['level']} | status: {e['legal_status']} | PDF page {e['page']}\n{e['_text'][:1000]}"
                          for e in evidence[:9])
        rules = "\n".join(f"{r['rule_id']}: {r['rule']}" for r in RULES)
        prompt = (
            "You compare planning documents from different governing bodies. Use ONLY the numbered passages. "
            "Some passages are in Hindi. Answer in English.\n"
            f"Topic: {topic}\n\nPassages:\n{ctx}\n\nRules of precedence (apply these, do not invent others):\n{rules}\n\n"
            "Return JSON: {\"findings\": [{\"type\": \"conflict\" | \"alignment\" | \"gap\", \"bodies\": [..], "
            "\"issue\": \"one sentence\", \"evidence\": [passage numbers], \"explanation\": \"what each passage says\", "
            "\"rule\": \"rule id that decides it, or null\", \"recommended_option\": \"the option that follows the rules\", "
            "\"draft_clause\": \"a policy clause that would remove the conflict or secure the alignment\"}]}. "
            "A conflict needs two passages from different bodies that cannot both be followed. "
            "Do not state any figure that is not in a passage. If there is nothing to report, return {\"findings\": []}.")
        try:
            out = ask_model(prompt)
            ok = {e["n"] for e in evidence}
            result["findings"] = [f | {"evidence": [n for n in f.get("evidence", []) if n in ok]}
                                  for f in out.get("findings", []) if isinstance(f, dict)]
        except Exception as e:
            result["model_error"] = str(e)
    return result
