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

## Regulatory matrix (first tab)

Click the map (authority area, RRTS station influence zone, or the track strip) or pick a place. The app works out which jurisdictions overlap that point and shows only the documents that govern it. Switch between FAR/FSI, Ground coverage and height, Setbacks and road widths, Permissible land use, and TOD and economic incentives. Each document is a card with base and maximum tables, conditions, purchasable allowances, its place in the order of precedence, draft or published status, and PDF page citations. Conflicts, unlocks and checks are flagged above the cards.

Map engine: the map is drawn with GeoLibre's headless engine (opengeos/GeoLibre, MIT; MapLibre GL JS 6). Rebuild the bundle with `sh geolibre/build.sh` (Node 20+); output goes to `app/static/geolibre/`. Basemaps are Esri streets and imagery tiles (keyless, need internet), or none.

Data: `data/regulations.json` (built by `pipeline/build_regulations.py`, every figure cited to a PDF page), `app/static/geo.json` (OSM tehsils, stations, 1.5 km and 500 m influence zones). Limits: authority areas are tehsil approximations; GDA has map sheets only; the TOD Policy 2022 is not loaded; scanned Hindi notifications show no figures. Base-map tiles need internet on your machine; the vector layers work without them.

## Tabs

- **Regulatory matrix**: click-to-compare map with 16 planning parameters (FAR, coverage and height, setbacks and roads, land use, TOD, parking and basements, layouts and subdivision, open space and green cover, community facilities, EWS/LIG and affordable housing, water, energy and environment, fire safety, heritage and rivers, fees and charges, TDR, pooling and extra FAR, permissions and process). All cards come from `pipeline/build_regulations.py`, each figure cited to a PDF page.
- **Find a rule**: keyword search over those curated rules, filtered by parameter, land use and governing body.
- **Ask a question**: matching curated rules first, then the full-text passages (including Hindi documents).
- **Conflicts and alignment**: the flagged conflicts and checks, a grid of which body covers which parameter (dashes are gaps), and the order of precedence. The old passage-by-passage comparison is kept under "advanced".
- **Documents**: the library, with the parameters each document feeds.

Not yet covered by curated rules: use-specific standards (hotels, cinemas, petrol pumps, hospitals, schools, farmhouses), EV charging, accessibility, structural safety, and most of the Noida, NCRPB and GDA documents (map sheets and scans give no figures).
