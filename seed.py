from database import engine
from models import metadata, users, user_skills, courses, create_tables
from embeddings import embed_text
import json

COURSES = [
    ("Python for Data Science", "Learn Python for data analysis using pandas, numpy, and matplotlib."),
    ("Machine Learning Fundamentals", "Supervised and unsupervised learning, regression, classification, clustering."),
    ("Deep Learning with PyTorch", "Neural networks, CNNs, RNNs, and model training using PyTorch."),
    ("Web Development with FastAPI", "Build REST APIs with FastAPI, SQLAlchemy, and Python."),
    ("SQL and Database Design", "Relational databases, SQL queries, normalization, and database design."),
    ("Natural Language Processing", "Text preprocessing, embeddings, transformers, and NLP pipelines."),
    ("React and Frontend Development", "Build modern UIs with React, hooks, and component architecture."),
    ("Docker and DevOps Basics", "Containerization, CI/CD pipelines, and deployment fundamentals."),
    ("Statistics for Data Science", "Probability, hypothesis testing, distributions, and statistical inference."),
    ("Cloud Computing with AWS", "EC2, S3, Lambda, and building scalable cloud architectures."),
]

USERS = [
    ("Alice", ["Python", "data analysis", "statistics"]),
    ("Bob", ["JavaScript", "React", "HTML", "CSS"]),
    ("Charlie", ["SQL", "database design", "PostgreSQL"]),
]

def seed():
    create_tables(engine)
    with engine.connect() as conn:
        # Check if already seeded
        result = conn.execute(courses.select()).fetchall()
        if result:
            print("Already seeded.")
            return

        print("Seeding courses...")
        for title, desc in COURSES:
            embedding = json.dumps(embed_text(f"{title}. {desc}"))
            conn.execute(courses.insert().values(
                title=title, description=desc, embedding=embedding
            ))

        print("Seeding users...")
        for name, skills in USERS:
            result = conn.execute(users.insert().values(name=name))
            user_id = result.inserted_primary_key[0]
            for skill in skills:
                conn.execute(user_skills.insert().values(
                    user_id=user_id, skill_name=skill
                ))

        conn.commit()
    print("Done.")

if __name__ == "__main__":
    seed()