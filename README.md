# Week 7: Skills Utilization Platform & Course Recommendation Engine

## Overview
An AI-powered backend system that recommends relevant courses based on user skills using semantic embeddings and cosine similarity.

## Tech Stack
- **FastAPI** — API framework
- **PostgreSQL** — Database
- **SQLAlchemy** — ORM
- **Sentence Transformers** — `all-MiniLM-L6-v2` embedding model
- **Cosine Similarity** — Ranking algorithm
- **Uvicorn** — ASGI server

## Project Structure
week7/
├── main.py            # FastAPI app and all endpoints
├── models.py          # SQLAlchemy database models
├── database.py        # Database connection setup
├── embeddings.py      # Embedding generation and similarity logic
├── seed.py            # Sample data population
├── requirements.txt   # Project dependencies
└── README.md

## How It Works
1. User skills are converted to vector embeddings using Sentence Transformers
2. Multiple skill embeddings are averaged into a single user profile vector
3. Course descriptions are pre-embedded and stored in the database
4. Cosine similarity is computed between the user vector and all course vectors
5. Courses are ranked by similarity score and top N are returned
6. All recommendations are logged to the database

## Database Schema
| Table | Columns |
|-------|---------|
| `users` | id, name |
| `user_skills` | id, user_id, skill_name |
| `courses` | id, title, description, embedding |
| `recommendation_logs` | id, user_id, input_skills, recommended_courses, created_at |

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/zzaid218/week7-recommendation-engine.git
cd week7-recommendation-engine
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL
```bash
sudo -u postgres psql
ALTER USER postgres PASSWORD 'postgres123';
\q
sudo -u postgres createdb skills_db
```

### 5. Update database.py
```python
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/skills_db"
```

### 6. Seed the database
```bash
python seed.py
```

### 7. Run the server
```bash
uvicorn main:app --reload
```

### 8. Open Swagger UI
http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List all users |
| POST | `/api/users` | Add a new user with skills |
| GET | `/api/courses` | List all courses |
| POST | `/api/recommend` | Recommend by skills text |
| POST | `/api/recommend/by-user` | Recommend by user ID |
| GET | `/api/logs` | View recommendation logs |

## Example Inputs & Outputs

### Recommend by skills text
**Input:**
```json
{
  "skills_text": "Python, machine learning, SQL",
  "top_n": 3
}
```
**Output:**
```json
{
  "extracted_skills": ["Python", "machine learning", "SQL"],
  "recommended_courses": [
    "Machine Learning Fundamentals",
    "Python for Data Science",
    "SQL and Database Design"
  ],
  "top_recommendations": [
    {"id": 2, "title": "Machine Learning Fundamentals", "similarity_score": 0.89},
    {"id": 1, "title": "Python for Data Science", "similarity_score": 0.85},
    {"id": 5, "title": "SQL and Database Design", "similarity_score": 0.81}
  ],
  "explanation": "Courses ranked by cosine similarity to your skill embeddings."
}
```

### Recommend by user ID
**Input:**
```json
{
  "user_id": 1,
  "top_n": 3
}
```
**Output:**
```json
{
  "user_id": 1,
  "user": "Alice",
  "extracted_skills": ["Python", "data analysis", "statistics"],
  "recommended_courses": [
    "Python for Data Science",
    "Statistics for Data Science",
    "Machine Learning Fundamentals"
  ],
  "explanation": "Top 3 courses matched to Alice's skills using semantic similarity."
}
```

### Add a new user
**Input:**
```json
{
  "name": "Sara",
  "skills": ["Docker", "AWS", "Linux"]
}
```
**Output:**
```json
{
  "id": 4,
  "name": "Sara",
  "skills": ["Docker", "AWS", "Linux"]
}
```

## Sample Users (Seeded)
| ID | Name | Skills |
|----|------|--------|
| 1 | Alice | Python, data analysis, statistics |
| 2 | Bob | JavaScript, React, HTML, CSS |
| 3 | Charlie | SQL, database design, PostgreSQL |

## Sample Courses (Seeded)
- Python for Data Science
- Machine Learning Fundamentals
- Deep Learning with PyTorch
- Web Development with FastAPI
- SQL and Database Design
- Natural Language Processing
- React and Frontend Development
- Docker and DevOps Basics
- Statistics for Data Science
- Cloud Computing with AWS
