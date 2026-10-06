"""CareerLens AI - Flask server. Run:  python -m backend.app"""
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from .analyzer import analyze_pdf, rank_resumes

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
MAX_MB = 10

app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = MAX_MB * 5 * 1024 * 1024  # allows several PDFs for ranking


def _is_pdf(storage) -> bool:
    return bool(storage and storage.filename and storage.filename.lower().endswith(".pdf"))


def _error(message: str, code: int = 400):
    return jsonify({"error": message}), code


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/analyze")
def analyze():
    resume = request.files.get("resume")
    if not _is_pdf(resume):
        return _error("Upload your resume as a PDF file.")
    data = resume.read()
    if len(data) > MAX_MB * 1024 * 1024:
        return _error(f"The file is larger than {MAX_MB} MB.", 413)
    try:
        result = analyze_pdf(data, request.form.get("job_description", ""))
    except ValueError as exc:
        return _error(str(exc), 422)
    except Exception:
        return _error("We could not read this PDF. Try exporting it again.", 422)
    return jsonify(result)


@app.post("/api/rank")
def rank():
    job = request.form.get("job_description", "").strip()
    files = [f for f in request.files.getlist("resumes") if _is_pdf(f)]
    if not job:
        return _error("Paste the job description to rank candidates against.")
    if len(files) < 2:
        return _error("Upload at least two PDF resumes to compare.")
    return jsonify({"ranking": rank_resumes([(f.filename, f.read()) for f in files], job)})


if __name__ == "__main__":
    import os

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
    
