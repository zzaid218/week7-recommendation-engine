from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

from database import engine
from models import create_tables
from embeddings import embed_skills, rank_courses
from seed import seed
from llm import extract_skills_with_llm, explain_recommendation
from crud import (
    get_all_courses, get_user_by_id, get_user_skills,
    get_all_users, create_user, save_log, get_all_logs
)

create_tables(engine)
seed()

app = FastAPI(title="Skills & Course Recommendation Engine")

# --- Schemas ---
class RecommendByUser(BaseModel):
    user_id: int
    top_n: int = 3

class RecommendByText(BaseModel):
    skills_text: str
    top_n: int = 3

class ExtractAndRecommend(BaseModel):
    text: str
    top_n: int = 3

class AddUser(BaseModel):
    name: str
    skills: list[str]

# --- Helpers ---
def add_explanations(skills, ranked):
    for course in ranked:
        course["explanation"] = explain_recommendation(
            skills, course["title"], course["description"]
        )
    return ranked

# --- Routes ---
@app.get("/")
def root():
    return {"message": "API is running"}

@app.post("/api/recommend")
def recommend_by_text(req: RecommendByText):
    skills = [s.strip() for s in req.skills_text.replace(",", " ").split() if s.strip()]
    if not skills:
        raise HTTPException(400, "No skills provided.")
    with engine.connect() as conn:
        all_courses = get_all_courses(conn)
        user_vec = embed_skills(skills)
        ranked = rank_courses(user_vec, all_courses)[:req.top_n]
        ranked = add_explanations(skills, ranked)
        save_log(conn, None, skills, ranked)
    return {
        "extracted_skills": skills,
        "recommended_courses": [c["title"] for c in ranked],
        "top_recommendations": ranked,
        "explanation": "Courses ranked by cosine similarity to your skill embeddings."
    }

@app.post("/api/recommend/by-user")
def recommend_by_user(req: RecommendByUser):
    with engine.connect() as conn:
        user = get_user_by_id(conn, req.user_id)
        if not user:
            raise HTTPException(404, "User not found.")
        skills = get_user_skills(conn, req.user_id)
        if not skills:
            return {
                "user_id": req.user_id,
                "user": user.name,
                "extracted_skills": [],
                "recommended_courses": [],
                "explanation": "No skills found for this user."
            }
        all_courses = get_all_courses(conn)
        if not all_courses:
            raise HTTPException(404, "No courses available.")
        user_vec = embed_skills(skills)
        ranked = rank_courses(user_vec, all_courses)[:req.top_n]
        ranked = add_explanations(skills, ranked)
        save_log(conn, req.user_id, skills, ranked)
    return {
        "user_id": req.user_id,
        "user": user.name,
        "extracted_skills": skills,
        "recommended_courses": [c["title"] for c in ranked],
        "top_recommendations": ranked,
        "explanation": f"Top {req.top_n} courses matched to {user.name}'s skills."
    }

@app.post("/api/recommend/from-cv")
def recommend_from_cv(req: ExtractAndRecommend):
    skills = extract_skills_with_llm(req.text)
    if not skills:
        raise HTTPException(400, "Could not extract skills from text.")
    with engine.connect() as conn:
        all_courses = get_all_courses(conn)
        if not all_courses:
            raise HTTPException(404, "No courses available.")
        user_vec = embed_skills(skills)
        ranked = rank_courses(user_vec, all_courses)[:req.top_n]
        ranked = add_explanations(skills, ranked)
        save_log(conn, None, skills, ranked)
    return {
        "input_text": req.text,
        "extracted_skills": skills,
        "recommended_courses": [c["title"] for c in ranked],
        "top_recommendations": ranked,
        "explanation": "Skills extracted by GPT, courses ranked by semantic similarity."
    }

@app.post("/api/users")
def add_user(req: AddUser):
    with engine.connect() as conn:
        user_id = create_user(conn, req.name, req.skills)
    return {"id": user_id, "name": req.name, "skills": req.skills}

@app.get("/api/users")
def list_users():
    with engine.connect() as conn:
        all_users = get_all_users(conn)
        result = []
        for u in all_users:
            skills = get_user_skills(conn, u.id)
            result.append({"id": u.id, "name": u.name, "skills": skills})
    return result

@app.get("/api/courses")
def list_courses():
    with engine.connect() as conn:
        all_courses = get_all_courses(conn)
    return [{"id": c.id, "title": c.title, "description": c.description} for c in all_courses]

@app.get("/api/logs")
def get_logs():
    with engine.connect() as conn:
        logs = get_all_logs(conn)
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "input_skills": json.loads(l.input_skills),
            "recommended_courses": json.loads(l.recommended_courses),
            "created_at": l.created_at
        }
        for l in logs
    ]