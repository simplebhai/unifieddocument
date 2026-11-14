"""Per-page text for PDFs typeset in Kruti Dev: converts only the runs set in the legacy font."""
import subprocess, html, re
import xml.etree.ElementTree as ET
from krutidev import kd2uni

LEGACY = ("kruti", "devlys", "bhartiya", "chanakya")

def pages(pdf):
    xml = subprocess.run(["pdftohtml", "-xml", "-i", "-stdout", str(pdf)], capture_output=True).stdout
    xml = re.sub(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", b"", xml)
    root = ET.fromstring(xml)
    for pg in root.iter("page"):
        fonts = {f.get("id"): f.get("family", "").lower() for f in pg.iter("fontspec")}
        fonts.update(getattr(pages, "_f", {})); pages._f = fonts
        runs = []
        for t in pg.iter("text"):
            s = "".join(t.itertext())
            if any(k in fonts.get(t.get("font"), "") for k in LEGACY):
                s = kd2uni(s)
            runs.append((int(t.get("top")), int(t.get("left")), int(t.get("height")), s))
        runs.sort()
        lines, cur, base = [], [], None
        for top, left, h, s in runs:
            if base is None or abs(top - base) <= max(6, h // 2):
                cur.append((left, s)); base = top if base is None else base
            else:
                lines.append(" ".join(x for _, x in sorted(cur))); cur, base = [(left, s)], top
        if cur: lines.append(" ".join(x for _, x in sorted(cur)))
        yield int(pg.get("number")), re.sub(r"[ \t]+", " ", "\n".join(lines)).strip()
