from database import engine
from models import users, user_skills, courses, recommendation_logs
from datetime import datetime
import json

def get_all_courses(conn):
    return conn.execute(courses.select()).fetchall()

def get_user_by_id(conn, user_id: int):
    return conn.execute(users.select().where(users.c.id == user_id)).fetchone()

def get_user_skills(conn, user_id: int):
    rows = conn.execute(
        user_skills.select().where(user_skills.c.user_id == user_id)
    ).fetchall()
    return [row.skill_name for row in rows]

def get_all_users(conn):
    return conn.execute(users.select()).fetchall()

def create_user(conn, name: str, skills: list[str]):
    result = conn.execute(users.insert().values(name=name))
    user_id = result.inserted_primary_key[0]
    for skill in skills:
        conn.execute(user_skills.insert().values(user_id=user_id, skill_name=skill))
    conn.commit()
    return user_id

def save_log(conn, user_id, skills: list[str], ranked: list[dict]):
    conn.execute(recommendation_logs.insert().values(
        user_id=user_id,
        input_skills=json.dumps(skills),
        recommended_courses=json.dumps([c["title"] for c in ranked]),
        created_at=datetime.utcnow()
    ))
    conn.commit()

def get_all_logs(conn):
    return conn.execute(
        recommendation_logs.select().order_by(recommendation_logs.c.created_at.desc())
    ).fetchall()