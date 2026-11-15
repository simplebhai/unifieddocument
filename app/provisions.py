"""Find the exact provision each governing body has on a question (e.g. "FAR for industry").

A question is split into concepts (FAR / industry). For each body the code finds the block of text where all the
concepts occur closest together, preferring binding documents and blocks that carry figures. The block is returned
word for word with its document and PDF page. With a local model on, the model restates each block in one sentence.
"""
import re
from .glossary import GLOSSARY, STOP
from . import conflicts

ACRONYMS = {"far", "tod", "tdr", "rrts", "row", "ews", "lig", "sez", "msme"}
WINDOW, STEP = 14, 5

def concepts(q):
    """[(label, fts_terms, regex)] - one entry per idea in the question, with its Hindi equivalents."""
    ql = re.sub(r"[^\w\s.\-\u0900-\u097F]", " ", q.lower())
    found, used = [], set()
    for phrase in sorted(GLOSSARY, key=len, reverse=True):
        if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", ql) and not set(phrase.split()) & used:
            found.append((phrase, GLOSSARY[phrase])); used.update(phrase.split())
    for w in re.findall(r"[\w\u0900-\u097F][\w.\-\u0900-\u097F]*", ql):
        w = w.strip(".-")
        if w and w not in STOP and w not in used and len(w) > 1 and not w.isdigit():
            found.append((w, [])); used.add(w)
    merged = []                                   # industry + industrial share Hindi words: treat as one concept
    for en, hi in found:
        for m in merged:
            if set(hi) & set(m[1]):
                m[0].append(en); m[1] += [h for h in hi if h not in m[1]]; break
        else:
            merged.append(([en], list(hi)))
    out = []
    for ens, his in merged:
        fts, pats = [], []
        for en in ens:
            if en in ACRONYMS:
                fts.append(f'"{en}"'); pats.append(r"(?<![A-Za-z])" + r"\.?\s?".join(en.upper()) + r"(?![A-Za-z])")
            elif " " in en or len(en) < 5 or not en.isascii():
                fts.append(f'"{en}"'); pats.append(r"(?i:" + re.escape(en).replace(r"\ ", r"[\s\-]+") + ")")
            else:
                stem = en[:max(5, len(en) - 3)]
                fts.append(f'"{stem}"*'); pats.append(r"(?i:\b" + re.escape(stem) + r"\w*)")
        for h in his:
            fts.append('"' + h + '"'); pats.append(re.escape(h))
        out.append({"label": ens[0], "fts": "(" + " OR ".join(fts) + ")", "re": re.compile("|".join(pats))})
    return out

def best_blocks(text, cons, need):
    """Best window of lines holding at least `need` of the concepts close together."""
    lines = text.split("\n")
    hits = [[i for i, l in enumerate(lines) if c["re"].search(l)] for c in cons]
    if sum(bool(h) for h in hits) < need:
        return []
    best = None
    for start in range(0, max(1, len(lines) - WINDOW + STEP), STEP):
        end = start + WINDOW
        inside = [[i for i in h if start <= i < end] for h in hits]
        present = [h for h in inside if h]
        if len(present) < need:
            continue
        span = min(max(min(abs(a - b) for b in other) for other in present) for a in present[0])
        if span > 6:
            continue
        digits = sum(bool(re.search(r"\d", lines[i])) for h in present for i in h)
        score = len(present) * 6 + 10 - min(span, 9) + min(digits, 4) + min(sum(len(h) for h in present), 6) * 0.5
        if not best or score > best[0]:
            best = (score, span, "\n".join(lines[start:end]).strip(), len(present))
    return [best] if best else []

def find(con, q, jurisdiction=None, sector=None):
    cons = concepts(q)
    if not cons:
        return {"query": q, "concepts": [], "bodies": []}
    docs = {r["doc_id"]: dict(r) for r in con.execute("select * from docs where status in ('core','adjacent')")}
    def allowed(d):
        return ((not jurisdiction or any(j in d["jurisdiction"] for j in jurisdiction)) and
                (not sector or any(s in d["sector"] for s in sector)))
    need = len(cons) if len(cons) <= 2 else len(cons) - 1          # long questions may miss one term
    rows = con.execute("select doc_id, page, text from passages where passages match ? order by bm25(passages) limit 600",
                       (" OR ".join(c["fts"] for c in cons),)).fetchall()
    per_body = {}
    for r in rows:
        d = docs.get(r["doc_id"])
        if not d or not allowed(d):
            continue
        for score, span, block, got in best_blocks(r["text"], cons, need):
            level = int(d["level"])
            score += {1: 3, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 1}.get(level, -4)      # binding documents first
            per_body.setdefault(d["body"], []).append({
                "score": round(score, 1), "doc_id": d["doc_id"], "title": d["title"], "page": r["page"],
                "level": conflicts.LEVELS.get(level), "legal_status": d["legal_status"], "method": d["method"],
                "language": d["language"], "jurisdiction": d["jurisdiction"],
                "citation": f"{d['title']} ({d['body']}), PDF page {r['page']}", "text": block,
                "match": "direct" if span <= 2 and got == len(cons) else "nearby"})
    bodies = []
    all_bodies = sorted({d["body"] for d in docs.values() if allowed(d)})
    for b in all_bodies:
        items = sorted(per_body.get(b, []), key=lambda x: -x["score"])
        keep, seen_docs = [], set()
        for it in items:                              # best extract from each document first
            if it["doc_id"] not in seen_docs:
                seen_docs.add(it["doc_id"]); keep.append(it)
        for it in items:                              # then a second page from the top document
            if len(keep) < 2 and it not in keep:
                keep.append(it)
        keep = sorted(keep, key=lambda x: -x["score"])[:4]
        bodies.append({"body": b, "provisions": keep})
    bodies.sort(key=lambda x: (not x["provisions"], -(x["provisions"][0]["score"] if x["provisions"] else 0)))
    result = {"query": q, "concepts": [c["label"] for c in cons], "bodies": bodies,
              "highlight": "|".join(c["re"].pattern for c in cons), "model": None}
    import os
    if os.environ.get("OLLAMA_MODEL") and any(b["provisions"] for b in bodies):
        n, ctx = 0, []
        for b in bodies:
            for p in b["provisions"][:2]:
                n += 1; p["n"] = n
                ctx.append(f"[{n}] {b['body']} | {p['title']} | PDF page {p['page']}\n{p['text'][:1200]}")
        prompt = ("Question: " + q + "\n\nFor each numbered extract below, state in one or two sentences exactly what it "
                  "provides on the question: the figures, units and conditions as written. Use only the extract. "
                  "If the extract does not answer the question, write \"not stated in this extract\". Extracts may be in Hindi; "
                  "answer in English and keep figures unchanged.\n\n" + "\n\n".join(ctx) +
                  "\n\nReturn JSON: {\"answers\": [{\"n\": extract number, \"says\": \"...\"}]}")
        try:
            out = conflicts.ask_model(prompt)
            says = {a.get("n"): a.get("says") for a in out.get("answers", []) if isinstance(a, dict)}
            for b in bodies:
                for p in b["provisions"]:
                    p["says"] = says.get(p.get("n"))
            result["model"] = os.environ["OLLAMA_MODEL"]
        except Exception as e:
            result["model_error"] = str(e)
    return result
