"""Compare necro (txt) vs forbidden_rites_pdf (PDF) chunk quality."""
import os
import re

base = r"E:\munich_handbook_research\data\sources"

# Sample several chunks to compare
for cid in [5, 10, 15, 20, 25, 30]:
    n_path = os.path.join(base, "necro", f"chunk_{cid:03d}.txt")
    p_path = os.path.join(base, "forbidden_rites_pdf", f"chunk_{cid:03d}.txt")
    
    if not os.path.exists(n_path) or not os.path.exists(p_path):
        continue
    
    with open(n_path, "r", encoding="utf-8") as f:
        necro = f.read()
    with open(p_path, "r", encoding="utf-8") as f:
        pdf = f.read()
    
    # Skip headers (first 200 chars)
    n_body = necro[200:]
    p_body = pdf[200:]
    
    # Check for table-like content (multiple consecutive spaces = column alignment)
    n_table_lines = [l for l in n_body.split("\n") if re.search(r"\S\s{3,}\S", l)]
    p_table_lines = [l for l in p_body.split("\n") if re.search(r"\S\s{3,}\S", l)]
    
    # Check for page markers
    n_pages = re.findall(r"(?:page|p\.|pp\.)\s*\d+", n_body, re.I)
    p_pages = re.findall(r"(?:page|p\.|pp\.)\s*\d+", p_body, re.I)
    
    # Check for Latin text
    latin_words = ["dominus", "spiritus", "conjuro", "exorcizo", "daemon", "circul"]
    n_latin = sum(n_body.lower().count(w) for w in latin_words)
    p_latin = sum(p_body.lower().count(w) for w in latin_words)
    
    # Check for footnote/endnote markers
    n_notes = len(re.findall(r"\b\d{1,3}\b(?=\s*[A-Z])", n_body))
    p_notes = len(re.findall(r"\b\d{1,3}\b(?=\s*[A-Z])", p_body))
    
    print(f"Chunk {cid:3d}: necro={len(necro):5d}ch  pdf={len(pdf):5d}ch  "
          f"table_lines(n/p)={len(n_table_lines):2d}/{len(p_table_lines):2d}  "
          f"pages(n/p)={len(n_pages):2d}/{len(p_pages):2d}  "
          f"latin(n/p)={n_latin:2d}/{p_latin:2d}")
    
    # Show any table-like content from the PDF that txt missed
    if len(p_table_lines) > len(n_table_lines) + 2:
        print(f"  PDF has more structured content. Sample:")
        for line in p_table_lines[:3]:
            print(f"    | {line.strip()[:100]}")

# Also check: are they the same text or different content?
print("\n--- CONTENT OVERLAP CHECK (chunk 10) ---")
with open(os.path.join(base, "necro", "chunk_010.txt"), "r", encoding="utf-8") as f:
    n10 = f.read()[200:]
with open(os.path.join(base, "forbidden_rites_pdf", "chunk_010.txt"), "r", encoding="utf-8") as f:
    p10 = f.read()[200:]

# Find common long phrases
n_words = set(n10.split())
p_words = set(p10.split())
overlap = len(n_words & p_words) / max(len(n_words | p_words), 1)
print(f"Word-level overlap: {overlap:.0%}")
print(f"Necro unique words sample: {list(n_words - p_words)[:10]}")
print(f"PDF unique words sample: {list(p_words - n_words)[:10]}")
