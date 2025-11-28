
from typing import List, Dict
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _compute_tfidf_similarity(job_description: str, candidate_texts: List[str]) -> List[float]:
    docs = [job_description] + candidate_texts
    vect = TfidfVectorizer(stop_words="english", max_features=5000)
    X = vect.fit_transform(docs)
    job_vec = X[0:1]
    cand_vecs = X[1:]
    sims = cosine_similarity(job_vec, cand_vecs)[0]
    return sims.tolist()

def _keyword_match_score(text: str, keywords: List[str]) -> float:
    if not keywords:
        return 0.0
    lower = text.lower()
    matches = sum(1 for kw in keywords if kw.lower() in lower)
    return matches / len(keywords)

def _skill_match_score(candidate_skills: List[str], required_skills: List[str]) -> int:
    if not required_skills:
        return 0
    cand_set = {s.lower() for s in candidate_skills}
    req_set = {s.lower() for s in required_skills}
    if not req_set:
        return 0
    matches = len(cand_set.intersection(req_set))
    return matches

def rank_candidates(
    candidates: List[Dict],
    job_description: str,
    job_keywords: List[str],
    required_skills: List[str],
):
    candidate_texts = [c.get("raw_text", "") for c in candidates]
    tfidf_scores = _compute_tfidf_similarity(job_description, candidate_texts)

    rows = []
    for c, tfidf_score in zip(candidates, tfidf_scores):
        text = c.get("raw_text", "")
        keyword_score = _keyword_match_score(text, job_keywords)
        skill_score = _skill_match_score(c.get("skills", []), required_skills)

        total = 0.6 * tfidf_score + 0.2 * keyword_score + 0.2 * skill_score

        rows.append(
            {
                "File Name": c.get("file_name"),
                "Name": c.get("name"),
                "Email": c.get("email"),
                "Percentage Matched": f"{tfidf_score * 100:.1f}%",
                "Required Skill Match": skill_score,
                "Total Score": total,
            }
        )

    df = pd.DataFrame(rows)
    df = df.sort_values(by="Total Score", ascending=False).reset_index(drop=True)
    return df
