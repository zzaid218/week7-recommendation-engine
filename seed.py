from database import SessionLocal, engine
from models import Base, User, UserSkill, Course
from embeddings import embed_text

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
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(Course).count() > 0:
        print("Already seeded.")
        db.close()
        return
    print("Seeding courses...")
    for title, desc in COURSES:
        c = Course(title=title, description=desc)
        c.set_embedding(embed_text(f"{title}. {desc}"))
        db.add(c)
    print("Seeding users...")
    for name, skills in USERS:
        u = User(name=name)
        db.add(u)
        db.flush()
        for s in skills:
            db.add(UserSkill(user_id=u.id, skill_name=s))
    db.commit()
    db.close()
    print("Done.")

if __name__ == "__main__":
    seed()