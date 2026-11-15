# Multi-Agency Regional Growth & Policy Coordination Platform

A workspace for reading the plans of several governing bodies side by side. Pilot region: the Delhi–Meerut corridor
(NCRPB, NCRTC, GDA, MDA, Government of Uttar Pradesh rules, plus adjacent and reference documents).

## What works now

1. **Rule lookup (standard form)** – pick a region, a land use and a rule (FAR, ground coverage, height, setbacks,
   density, parking, road width, plot size, green belt, conversion charges, development fee). The app shows what
   each governing body provides, word for word, with document, legal status and PDF page. A grid shows at a glance
   which body has which rule, and a bar chart shows how many pages carry it.
2. **Ask a question** – the same answer for a question in your own words, plus the other matching passages.
3. **Conflicts and alignment** – what each body says on a topic, which document prevails under the Acts
   (`data/precedence.csv`, each rule with its source page), a warning when the prevailing document is a draft, and a
   suggested policy clause. With a local model it also reports conflicts, alignments and gaps and drafts the clause.
4. **Documents** – every document tagged by region, governing body, jurisdiction, sector, type, legal level and year.
5. **Any region** – documents carry a region. State-wide and NCR-wide documents apply to every region inside them.
6. **Automatic intake** – give a link (Documents tab, or `data/sources.csv`) or drop a PDF in `source_pdfs/`. The
   app downloads it, works out how to read it (real text, scan in English or Hindi, or Hindi in a legacy font),
   suggests title, type, legal level, draft status, year and language, extracts the text and re-indexes.

Not built yet: map-based filtering and spatial conflict checks (need boundary layers).

No cloud service is used. Everything runs on one computer.

## Run

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000 (in Codespaces, open the forwarded port 8000). The search index is built on first start
from `data/pages/`.

### The local AI model

The app uses a ready open model that runs on the laptop through [Ollama](https://ollama.com). Nothing is sent online.

```
ollama pull llama3.2:3b          # about 8 GB RAM; use qwen2.5:7b on 16 GB or more
OLLAMA_MODEL=llama3.2:3b uvicorn app.main:app        # Windows PowerShell: $env:OLLAMA_MODEL="llama3.2:3b"; uvicorn app.main:app
```

With the model on, search adds a written summary and the Conflicts tab adds findings and drafted clauses. The model
only reads the passages the search finds and must cite them; the order of precedence is fixed by the rule table.
Without the model the app still works and shows passages, precedence and template clauses.

The findings are a planning aid, not legal advice. Check each one against the cited pages.

## Adding documents and regions

- In the app: Documents tab, "Add a document": link, governing body, region.
- In bulk: add rows to `data/sources.csv` (url, file, body, region, jurisdiction, sector) and run
  `python pipeline/auto.py`. PDFs you already have go in `source_pdfs/`.
- Needs poppler-utils and tesseract with the Hindi pack (`sudo apt install poppler-utils tesseract-ocr tesseract-ocr-hin`).
- New rows in `data/manifest.csv` are marked `tagged_by=auto`. Check the suggested type, legal level and status,
  because the order of precedence depends on them.
- A new region needs its own precedence rules where its Acts differ: add them to `data/precedence.csv`.

## Known limits

- Scanned documents are read by OCR. Words are mostly right but figures can be wrong; check them against the PDF page.
- Raster map sheets have little or no searchable text. They are listed in the repository with their tags.
- Page numbers are PDF page numbers, not the numbers printed on the page.
