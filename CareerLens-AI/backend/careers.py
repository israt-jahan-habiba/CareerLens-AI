"""Career recommendation and interview question generation."""
import json
import random
from functools import lru_cache

from .skills import DATASET


@lru_cache(maxsize=1)
def _careers() -> dict:
    with open(DATASET / "careers.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _questions() -> dict:
    with open(DATASET / "questions.json", encoding="utf-8") as f:
        return json.load(f)


def recommend_careers(skills: list, top_n: int = 3) -> list:
    have = set(skills)
    results = []
    for career, required in _careers().items():
        hit = [s for s in required if s in have]
        if not hit:
            continue
        results.append({
            "career": career,
            "match": round(len(hit) / len(required) * 100),
            "matched_skills": hit,
            "missing_skills": [s for s in required if s not in have][:4],
        })
    results.sort(key=lambda r: r["match"], reverse=True)
    return results[:top_n]


def interview_questions(skills: list, projects: list, per_skill: int = 1, limit: int = 8) -> list:
    rng = random.Random(len(skills) * 31 + len(projects))  # stable output per resume
    out = []
    for skill in skills:
        bank = _questions().get(skill)
        if bank:
            out.extend({"topic": skill, "question": q}
                       for q in rng.sample(bank, min(per_skill, len(bank))))
    for title in projects[:2]:
        out.append({"topic": "Project", "question": f'Walk me through "{title}": what problem did it solve and what would you improve?'})
    if projects:
        out.append({"topic": "Project", "question": "How did you design the database or data model for your project?"})
    return out[:limit]
