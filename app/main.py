from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import FarmInput
from app.agent import generate_farm_analysis
import os


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


@app.get("/")
def home():
    return {
        "message": "Welcome to AgriAgent AI",
        "docs": "/docs",
        "status": "API is running successfully"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "endpoint_loaded": bool(os.getenv("AZURE_OPENAI_ENDPOINT")),
        "api_key_loaded": bool(os.getenv("AZURE_OPENAI_API_KEY")),
        "deployment_loaded": bool(os.getenv("AZURE_OPENAI_DEPLOYMENT")),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION")
    }


@app.post("/analyze")
def analyze_farm(data: FarmInput):
    ai_plan = generate_farm_analysis(data)

    return {
        "farmer_profile": {
            "location": data.location,
            "farming_goal": data.farming_goal,
            "farm_size": data.farm_size,
            "challenge": data.challenge
        },
        "ai_farming_plan": ai_plan,
        "model_used": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        "status": "AI farm analysis completed successfully"
    }
