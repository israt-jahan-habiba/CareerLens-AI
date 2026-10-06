"""ATS scoring: keyword coverage + TF-IDF cosine similarity."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .skills import detect_skills

KEYWORD_WEIGHT = 0.75
SIMILARITY_WEIGHT = 0.25


def tfidf_similarity(resume_text: str, job_text: str) -> float:
    """Cosine similarity (0..1) between resume and job description."""
    if not resume_text.strip() or not job_text.strip():
        return 0.0
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    try:
        matrix = vec.fit_transform([resume_text, job_text])
    except ValueError:  # empty vocabulary
        return 0.0
    return float(cosine_similarity(matrix[0], matrix[1])[0][0])


def label_for(score: float) -> str:
    if score >= 80:
        return "Excellent match"
    if score >= 65:
        return "Good match"
    if score >= 45:
        return "Partial match"
    return "Weak match"


def ats_score(resume_text: str, job_text: str, resume_skills=None) -> dict:
    """Compare a resume with a job description."""
    resume_skills = resume_skills if resume_skills is not None else detect_skills(resume_text)
    job_skills = detect_skills(job_text)
    matched = [s for s in job_skills if s in resume_skills]
    missing = [s for s in job_skills if s not in resume_skills]

    similarity = tfidf_similarity(resume_text, job_text)
    if job_skills:
        coverage = len(matched) / len(job_skills)
        score = KEYWORD_WEIGHT * coverage + SIMILARITY_WEIGHT * min(1.0, similarity * 2)
    else:  # job description has no known skills -> rely on text similarity
        coverage = 0.0
        score = min(1.0, similarity * 2)

    score = round(score * 100)
    return {
        "score": score,
        "label": label_for(score),
        "keyword_coverage": round(coverage * 100),
        "text_similarity": round(similarity * 100),
        "matched_skills": matched,
        "missing_skills": missing,
        "job_skills": job_skills,
    }
