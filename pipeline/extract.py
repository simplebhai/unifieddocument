"""Extract per-page text from the source PDFs into data/pages/<doc_id>.jsonl.

Usage: python pipeline/extract.py <folder with PDFs> [doc_id ...]
method=text -> pdftotext; method=krutidev -> legacy Hindi font converted to Unicode; method=ocr -> render page + tesseract; method=none -> metadata only.
Needs poppler-utils and tesseract (with the 'hin' language pack for Hindi scans).
"""
import csv, json, re, subprocess, sys, tempfile, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "pages"

def npages(pdf):
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    return int(next(l.split()[1] for l in out.splitlines() if l.startswith("Pages")))

def page_text(pdf, p):
    return subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", str(pdf), "-"],
                          capture_output=True, text=True).stdout

def page_ocr(pdf, p, lang):
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "p")
        # big map sheets are rendered to a fixed pixel width instead of a dpi
        size = subprocess.run(["pdfinfo", "-f", str(p), "-l", str(p), str(pdf)], capture_output=True, text=True).stdout
        big = any("Page" in l and "size" in l and float(l.split()[3]) > 1500 for l in size.splitlines())
        args = ["-scale-to", "6000"] if big else ["-r", "170"]
        subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-gray", "-png", *args, str(pdf), base], check=True)
        img = next(Path(d).glob("*.png"))
        return subprocess.run(["tesseract", str(img), "-", "-l", lang, "--psm", "11" if big else "3"],
                              capture_output=True, text=True).stdout

def run(row, src):
    pdf = src / row["file"]
    dst = OUT / f"{row['doc_id']}.jsonl"
    if row["method"] == "none" or not pdf.exists():
        return row["doc_id"], 0
    if row["method"] == "krutidev":
        import legacy_hindi
        pages = [{"page": p, "text": t} for p, t in sorted(legacy_hindi.pages(pdf))]
        with open(dst, "w", encoding="utf-8") as f:
            for r in pages: f.write(json.dumps(r, ensure_ascii=False) + "\n")
        return row["doc_id"], len(pages)
    n = npages(pdf)
    def one(p):
        t = page_text(pdf, p) if row["method"] == "text" else page_ocr(pdf, p, row["ocr_lang"] or "eng")
        t = re.sub(r"[ \t]{4,}", "   ", t); t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
        return {"page": p, "text": t.strip()}
    with ThreadPoolExecutor(2) as ex:
        pages = list(ex.map(one, range(1, n + 1)))
    with open(dst, "w", encoding="utf-8") as f:
        for r in pages:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return row["doc_id"], n

if __name__ == "__main__":
    src = Path(sys.argv[1]); only = set(sys.argv[2:])
    OUT.mkdir(parents=True, exist_ok=True)
    for row in csv.DictReader(open(ROOT / "data" / "manifest.csv", encoding="utf-8")):
        if only and row["doc_id"] not in only: continue
        print(*run(row, src), flush=True)
