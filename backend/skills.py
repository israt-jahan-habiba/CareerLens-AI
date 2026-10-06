"""Skill detection from text using a skill database (canonical name -> aliases)."""
import json
import re
from functools import lru_cache
from pathlib import Path

DATASET = Path(__file__).resolve().parent.parent / "dataset"

# Bare words that double as ordinary English words ("let's go", "spring weather",
# "react quickly", "agile movements"). Case-insensitive matching on these produces
# false positives in plain prose, so they are only matched against their
# Title-Case form, which is how a resume actually writes the skill name. Multi-word
# aliases built from them ("spring boot", "react native") are unaffected and stay
# case-insensitive, since those phrases are not ordinary English.
AMBIGUOUS_WORDS = {"go", "react", "spring", "angular", "swift", "express", "agile", "flow"}


@lru_cache(maxsize=1)
def load_skill_db() -> dict:
    with open(DATASET / "skills.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def _pattern(alias: str, case_sensitive: bool):
    # Custom boundaries so that "C++", "C#" and ".NET" are matched correctly
    # and "Java" does not match inside "JavaScript".
    flags = 0 if case_sensitive else re.I
    return re.compile(r"(?<![A-Za-z0-9+#])" + re.escape(alias) + r"(?![A-Za-z0-9+#])", flags)


def detect_skills(text: str) -> list:
    """Return a sorted list of canonical skill names found in `text`."""
    found = set()
    for canonical, aliases in load_skill_db().items():
        for alias in {canonical.lower(), *aliases}:
            # single-letter aliases such as "c" or "r" are too noisy on their own
            if len(alias) == 1:
                continue
            if alias in AMBIGUOUS_WORDS:
                # require the way a resume actually writes it: "Go", "React", "Spring"
                if _pattern(alias.capitalize(), case_sensitive=True).search(text):
                    found.add(canonical)
                    break
                continue
            if _pattern(alias, case_sensitive=False).search(text):
                found.add(canonical)
                break
    return sorted(found)
