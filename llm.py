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