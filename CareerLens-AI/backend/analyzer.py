"""Ties every module together into one analysis result."""
from .careers import interview_questions, recommend_careers
from .quality import quality_report, suggestions
from .resume_parser import extract_info, extract_text
from .scoring import ats_score
from .skills import detect_skills


def analyze_text(text: str, job_text: str = "") -> dict:
    info = extract_info(text)
    skills = detect_skills(text)
    match = ats_score(text, job_text, skills) if job_text.strip() else None
    return {
        "info": info,
        "skills": skills,
        "match": match,
        "quality": quality_report(text, info, skills),
        "suggestions": suggestions(text, info, skills, match),
        "careers": recommend_careers(skills),
        "interview_questions": interview_questions(skills, info["projects"]),
    }


def analyze_pdf(file_bytes: bytes, job_text: str = "") -> dict:
    text = extract_text(file_bytes)
    if not text:
        raise ValueError("No text found. The PDF may be a scanned image; upload a text-based PDF.")
    return analyze_text(text, job_text)


def rank_resumes(files: list, job_text: str) -> list:
    """files: list of (filename, bytes). Returns candidates sorted by ATS score."""
    ranked = []
    for name, data in files:
        try:
            text = extract_text(data)
            if not text:
                raise ValueError("no text")
            skills = detect_skills(text)
            m = ats_score(text, job_text, skills)
            info = extract_info(text)
            ranked.append({"file": name, "name": info["name"] or name, "score": m["score"],
                           "label": m["label"], "matched_skills": m["matched_skills"],
                           "missing_skills": m["missing_skills"], "error": None})
        except Exception as exc:  # keep ranking the remaining files
            ranked.append({"file": name, "name": name, "score": 0, "label": "Unreadable",
                           "matched_skills": [], "missing_skills": [], "error": str(exc)})
    ranked.sort(key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
    return ranked
