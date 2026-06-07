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
        "message": "Welcome to AgriAgent AI",
        "status": "API running successfully"
    }

@app.post("/analyze")
def analyze_farm(data: FarmerInput):
    return {
        "farmer_profile": {
            "location": data.location,
            "farming_goal": data.farming_goal,
            "farm_size": data.farm_size,
            "challenge": data.challenge
        },
        "recommendation": {
            "best_option": "Start with a small, water-efficient tomato production plan.",
            "water_strategy": "Use drip irrigation, mulch, and early morning watering to reduce water loss.",
            "risk_level": "Medium",
            "reasoning": "Tomatoes can grow well in Limpopo, but limited water increases the risk. A controlled irrigation plan is important."
        },
        "action_plan": [
            "Test or inspect the soil before planting.",
            "Choose tomato varieties suitable for warm conditions.",
            "Prepare raised beds with compost.",
            "Use mulch to keep soil moisture.",
            "Install simple drip irrigation if possible.",
            "Monitor pests and plant health weekly."
        ],
        "resources_needed": [
            "Tomato seedlings or seeds",
            "Compost or organic fertilizer",
            "Mulch",
            "Basic watering system",
            "Pest monitoring plan"
        ],
        "status": "Structured farming plan generated successfully"
    }
