import numpy as np
import json
from sentence_transformers import SentenceTransformer

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

def rank_courses(user_vector, course_rows) -> list[dict]:
    results = []
    for row in course_rows:
        if not row.embedding:
            continue
        vec = json.loads(row.embedding)
        results.append({
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "similarity_score": round(cosine_similarity(user_vector, vec), 4)
        })
    return sorted(results, key=lambda x: x["similarity_score"], reverse=True)