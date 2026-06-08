import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI


# --------------------------------------------------
# Load Azure OpenAI values from GitHub Codespaces Secrets
# --------------------------------------------------
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")


# --------------------------------------------------
# Create FastAPI app
# --------------------------------------------------
app = FastAPI(
    title="AgriAgent AI",
    description="AI-powered farming guidance API for rural and aspiring farmers",
    version="1.0.0"
)


# --------------------------------------------------
# Allow frontend apps, Swagger UI, and future web apps
# to communicate with this API
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Input model: the user only needs to answer 4 simple questions
# --------------------------------------------------
class FarmInput(BaseModel):
    location: str
    farming_goal: str
    farm_size: str
    challenge: str


# --------------------------------------------------
# Create Azure OpenAI client
# --------------------------------------------------
def get_azure_client():
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Azure OpenAI endpoint or API key is missing."
        )

    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )


# --------------------------------------------------
# Build expert prompt from simple farmer inputs
# --------------------------------------------------
def build_prompt(data: FarmInput) -> str:
    return f"""
You are AgriAgent AI, an expert agricultural reasoning assistant.

Your mission:
Help rural, beginner, and aspiring farmers make practical farming decisions.
The user does not understand AI prompting, so you must turn their simple answers
into a professional farming plan.

Farmer details:
- Location: {data.location}
- Farming goal: {data.farming_goal}
- Farm size: {data.farm_size}
- Main challenge: {data.challenge}

Return a clear farming plan with these sections:

1. Farmer Profile Summary
2. Best Farming Recommendation
3. Crop Suitability
4. Step-by-Step Action Plan
5. Required Resources
6. Risks and Warnings
7. Water and Climate Strategy
8. Cost-Saving Tips
9. Beginner-Friendly Explanation

Use simple language.
Be practical.
Avoid unnecessary theory.
Focus on what the farmer should do next.
"""


# --------------------------------------------------
# Home route
# --------------------------------------------------
@app.get("/")
def home():
    return {
        "message": "Welcome to AgriAgent AI",
        "docs": "/docs",
        "status": "API is running successfully"
    }


# --------------------------------------------------
# Health check route
# --------------------------------------------------
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "azure_endpoint_loaded": bool(AZURE_OPENAI_ENDPOINT),
        "azure_key_loaded": bool(AZURE_OPENAI_API_KEY),
        "deployment_loaded": bool(AZURE_OPENAI_DEPLOYMENT),
        "api_version": AZURE_OPENAI_API_VERSION
    }


# --------------------------------------------------
# Main AI farming analysis endpoint
# --------------------------------------------------
@app.post("/analyze")
def analyze_farm(data: FarmInput):
    if not AZURE_OPENAI_DEPLOYMENT:
        raise HTTPException(
            status_code=500,
            detail="AZURE_OPENAI_DEPLOYMENT is missing."
        )

    client = get_azure_client()
    prompt = build_prompt(data)

    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {
                    "role": "system",
                    "content": "You are AgriAgent AI, a practical farming advisor for rural and beginner farmers."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=1200
        )

        ai_plan = response.choices[0].message.content

        return {
            "farmer_profile": {
                "location": data.location,
                "farming_goal": data.farming_goal,
                "farm_size": data.farm_size,
                "challenge": data.challenge
            },
            "ai_farming_plan": ai_plan,
            "model_used": AZURE_OPENAI_DEPLOYMENT,
            "status": "AI farm analysis completed successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Azure OpenAI request failed: {str(e)}"
        )
