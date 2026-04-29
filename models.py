from sqlalchemy import Table, Column, Integer, String, Text, DateTime, MetaData
from datetime import datetime

metadata = MetaData()

users = Table("users", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
)

user_skills = Table("user_skills", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, nullable=False),
    Column("skill_name", String, nullable=False),
)

courses = Table("courses", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String, nullable=False),
    Column("description", Text, nullable=False),
    Column("embedding", Text, nullable=True),
)

recommendation_logs = Table("recommendation_logs", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, nullable=True),
    Column("input_skills", Text),
    Column("recommended_courses", Text),
    Column("created_at", DateTime, default=datetime.utcnow),
)

def create_tables(engine):
    metadata.create_all(engine)