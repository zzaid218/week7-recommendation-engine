import numpy as np
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> list[float]:
    return _model.encode(text).tolist()

def embed_skills(skills: list[str]) -> list[float]:
    vectors = [_model.encode(s) for s in skills]
    return np.mean(vectors, axis=0).tolist()

def cosine_similarity(a, b) -> float:
    a, b = np.array(a), np.array(b)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na and nb else 0.0

def rank_courses(user_vector, courses) -> list[dict]:
    results = []
    for course in courses:
        vec = course.get_embedding()
        if vec is None:
            continue
        results.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "similarity_score": round(cosine_similarity(user_vector, vec), 4)
        })
    return sorted(results, key=lambda x: x["similarity_score"], reverse=True)