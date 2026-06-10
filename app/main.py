import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import FarmInput
from app.agent import generate_farm_analysis, run_all_agents


app = FastAPI(
    title="AgriAgent Global",
    description="Multi-agent climate and food security intelligence platform",
    version="3.0.0"
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
        "message": "Welcome to AgriAgent Global",
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
    result = generate_farm_analysis(data)

    return {
        "farmer_profile": {
            "location": data.location,
            "farming_goal": data.farming_goal,
            "farm_size": data.farm_size,
            "challenge": data.challenge
        },
        **result,
        "model_used": os.getenv("AZURE_OPENAI_DEPLOYMENT")
    }


@app.post("/multi-agent-analysis")
def multi_agent_analysis(data: FarmInput):
    result = run_all_agents(data)

    return {
        "farmer_profile": {
            "location": data.location,
            "farming_goal": data.farming_goal,
            "farm_size": data.farm_size,
            "challenge": data.challenge
        },
        **result,
        "model_used": os.getenv("AZURE_OPENAI_DEPLOYMENT")
    }
