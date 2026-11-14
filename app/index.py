"""Build the SQLite search index from data/manifest.csv and data/pages/*.jsonl."""
import csv, json, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "index.sqlite"
COLS = ["doc_id", "file", "title", "body", "jurisdiction", "sector", "doc_type", "year", "horizon",
        "language", "status", "method"]

def build(db_path=DB):
    if db_path.exists(): db_path.unlink()
    con = sqlite3.connect(db_path)
    con.execute(f"create table docs ({', '.join(COLS)}, pages integer, chars integer)")
    con.execute("create virtual table passages using fts5(doc_id unindexed, page unindexed, text, "
                "tokenize=\"unicode61 remove_diacritics 0 categories 'L* N* Co Mn Mc'\")")
    for row in csv.DictReader(open(ROOT / "data" / "manifest.csv", encoding="utf-8")):
        f = ROOT / "data" / "pages" / f"{row['doc_id']}.jsonl"
        n = chars = 0
        if f.exists():
            for line in open(f, encoding="utf-8"):
                r = json.loads(line); n += 1; chars += len(r["text"])
                if r["text"].strip():
                    con.execute("insert into passages values (?,?,?)", (row["doc_id"], r["page"], r["text"]))
        con.execute(f"insert into docs values ({','.join('?' * (len(COLS) + 2))})", [row[c] for c in COLS] + [n, chars])
    con.commit(); con.close()
    return db_path

if __name__ == "__main__":
    print("built", build())
