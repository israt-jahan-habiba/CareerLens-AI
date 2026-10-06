<div align="center">

# CareerLens AI

**An AI-powered resume analyzer, ATS scorer, and career-matching platform**

Upload a resume, get the same read a hiring system would give it — detected skills, an ATS match score against a real job description, resume quality checks, career recommendations, and interview questions to practice.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?logo=flask&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-NLP-F7931E?logo=scikitlearn&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-blue)

[Features](#features) · [Demo](#demo) · [Getting started](#getting-started) · [API](#api-reference) · [How it works](#how-it-works) · [Roadmap](#roadmap)

</div>

---

## Why I built this

Most "resume analyzer" tutorials stop at "upload a PDF, print a score." CareerLens AI goes further and works closer to a real **ATS (Applicant Tracking System)**: it parses a resume into structured data, scores it against an actual job description using NLP, checks it for the things recruiters actually look for, and turns detected skills into career suggestions and interview prep — end to end, with a working UI on top.

## Demo

<!-- Replace with your own screenshot or GIF once you deploy it -->
<p align="center">
  <img src="screenshots/demo.png" alt="CareerLens AI screenshot" width="80%">
</p>

🔗 **Live demo:** _add your deployed link here (Render / Railway / Hugging Face Spaces)_

## Features

| | Feature | Details |
|---|---|---|
| 📄 | **PDF parsing** | Extracts text from resumes with `pdfplumber`, no manual copy-paste |
| 🧠 | **Info extraction** | Pulls out name, email, phone, LinkedIn, GitHub, education, and projects |
| 🏷️ | **Skill detection** | Matches 68 skills and their aliases (e.g. "JS" → JavaScript) from an editable JSON dataset |
| 🎯 | **ATS score** | 75% keyword coverage + 25% TF-IDF cosine similarity against a job description |
| 🔍 | **Job matching** | Shows exactly which required skills are matched vs. missing |
| ✅ | **Resume quality checker** | 10 automated checks: contact info, sections present, length, keyword density |
| 💡 | **Improvement suggestions** | Rule-based tips — add metrics, add a GitHub link, use action verbs, and more |
| 🚀 | **Career recommendations** | Ranks careers by skill overlap using an editable careers dataset |
| 🎤 | **Interview question generator** | Generates questions tailored to your detected skills and projects |
| 🏆 | **Candidate ranking** | Upload multiple resumes and rank them against one job description |

## Getting started

### Prerequisites
- Python 3.9+

### Installation

```bash
git clone https://github.com/<your-username>/CareerLens-AI.git
cd CareerLens-AI

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Run it

```bash
python -m backend.app
```

Open **http://127.0.0.1:5000** and upload a resume.

### Run the tests

```bash
pytest
```

## Project structure

```
CareerLens-AI
├── frontend/              index.html, style.css, script.js
├── backend/
│   ├── app.py             Flask routes
│   ├── analyzer.py        combines all modules into one report
│   ├── resume_parser.py   PDF → text, structured info extraction
│   ├── skills.py          skill detection engine
│   ├── scoring.py         ATS score (TF-IDF + keyword coverage)
│   ├── quality.py         quality checks + improvement suggestions
│   └── careers.py         career recommendations + interview questions
├── dataset/               skills.json, careers.json, questions.json (editable)
├── models/                reserved for future trained models
├── tests/                 pytest suite
├── screenshots/           add your screenshots here
└── requirements.txt
```

## API reference

| Method | Route | Body | Returns |
|---|---|---|---|
| `POST` | `/api/analyze` | `resume` (PDF), `job_description` (optional) | Full analysis: info, skills, ATS score, quality, suggestions, careers, questions |
| `POST` | `/api/rank` | `resumes` (2+ PDFs), `job_description` | Candidates ranked by ATS score |
| `GET` | `/api/health` | — | `{"status": "ok"}` |

## How it works

**ATS score**
```
score = 0.75 × (matched job skills ÷ total job skills) + 0.25 × min(1, 2 × cosine_similarity)
```
The keyword term rewards resumes that literally contain the skills a job asks for; the TF-IDF/cosine similarity term catches relevant phrasing the keyword list misses. Weights are configurable in `backend/scoring.py`.

**Skill detection** matches against a dataset of 68 canonical skills with aliases (`dataset/skills.json`), using word-boundary regex so "Java" doesn't false-positive inside "JavaScript," and "C++" / "C#" match correctly.

**Career recommendations** and **interview questions** are driven by two more editable JSON files (`dataset/careers.json`, `dataset/questions.json`) — add your own careers, skills, or questions without touching any code.

## Tech stack

- **Backend:** Python, Flask
- **NLP:** scikit-learn (TF-IDF, cosine similarity), regex-based extraction
- **PDF parsing:** pdfplumber
- **Frontend:** vanilla HTML/CSS/JS (no build step)
- **Testing:** pytest

## Roadmap

- [x] PDF upload + text extraction
- [x] Skill detection + ATS scoring
- [x] Job matching + improvement suggestions
- [x] Career recommendations + interview questions
- [ ] OCR support for scanned PDFs
- [ ] spaCy-based named entity recognition
- [ ] Save analysis history (PostgreSQL / MongoDB)
- [ ] Dockerize and deploy a live demo
- [ ] LLM-assisted rewriting of weak bullet points

## Contributing

Issues and pull requests are welcome. If you're extending the skill, career, or question datasets, no code changes are needed — just edit the JSON files in `dataset/`.

## License

Distributed under the MIT License. See `LICENSE` for details.

---

<div align="center">
Built by <strong><a href="https://github.com/<your-username>">Your Name</a></strong> — feel free to ⭐ this repo if you found it useful.
</div>
