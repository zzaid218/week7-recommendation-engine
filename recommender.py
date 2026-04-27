import numpy as np
from models import Embedding, Course

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def recommend_courses(db, user_vector, top_n=3):
    embeddings = db.query(Embedding).filter_by(entity_type="course").all()

    scores = []

    for emb in embeddings:
        if not emb.vector:
            continue

        score = cosine_similarity(user_vector, emb.vector)
        scores.append((emb.entity_id, score))

    scores.sort(key=lambda x: x[1], reverse=True)

    results = []

    for course_id, score in scores[:top_n]:
        course = db.query(Course).filter(Course.id == course_id).first()

        if course:
            results.append({
                "course": course.title,
                "score": float(score)
            })

    return results
