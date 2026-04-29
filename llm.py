from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_skills_with_llm(text: str) -> list[str]:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a skill extraction assistant. Extract technical skills from the given text and return ONLY a comma-separated list. No explanation, no bullets, no extra text. Example: Python, machine learning, SQL"
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0
    )
    raw = response.choices[0].message.content.strip()
    skills = [s.strip() for s in raw.split(",") if s.strip()]
    return skills

def explain_recommendation(user_skills: list[str], course_title: str, course_description: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a course recommendation assistant. Given a user's skills and a course, explain in 1-2 sentences why this course is a good match for them. Be specific and concise."
            },
            {
                "role": "user",
                "content": f"User skills: {', '.join(user_skills)}\nCourse: {course_title}\nDescription: {course_description}"
            }
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()