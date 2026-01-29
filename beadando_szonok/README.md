# GC Content Calculator

Simple web app (Flask) that calculates GC content of a DNA sequence.

Test sequence: `ATGCGTACGTTAGC` → expected GC = **61.54%**

Run locally:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Deploy on Render / Heroku by connecting the repository and using `gunicorn app:app` (Procfile included).
