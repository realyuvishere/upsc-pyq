"""Scan the PYQs/ folder and emit ./data.json.

Every PDF filename roughly follows:
    {Subject}[_Paper..{RomanNum}]_{Phase}_{Year}_{Category}.pdf
but the naming drifts a lot across years, so we normalise Subject / Category
so that (e.g.) "Mathematics Paper I" lines up across 2016..2025.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
PYQS_DIR = os.path.join(ROOT, "PYQs")
OUT = os.path.join(ROOT, ".", "data.json")
OUT_JS = os.path.join(ROOT, ".", "data.js")

# --- category (folder name) normalisation ------------------------------------
CATEGORY_MAP = {
    "Optional_Subjects": "Optional",
    "Optional": "Optional",
    "Optional_Literature": "Literature",
    "Literature_Subjects": "Literature",
    "Compulsory_Subjects": "Compulsory Language",
    "Compulsory": "Compulsory Language",
    "Indian_Languages_(Compulsory)": "Compulsory Language",
    "General_Studies": "General Studies",
    "General": "General",
}

# --- subject synonym normalisation -------------------------------------------
SUBJECT_SYNONYMS = {
    "agricultural": "Agriculture",
    "agriculture": "Agriculture",
    "commerce and accountancy": "Commerce & Accountancy",
    "commerce & accountancy": "Commerce & Accountancy",
    "political science and ir": "Political Science & IR",
    "political science & ir": "Political Science & IR",
    "political science and international relation": "Political Science & IR",
    "political science and international relations": "Political Science & IR",
    "kashimiri": "Kashmiri",
    "kashmiri": "Kashmiri",
    "oriya": "Odia",
    "odia": "Odia",
    "santhali": "Santali",
    "santali": "Santali",
    "sindhi devanagari": "Sindhi (Devanagari)",
    "sindhi devnagari": "Sindhi (Devanagari)",
    "sindhi (devnagari)": "Sindhi (Devanagari)",
    "sindhi (devanagari)": "Sindhi (Devanagari)",
    "sindhi (arabic)": "Sindhi (Arabic)",
}

ROMAN = ("IV", "III", "II", "I")


def normalize_category(folder):
    return CATEGORY_MAP.get(folder, folder.replace("_", " "))


def normalize_subject(subj):
    s = subj.replace("_", " ")
    s = s.replace("(Compulsory)", " ").replace("Compulsory", " ")
    s = re.sub(r"\bLiterature\b", " ", s)
    s = re.sub(r"\bDev\b", " ", s)
    s = s.replace("&", " & ")
    s = re.sub(r"\s+", " ", s).strip(" -")
    # drop stray unmatched parens left behind by removing "Compulsory" etc.
    if s.count("(") == 0:
        s = s.replace(")", "").strip()
    key = s.lower()
    if key.startswith("animal hus"):
        return "Animal Husbandry & Veterinary Science"
    if key in SUBJECT_SYNONYMS:
        return SUBJECT_SYNONYMS[key]
    return s


def parse(filename, folder):
    stem = filename[:-4] if filename.lower().endswith(".pdf") else filename

    m = re.search(r"_(Mains|Prelims)_(\d{4})", stem)
    if m:
        phase = m.group(1)
        year = int(m.group(2))
        prefix = stem[: m.start()]
    else:
        phase = "Mains"
        ym = re.search(r"(\d{4})", stem)
        year = int(ym.group(1)) if ym else None
        prefix = stem[: ym.start()].rstrip("_") if ym else stem

    # paper roman numeral (only when a "Paper" marker or "_-_" separator exists)
    paper = None
    rm = re.search(r"(IV|III|II|I)$", prefix)
    if rm and re.search(r"Paper|_-_", prefix):
        paper = rm.group(1)

    # strip the paper marker to isolate the subject
    subj = re.sub(r"_?_?Paper.*$", "", prefix)
    if subj == prefix:
        subj = re.sub(r"_-_(IV|III|II|I)$", "", prefix)

    subject = normalize_subject(subj)
    return {
        "subject": subject,
        "paper": paper,
        "phase": phase,
        "year": year,
        "category": normalize_category(folder),
    }


def main():
    records = []
    for dirpath, _dirs, files in os.walk(PYQS_DIR):
        for fn in files:
            if not fn.lower().endswith(".pdf"):
                continue
            folder = os.path.basename(dirpath)
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT).replace("\\", "/")
            rec = parse(fn, folder)
            rec["path"] = rel
            rec["filename"] = fn
            records.append(rec)

    records.sort(key=lambda r: (r["subject"], r["paper"] or "", -(r["year"] or 0)))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=1)
    # data.js lets index.html work by double-click (file://) with no server
    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write("window.PYQ_DATA = ")
        json.dump(records, f, ensure_ascii=False)
        f.write(";\n")

    years = sorted({r["year"] for r in records if r["year"]})
    subjects = sorted({r["subject"] for r in records})
    print(f"Wrote {len(records)} records to {OUT}")
    print(f"Years: {years[0]}..{years[-1]} ({len(years)})")
    print(f"Subjects ({len(subjects)}):")
    for s in subjects:
        print("   ", s)


if __name__ == "__main__":
    main()
