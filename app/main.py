import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

app = FastAPI(
    title="AgriAgent AI",
    description="AI-powered farming guidance API for rural and aspiring farmers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FarmInput(BaseModel):
    location: str
    farming_goal: str
    farm_size: str
    challenge: str


client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
)


def build_prompt(data: FarmInput):
    return f"""
You are AgriAgent AI, an expert farming reasoning assistant for rural and beginner farmers.

The user does not know how to write AI prompts. They only gave four simple inputs.

Farmer profile:
Location: {data.location}
Farming goal: {data.farming_goal}
Farm size: {data.farm_size}
Main challenge: {data.challenge}

Create a practical farming plan.

Return the answer with these sections:
1. Farmer profile summary
2. Best recommendation
3. Reasoning
4. Risks
5. Resources needed
6. Step-by-step action plan
7. Cost-saving tips

Use simple language. Be practical. Avoid complicated theory.
"""


@app.get("/")
def home():
    return {
        "message": "Welcome to AgriAgent AI",
        "docs": "/docs",
        "status": "API is running successfully"
    }


@app.post("/analyze")
def analyze_farm(data: FarmInput):
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not deployment_name:
        return {
            "error": "AZURE_OPENAI_DEPLOYMENT is missing in .env"
        }

    prompt = build_prompt(data)

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful agricultural AI agent for rural and beginner farmers."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4,
        max_tokens=1000
    )

    return {
        "farmer_profile": {
            "location": data.location,
            "farming_goal": data.farming_goal,
            "farm_size": data.farm_size,
            "challenge": data.challenge
        },
        "ai_farming_plan": response.choices[0].message.content,
        "status": "AI farm analysis completed successfully"
    }
