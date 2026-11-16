"""Generate the committed synthetic filings: three filings, each a 1-page primary document and a
2-page financial-statement report, as hand-written PDF bytes. Deterministic: the same bytes every run.
The pin is fixtures/filings/SHA256SUMS; tests/test_fixtures.py checks it and, because the generator is
deterministic, also that regenerating reproduces the committed bytes."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "fixtures" / "filings"

# adsh, cik, form, accepted (ET, explicit offset), scale, values in thousands for the five tags.
FILINGS = [
    {"adsh": "0000000001-25-000001", "cik": "1000001", "form": "10-K", "accepted": "2025-02-27T16:05:12-05:00",
     "scale": 1000, "ddate": "2024-12-31", "qtrs": {"Revenues": 4, "NetIncomeLoss": 4, "Assets": 0, "Liabilities": 0, "StockholdersEquity": 0},
     "values": {"Revenues": 1234, "NetIncomeLoss": -56, "Assets": 9876, "Liabilities": 4321, "StockholdersEquity": 5555}},
    {"adsh": "0000000002-25-000002", "cik": "1000002", "form": "10-Q", "accepted": "2025-05-08T09:41:00-04:00",
     "scale": 1000, "ddate": "2025-03-31", "qtrs": {"Revenues": 1, "NetIncomeLoss": 1, "Assets": 0, "Liabilities": 0, "StockholdersEquity": 0},
     "values": {"Revenues": 780, "NetIncomeLoss": 42, "Assets": 3200, "Liabilities": 1100, "StockholdersEquity": 2100}},
    {"adsh": "0000000003-25-000003", "cik": "1000003", "form": "10-K", "accepted": "2025-03-14T17:30:00-04:00",
     "scale": 1000, "ddate": "2024-12-31", "qtrs": {"Revenues": 4, "NetIncomeLoss": 4, "Assets": 0, "Liabilities": 0, "StockholdersEquity": 0},
     "values": {"Revenues": 51000, "NetIncomeLoss": 2750, "Assets": 120500, "Liabilities": 70250, "StockholdersEquity": 50250}},
]
LABELS = {"Revenues": "Revenues", "NetIncomeLoss": "Net income (loss)", "Assets": "Total assets",
          "Liabilities": "Total liabilities", "StockholdersEquity": "Total stockholders' equity"}

def fmt_thousands(v: int) -> str:
    s = f"{abs(v):,}"
    return f"({s})" if v < 0 else s

def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

def pdf_bytes(pages: list[list[str]]) -> bytes:
    """Minimal PDF 1.4: catalog, pages, one Type1 font, one content stream and one page object per page."""
    objs: list[bytes] = []
    kids = " ".join(f"{5 + 2 * i} 0 R" for i in range(len(pages)))
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode())
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for lines in pages:
        text = " ".join(f"({_esc(l)}) Tj T*" for l in lines)
        stream = f"0.85 g 72 96 240 24 re f 0 g BT /F1 14 Tf 72 720 Td 18 TL {text} ET".encode()
        objs.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
        objs.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> "
                    b"/Contents " + str(len(objs)).encode() + b" 0 R >>")
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for o in offsets:
        out += f"{o:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)

def primary_pages(f: dict) -> list[list[str]]:
    return [[f"Form {f['form']}", f"Accession number {f['adsh']}", f"Central index key {f['cik']}",
             "Item 7. Management's discussion of results.",
             "This synthetic filing exists so the pipeline has bytes to move and pages to render."]]

def statement_pages(f: dict) -> list[list[str]]:
    v = f["values"]
    return [
        ["Consolidated statements of operations", "(in thousands)", f"Period ended {f['ddate']}",
         f"{LABELS['Revenues']}  {fmt_thousands(v['Revenues'])}",
         f"{LABELS['NetIncomeLoss']}  {fmt_thousands(v['NetIncomeLoss'])}"],
        ["Consolidated balance sheets", "(in thousands)", f"As of {f['ddate']}",
         f"{LABELS['Assets']}  {fmt_thousands(v['Assets'])}",
         f"{LABELS['Liabilities']}  {fmt_thousands(v['Liabilities'])}",
         f"{LABELS['StockholdersEquity']}  {fmt_thousands(v['StockholdersEquity'])}"],
    ]

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sums, index = [], []
    for f in FILINGS:
        for role, pages in (("primary", primary_pages(f)), ("statement", statement_pages(f))):
            p = OUT / f"{f['adsh']}-{role}.pdf"
            data = pdf_bytes(pages)
            p.write_bytes(data)
            h = hashlib.sha256(data).hexdigest()
            sums.append(f"{h}  {p.name}")
            index.append({"id": p.stem, "adsh": f["adsh"], "cik": f["cik"], "form": f["form"], "accepted": f["accepted"],
                          "page_role": role, "scale": f["scale"], "sha256": h})
            print(f"wrote {p.name} {len(data)} bytes {len(pages)} pages")
    (OUT / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8", newline="\n")
    (OUT / "index.json").write_text(json.dumps({"filings": index}, indent=2, sort_keys=True) + "\n",
                                    encoding="utf-8", newline="\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
