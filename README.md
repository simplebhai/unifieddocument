# Multi-Agency Regional Growth & Policy Coordination Platform

A workspace for reading the plans of several governing bodies side by side. Pilot region: the Delhi–Meerut corridor
(NCRPB, NCRTC, GDA, MDA, Government of Uttar Pradesh rules, plus adjacent and reference documents).

## What works now

1. **Document repository** – every document is tagged by governing body, jurisdiction, sector, type, year and plan
   horizon (`data/manifest.csv`).
2. **Search across all documents with citations** – a plain-English question returns the matching passages grouped by
   governing body, each with document name, body and PDF page. English questions also reach the Hindi documents
   through a glossary of planning terms (`app/glossary.py`).
3. **Filters** – by governing body, jurisdiction, sector and document type.

Not built yet: conflict detection, synergy discovery, map-based filtering.

No cloud service is used. Everything runs on one computer.

## Run

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000 (in Codespaces, open the forwarded port 8000). The search index is built on first start
from `data/pages/`.

### Optional: written answers from a local model

Install [Ollama](https://ollama.com), pull a model, and start the app with `OLLAMA_MODEL=<model name>`. The app then
adds a short written summary above the passages. Without it the app shows passages only.

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
