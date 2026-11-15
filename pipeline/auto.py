"""One standard route for any document, any region: download -> detect -> extract -> tag -> index.

    python pipeline/auto.py                     process everything in data/sources.csv and source_pdfs/ that is new
    python pipeline/auto.py --detect <pdf>      only show what would be detected for one file

For each new PDF it works out by itself:
  - how to read it: real text, scanned (OCR, English or Hindi), or Hindi in a legacy font (converted to Unicode);
  - a first set of tags: title, document type, legal level, draft or not, year, language.
Body, region, jurisdiction and sector come from data/sources.csv (or are left for you to fill in the manifest).
Auto-tagged rows are marked tagged_by=auto so they can be reviewed.
"""
import csv, os, re, subprocess, sys, tempfile, urllib.request, urllib.parse
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source_pdfs"
MANIFEST = ROOT / "data" / "manifest.csv"
LEGACY_FONTS = re.compile(r"kruti|devlys|chanakya|bhartiya", re.I)
DEVA = re.compile(r"[ऀ-ॿ]")
TYPES = [  # (pattern on title + file name, doc_type, legal level)
    (r"regional plan", "Regional plan", 1), (r"\bact\b|अधिनियम", "Act", 2),
    (r"bye-?laws?|उपविधि", "Byelaws", 4), (r"rules?\b|niyamawali|नियमावली", "Rules", 3),
    (r"policy|niti|नीति", "Policy", 3), (r"notification|अधिसूचना|government order|शासनादेश", "Notification", 3),
    (r"zonal|zone", "Zonal plan", 6), (r"master ?plan|महायोजना|development plan", "Master plan", 5),
    (r"expression of interest|\beoi\b|\brfp\b|tender|dpr|detailed project report", "Project proposal", 7),
]

def sh(*a):
    return subprocess.run(a, capture_output=True, text=True, errors="ignore").stdout

def detect(pdf):
    """Work out how to read a PDF and suggest its tags."""
    info = sh("pdfinfo", str(pdf))
    n = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    w = float(re.search(r"Page size:\s+([\d.]+)", info).group(1))
    sample = sorted({1, 2, 3, max(1, n // 2), n})
    text = "".join(sh("pdftotext", "-f", str(p), "-l", str(p), str(pdf), "-") for p in sample if p <= n)
    per_page = len(text.strip()) / len([p for p in sample if p <= n])
    legacy = bool(LEGACY_FONTS.search(sh("pdffonts", "-l", str(min(n, 30)), str(pdf))))
    ocr_lang, first = "", text
    if legacy and per_page > 200:
        method, language = "krutidev", "Hindi"
    elif per_page > 200:
        method = "text"
        language = "Hindi" if len(DEVA.findall(text)) > 0.3 * len(re.findall(r"\w", text)) else "English"
    else:                                           # scanned: read one page both ways to pick the language
        method = "ocr"
        with tempfile.TemporaryDirectory() as d:
            p = min(2, n)
            args = ["-scale-to", "3000"] if w > 1500 else ["-r", "150"]
            subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-gray", "-png", *args, str(pdf), d + "/p"])
            img = next(Path(d).glob("*.png"), None)
            first = sh("tesseract", str(img), "-", "-l", "hin+eng") if img else ""
        hindi = len(DEVA.findall(first)) > 0.3 * max(1, len(re.findall(r"\w", first)))
        ocr_lang, language = ("hin+eng", "Hindi") if hindi else ("eng", "English")
        if len(first.strip()) < 40:
            method = "none" if w > 1500 else "ocr"
    if method == "krutidev":
        import legacy_hindi
        first = next(iter(legacy_hindi.pages(pdf)), (1, ""))[1]
    lines = [l.strip() for l in first.split("\n") if len(l.strip()) > 8 and not re.fullmatch(r"[\W\d]+", l.strip())]
    name = re.sub(r"[_\-]+", " ", Path(pdf).stem)
    title = name if method in ("ocr", "none") or not lines else " ".join(lines[:2])[:110]
    hay = (title + " " + name).lower()
    doc_type, level = next(((t, lv) for pat, t, lv in TYPES if re.search(pat, hay)), ("Document", 9))
    if w > 1500 and n <= 2:
        doc_type = "Map"
    years = [int(y) for y in re.findall(r"(?<!\d)(19[5-9]\d|20[0-4]\d)(?!\d)", title + " " + name)]
    draft = bool(re.search(r"draft|प्रारूप", (title + " " + name + " " + first[:1500]), re.I))
    return {"title": title, "doc_type": doc_type, "level": level, "legal_status": "Draft" if draft else "Not confirmed",
            "year": str(max(years)) if years else "", "language": language, "method": method, "ocr_lang": ocr_lang, "pages": n}

def download(url, dest):
    req = urllib.request.Request(urllib.parse.quote(url, safe=":/%?=&()"), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 16):
            f.write(chunk)
    if open(dest, "rb").read(5) != b"%PDF-":
        os.remove(dest); raise ValueError("not a PDF")

def run(log=print):
    SRC.mkdir(exist_ok=True)
    rows = list(csv.DictReader(open(MANIFEST, encoding="utf-8")))
    fields = list(rows[0].keys())
    known = {r["file"] for r in rows}
    given = {}
    sources = ROOT / "data" / "sources.csv"
    if sources.exists():
        for s in csv.DictReader(open(sources, encoding="utf-8")):
            f = s["file"] or os.path.basename(urllib.parse.urlparse(s["url"]).path)
            given[f] = s
            if s["url"] and f not in known and not (SRC / f).exists():
                try:
                    log(f"downloading {f}"); download(s["url"], SRC / f)
                except Exception as e:
                    log(f"  could not download {f}: {e}")
    added = []
    for pdf in sorted(SRC.glob("*.[pP][dD][fF]")):
        if pdf.name in known:
            continue
        log(f"reading {pdf.name}")
        d = detect(pdf); g = given.get(pdf.name, {})
        doc_id = re.sub(r"[^a-z0-9]+", "_", pdf.stem.lower()).strip("_")[:40]
        row = {k: "" for k in fields} | {
            "doc_id": doc_id, "file": pdf.name, "title": d["title"], "body": g.get("body") or "Unassigned",
            "jurisdiction": g.get("jurisdiction") or "", "sector": g.get("sector") or "", "doc_type": d["doc_type"],
            "year": d["year"], "language": d["language"], "status": "core", "method": d["method"], "ocr_lang": d["ocr_lang"],
            "level": d["level"], "legal_status": d["legal_status"], "region": g.get("region") or "Unassigned", "tagged_by": "auto"}
        log(f"  {d['method']} {d['ocr_lang']} | {d['doc_type']} | {d['language']} | {d['pages']} pages")
        extract.run(row, SRC)
        rows.append(row); added.append(doc_id)
        w = csv.DictWriter(open(MANIFEST, "w", encoding="utf-8", newline=""), fieldnames=fields); w.writeheader(); w.writerows(rows)
    index = ROOT / "data" / "index.sqlite"
    if added and index.exists():
        index.unlink()                               # rebuilt when the app next starts
    log(f"done: {len(added)} new document(s)")
    return added

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--detect":
        print(detect(sys.argv[2]))
    else:
        run()
