# Multi-Agency Regional Growth & Policy Coordination Platform

A workspace for reading the plans of several governing bodies side by side. Pilot region: the Delhi–Meerut corridor
(NCRPB, NCRTC, GDA, MDA, Government of Uttar Pradesh rules, plus adjacent and reference documents).

## What works now

1. **Document repository** – every document is tagged by governing body, jurisdiction, sector, type, year and plan
   horizon (`data/manifest.csv`).
2. **Provision finder** – ask for a specific provision ("FAR for industry"). For each governing body the app shows
   the exact extract where the terms occur together, word for word, with document, legal status and PDF page, and
   lists the bodies whose documents have no such provision. With the local model on, each extract also gets a
   one-line statement of what it provides (`app/provisions.py`).
   **Search across all documents with citations** – a plain-English question returns the matching passages grouped by
   governing body, each with document name, body and PDF page. English questions also reach the Hindi documents
   through a glossary of planning terms (`app/glossary.py`).
3. **Filters** – by governing body, jurisdiction, sector and document type.

4. **Conflicts and alignment** – pick a topic and see what each body says side by side, which document prevails
   under the Acts (`data/precedence.csv`, every rule with its source page), a warning when the prevailing document
   is only a draft, and a suggested policy clause. With a local model it also reports conflicts, alignments and gaps
   and drafts the clause.

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

## Adding documents

1. Put the PDF in a folder (the PDFs themselves are not stored in this repository).
2. Add a row to `data/manifest.csv`. `method` is `text` (PDF has real text), `ocr` (scanned; set `ocr_lang` to `eng`
   or `hin+eng`), `krutidev` (Hindi typeset in a Kruti Dev legacy font) or `none`.
3. `python pipeline/extract.py <folder> <doc_id>` (needs poppler-utils and tesseract), then delete
   `data/index.sqlite` and restart the app.

## Known limits

- Scanned documents are read by OCR. Words are mostly right but figures can be wrong; check them against the PDF page.
- Raster map sheets have little or no searchable text. They are listed in the repository with their tags.
- Page numbers are PDF page numbers, not the numbers printed on the page.
