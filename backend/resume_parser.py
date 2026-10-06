"""PDF -> text extraction and structured information extraction."""
import io
import re

import pdfplumber

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{8,}\d)")
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s)]+", re.I)
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[^\s)]+", re.I)

SECTION_ALIASES = {
    "education": ["education", "academic background", "academics"],
    "skills": ["skills", "technical skills", "core competencies", "technologies"],
    "projects": ["projects", "academic projects", "personal projects"],
    "experience": ["experience", "work experience", "employment", "internship", "internships"],
    "summary": ["summary", "objective", "profile", "about me"],
    "certifications": ["certifications", "certificates", "courses"],
    "achievements": ["achievements", "awards", "honors"],
}
DEGREE_RE = re.compile(
    r"\b(b\.?sc\.?|m\.?sc\.?|bachelor|master|ph\.?d|b\.?tech|m\.?tech|diploma|hsc|ssc|"
    r"university|college|institute)\b", re.I)


def extract_text(file_bytes: bytes) -> str:
    """Extract text from a PDF given as raw bytes."""
    pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def _heading_of(line: str):
    clean = re.sub(r"[^a-z ]", "", line.lower()).strip()
    if not clean or len(clean) > 30:
        return None
    for section, names in SECTION_ALIASES.items():
        if clean in names:
            return section
    return None


def split_sections(text: str) -> dict:
    sections, current = {}, "header"
    for line in text.splitlines():
        heading = _heading_of(line)
        if heading:
            current = heading
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(line.strip())
    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def guess_name(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if not line or EMAIL_RE.search(line) or PHONE_RE.search(line):
            continue
        if 2 <= len(line.split()) <= 5 and not re.search(r"\d", line):
            return line
        break
    return ""


def extract_info(text: str) -> dict:
    sections = split_sections(text)
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    linkedin = LINKEDIN_RE.search(text)
    github = GITHUB_RE.search(text)

    edu_lines = []
    for line in sections.get("education", "").splitlines():
        if line and (DEGREE_RE.search(line) or len(edu_lines) < 2):
            edu_lines.append(line)

    project_lines = [
        re.sub(r"^[\-•*▪\d.\s]+", "", l)
        for l in sections.get("projects", "").splitlines() if l.strip()
    ]
    # Short lines are usually project titles; long lines are descriptions.
    project_titles = [l for l in project_lines if len(l.split()) <= 8][:8]

    return {
        "name": guess_name(text),
        "email": email.group(0) if email else "",
        "phone": phone.group(0).strip() if phone else "",
        "linkedin": linkedin.group(0) if linkedin else "",
        "github": github.group(0) if github else "",
        "education": edu_lines[:4],
        "projects": project_titles,
        "sections_found": sorted(k for k in sections if k != "header"),
        "word_count": len(text.split()),
    }
