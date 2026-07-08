# upsc-pyq

A simple python scrapper to help UPSC CSE aspirants to scrap all PYQs available on the official UPSC website [https://upsc.gov.in/examinations/previous-question-papers](https://upsc.gov.in/examinations/previous-question-papers).
Currently, it fetches all the subjects, across all years. You are free to alter this behaviour as per convenience.

## Installation Steps

### Setup virtual env (optional)

#### For Linux / MacOS / WSL

```bash
python -m venv .venv
python .venv/bin/activate
```

#### For Windows

```bash
python -m venv .venv
python .venv\Scripts\activate
```

### Install dependencies

```
pip install -r requirements.txt
```

### Run the app

```
python main.py
```

## Browsing the papers (web app)

A lightweight, dependency-free web app is included to browse the downloaded PYQs.

1. Build the index (scans `PYQs/` into `webapp/data.js`):

   ```
   python build_index.py
   ```

2. Open `webapp/index.html` in your browser (just double-click it — no server needed).

Rerun `build_index.py` whenever you download new papers.

### What you can do

- **Browse by year** — pick a year chip; results group by category (Optional, Literature, Compulsory Language, General Studies, General).
- **One paper across years** — pick a subject and paper (e.g. *Management · Paper I*) to see every year 2016–2025.
- **Compare multiple subjects** — select several subjects (e.g. *Mathematics* and *Statistics*, Paper I / II / both) and switch to **Matrix** view for a year-by-year comparison grid.

Filters (subject, paper, year, category, phase, text search) combine freely, and each result links straight to the source PDF.

