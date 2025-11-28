
import re
import os
import tempfile
from typing import Dict, List

from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document

SECTION_HEADERS = [
    "education",
    "work experience",
    "experience",
    "professional experience",
    "skills",
    "projects",
    "certifications",
]

COMMON_SKILLS = [
    "python", "java", "c++", "c", "javascript", "typescript", "html", "css",
    "react", "angular", "django", "flask", "node", "node.js",
    "sql", "mysql", "postgresql", "mongodb",
    "machine learning", "deep learning", "data science",
    "nlp", "natural language processing",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "git", "docker", "kubernetes", "aws", "azure", "gcp"
]

def _extract_text_from_pdf(path: str) -> str:
    try:
        return extract_pdf_text(path)
    except Exception:
        return ""

def _extract_text_from_docx(path: str) -> str:
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""

def _extract_text_from_txt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def extract_text_from_upload(uploaded_file) -> str:
    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            text = _extract_text_from_pdf(tmp_path)
        elif suffix == ".docx":
            text = _extract_text_from_docx(tmp_path)
        else:
            text = _extract_text_from_txt(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return text

def extract_email(text: str) -> str:
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> str:
    match = re.search(r"(\+?\d[\d\-\s]{8,}\d)", text)
    return match.group(0) if match else ""

def extract_name(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if "@" in line:
            continue
        if len(line.split()) > 5:
            continue
        if line.replace(" ", "").isalpha():
            return line
    return ""

def extract_sections(text: str):
    lower = text.lower()
    sections = {}
    positions = []
    for header in SECTION_HEADERS:
        idx = lower.find(header)
        if idx != -1:
            positions.append((header, idx))

    if not positions:
        return sections

    positions.sort(key=lambda x: x[1])

    for i, (header, start) in enumerate(positions):
        end = positions[i + 1][1] if i + 1 < len(positions) else len(text)
        content = text[start:end].strip()
        sections[header] = content

    return sections

def extract_skills(text: str):
    lower = text.lower()
    found = set()
    for skill in COMMON_SKILLS:
        if skill in lower:
            found.add(skill)
    return sorted(found)

def parse_resume_file(uploaded_file):
    raw_text = extract_text_from_upload(uploaded_file)
    email = extract_email(raw_text)
    phone = extract_phone(raw_text)
    name = extract_name(raw_text)
    sections = extract_sections(raw_text)
    skills = extract_skills(raw_text)

    education = ""
    experience = ""

    for header, content in sections.items():
        if "education" in header:
            education = content
        if "experience" in header:
            experience = content

    return {
        "file_name": uploaded_file.name,
        "raw_text": raw_text,
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education,
        "experience": experience,
    }
