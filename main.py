from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
from database import engine, get_db
from models import Base, User, UserSkill, Course, RecommendationLog
from embeddings import embed_skills, rank_courses
from seed import seed

Base.metadata.create_all(bind=engine)
seed()

app = FastAPI(title="Skills & Course Recommendation Engine")

# --- Schemas ---
class RecommendByUser(BaseModel):
    user_id: int
    top_n: int = 3

class RecommendByText(BaseModel):
    skills_text: str   # e.g. "Python, machine learning, SQL"
    top_n: int = 3

class AddUser(BaseModel):
    name: str
    skills: list[str]

# --- Routes ---
@app.get("/")
def root():
    return {"message": "API is running"}

@app.post("/api/recommend")
def recommend_by_text(req: RecommendByText, db: Session = Depends(get_db)):
    skills = [s.strip() for s in req.skills_text.replace(",", " ").split() if s.strip()]
    if not skills:
        raise HTTPException(400, "No skills provided.")
    
    courses = db.query(Course).all()
    user_vec = embed_skills(skills)
    ranked = rank_courses(user_vec, courses)[:req.top_n]

    # ✅ ADD HERE — before return
    log = RecommendationLog(
        user_id=None,
        input_skills=json.dumps(skills),
        recommended_courses=json.dumps([c["title"] for c in ranked])
    )
    db.add(log)
    db.commit()

    return {
        "extracted_skills": skills,
        "recommended_courses": [c["title"] for c in ranked],
        "top_recommendations": ranked,
        "explanation": "Courses ranked by cosine similarity to your skill embeddings."
    }

@app.post("/api/recommend/by-user")
def recommend_by_user(req: RecommendByUser, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(404, "User not found.")
    
    skills = [us.skill_name for us in user.skills]
    
    if not skills:
        return {
            "user_id": req.user_id,
            "user": user.name,
            "extracted_skills": [],
            "recommended_courses": [],
            "explanation": "No skills found for this user."
        }
    
    courses = db.query(Course).all()
    
    if not courses:
        return {
            "user_id": req.user_id,
            "user": user.name,
            "extracted_skills": skills,
            "recommended_courses": [],
            "explanation": "No courses available."
        }

    user_vec = embed_skills(skills)
    ranked = rank_courses(user_vec, courses)[:req.top_n]

    # ✅ ADD HERE — before return
    log = RecommendationLog(
        user_id=req.user_id,
        input_skills=json.dumps(skills),
        recommended_courses=json.dumps([c["title"] for c in ranked])
    )
    db.add(log)
    db.commit()

    return {
        "user_id": req.user_id,
        "user": user.name,
        "extracted_skills": skills,
        "recommended_courses": [c["title"] for c in ranked],
        "top_recommendations": ranked,
        "explanation": f"Top {req.top_n} courses matched to {user.name}'s skills using semantic similarity."
    }

@app.post("/api/users")
def add_user(req: AddUser, db: Session = Depends(get_db)):
    u = User(name=req.name)
    db.add(u)
    db.flush()
    for s in req.skills:
        db.add(UserSkill(user_id=u.id, skill_name=s))
    db.commit()
    return {"id": u.id, "name": u.name, "skills": req.skills}

@app.get("/api/users")
def list_users(db: Session = Depends(get_db)):
    return [{"id": u.id, "name": u.name, "skills": [s.skill_name for s in u.skills]}
            for u in db.query(User).all()]

@app.get("/api/courses")
def list_courses(db: Session = Depends(get_db)):
    return [{"id": c.id, "title": c.title, "description": c.description}
            for c in db.query(Course).all()]

@app.get("/api/logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(RecommendationLog).order_by(RecommendationLog.created_at.desc()).all()
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