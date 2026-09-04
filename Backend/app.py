import json
import os
from typing import List

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError

load_dotenv()  # reads the .env file and loads it into os.environ

# ---------------------------
# Schemas
# ---------------------------

class StudentProfile(BaseModel):
    courses_taken: List[str]
    interests: List[str]
    career_path: str


class ElectiveRecommendation(BaseModel):
    elective_name: str
    reason: str
    fit_score: int = Field(ge=1, le=10)


class RecommendationResponse(BaseModel):
    recommendations: List[ElectiveRecommendation]


# ---------------------------
# App setup
# ---------------------------

app = FastAPI(title="Elective Advisor API")

# Allow the frontend (served from a different origin/port) to call this API.
# For local dev this is fine wide-open; tighten allow_origins before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"  # auto-routes to whichever free model is currently available


# ---------------------------
# Core logic
# ---------------------------

def build_prompt(profile: StudentProfile) -> str:
    return f"""
You are an academic advisor. Based on the student profile below, recommend exactly 3 elective subjects.

Student profile:
- Courses taken: {profile.courses_taken}
- Interests: {profile.interests}
- Career path: {profile.career_path}

Respond ONLY with valid JSON matching this exact schema, no extra text, no markdown fences:
{{
  "recommendations": [
    {{"elective_name": "string", "reason": "string", "fit_score": integer 1-10}},
    {{"elective_name": "string", "reason": "string", "fit_score": integer 1-10}},
    {{"elective_name": "string", "reason": "string", "fit_score": integer 1-10}}
  ]
}}
"""


def get_recommendations(profile: StudentProfile) -> RecommendationResponse:
    prompt = build_prompt(profile)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
    }

    resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    result = resp.json()

    # Defensive checks so we get a clear error instead of a cryptic AttributeError
    if "error" in result:
        raise ValueError(f"OpenRouter returned an error: {result['error']}")

    choices = result.get("choices")
    if not choices:
        raise ValueError(f"OpenRouter returned no choices. Full response: {result}")

    message_content = choices[0].get("message", {}).get("content")
    if not message_content:
        raise ValueError(f"OpenRouter returned empty content. Full response: {result}")

    raw_text = message_content.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        data = json.loads(raw_text)
        return RecommendationResponse(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"LLM returned invalid schema: {e}\nRaw output: {raw_text}")


# ---------------------------
# API route
# ---------------------------

@app.post("/recommend", response_model=RecommendationResponse)
def recommend(profile: StudentProfile):
    try:
        return get_recommendations(profile)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"OpenRouter API error: {e}")


@app.get("/health")
def health():
    return {"status": "ok"}