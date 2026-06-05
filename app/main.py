from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="AgriAgent AI",
    description="AI-powered farming assistant",
    version="1.0.0"
)

class FarmerInput(BaseModel):
    location: str
    farming_goal: str
    farm_size: str
    challenge: str

@app.get("/")
def home():
    return {
        "message": "Welcome to AgriAgent AI"
    }

@app.post("/analyze")
def analyze_farm(data: FarmerInput):

    return {
        "location": data.location,
        "farming_goal": data.farming_goal,
        "farm_size": data.farm_size,
        "challenge": data.challenge,
        "status": "Analysis received successfully"
    }
