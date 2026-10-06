"""Resume quality checks and improvement suggestions."""
import re

METRIC_RE = re.compile(r"\d+\s*(%|\+|k\b|users|customers|students|records|x\b)|\b\d{2,}\b", re.I)
ACTION_VERBS = ["developed", "built", "designed", "implemented", "created", "led",
                "improved", "optimized", "automated", "deployed", "analyzed", "managed"]


def quality_report(text: str, info: dict, skills: list) -> dict:
    sections = set(info["sections_found"])
    checks = [
        ("Contact email", bool(info["email"])),
        ("Phone number", bool(info["phone"])),
        ("LinkedIn profile", bool(info["linkedin"])),
        ("GitHub link", bool(info["github"])),
        ("Education section", "education" in sections),
        ("Skills section", "skills" in sections),
        ("Projects section", "projects" in sections),
        ("Experience or internship", "experience" in sections),
        ("Reasonable length (150-900 words)", 150 <= info["word_count"] <= 900),
        ("At least 5 detected skills", len(skills) >= 5),
    ]
    passed = sum(1 for _, ok in checks if ok)
    return {
        "score": round(passed / len(checks) * 100),
        "checks": [{"name": n, "ok": ok} for n, ok in checks],
    }


def suggestions(text: str, info: dict, skills: list, match: dict = None) -> list:
    tips = []
    if not METRIC_RE.search(text):
        tips.append('Add measurable achievements. Instead of "Made a website", write '
                    '"Developed a website used by 200 users".')
    if not info["github"]:
        tips.append("Add a GitHub link so recruiters can see your projects.")
    if not info["linkedin"]:
        tips.append("Add your LinkedIn profile URL to the header.")
    if "projects" not in info["sections_found"]:
        tips.append("Add a Projects section with one or two lines per project.")
    if "skills" not in info["sections_found"]:
        tips.append("Add a dedicated Skills section so ATS software can find your keywords.")
    if len(skills) < 5:
        tips.append("List more technical keywords (tools, frameworks, databases you have used).")
    if not any(v in text.lower() for v in ACTION_VERBS):
        tips.append("Start bullet points with action verbs such as Developed, Built, Implemented.")
    if info["word_count"] > 900:
        tips.append("Your resume is long. Aim for one page (about 400-700 words).")
    if info["word_count"] < 150:
        tips.append("Your resume looks short. Describe your projects and responsibilities.")
    if match and match["missing_skills"]:
        tips.append("For this job, consider adding (only if you really have them): "
                    + ", ".join(match["missing_skills"]) + ".")
    return tips
