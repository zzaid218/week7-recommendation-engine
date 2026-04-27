from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
import json
from sqlalchemy import DateTime
from datetime import datetime

class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    input_skills = Column(Text)
    recommended_courses = Column(Text)  # stored as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    skills = relationship("UserSkill", back_populates="user")

class UserSkill(Base):
    __tablename__ = "user_skills"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_name = Column(String, nullable=False)
    user = relationship("User", back_populates="skills")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    embedding = Column(Text, nullable=True)  # stored as JSON string

    def get_embedding(self):
        return json.loads(self.embedding) if self.embedding else None

    def set_embedding(self, vec):
        self.embedding = json.dumps(vec)