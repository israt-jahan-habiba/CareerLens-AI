import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from backend.app import app
from backend.scoring import ats_score
from backend.skills import detect_skills

RESUME = """Israt Jahan Habiba
israt@example.com | +880 1712 345678
github.com/israt | linkedin.com/in/israt
Education
BSc Computer Science, Brac University
Skills
Python, Java, SQL, Git, Machine Learning
Projects
Lost and Found System
Baby Day Care
Developed a web app used by 200 users with Flask and SQL.
"""
JOB = "Looking for Python developer with Python, SQL, Django, Machine Learning, Git"


def make_pdf(text: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = 800
    for line in text.splitlines():
        c.drawString(50, y, line)
        y -= 16
    c.save()
    return buf.getvalue()


def test_skill_detection_boundaries():
    skills = detect_skills("I know JavaScript and C++ but not Java.")
    assert "JavaScript" in skills and "C++" in skills and "Java" in skills
    assert "Java" not in detect_skills("Only JavaScript here")


def test_ambiguous_words_need_title_case():
    # "go", "react", "spring", "agile" are common English words; lowercase,
    # mid-sentence use must NOT be detected as skills.
    prose = detect_skills("Let's go to the market and react quickly to the spring weather")
    assert prose == []
    # but a resume that properly capitalizes them must still be detected.
    resume = detect_skills("Skills: Go, React, Spring Boot, Agile development")
    assert {"Go", "React", "Spring Boot", "Agile"} <= set(resume)


def test_ats_score_reports_missing_skills():
    m = ats_score(RESUME, JOB)
    assert "Django" in m["missing_skills"]
    assert {"Python", "SQL", "Git", "Machine Learning"} <= set(m["matched_skills"])
    assert 0 < m["score"] < 100


def test_api_analyze():
    client = app.test_client()
    r = client.post("/api/analyze", data={
        "resume": (io.BytesIO(make_pdf(RESUME)), "cv.pdf"), "job_description": JOB},
        content_type="multipart/form-data")
    assert r.status_code == 200
    body = r.get_json()
    assert body["info"]["email"] == "israt@example.com"
    assert body["match"]["score"] > 0
    assert body["careers"]


def test_api_rejects_non_pdf():
    r = app.test_client().post("/api/analyze", data={"resume": (io.BytesIO(b"x"), "cv.txt")},
                               content_type="multipart/form-data")
    assert r.status_code == 400


def test_api_rank_orders_candidates():
    weak = "Rahim Uddin\nSkills\nExcel, Communication"
    r = app.test_client().post("/api/rank", data={
        "job_description": JOB,
        "resumes": [(io.BytesIO(make_pdf(RESUME)), "israt.pdf"), (io.BytesIO(make_pdf(weak)), "rahim.pdf")]},
        content_type="multipart/form-data")
    ranking = r.get_json()["ranking"]
    assert ranking[0]["file"] == "israt.pdf" and ranking[0]["score"] > ranking[1]["score"]
