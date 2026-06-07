from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


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


@app.get("/")
def home():
    return {
        "message": "Welcome to AgriAgent AI",
        "docs": "/docs",
        "status": "API is running successfully"
    }


@app.post("/analyze")
def analyze_farm(data: FarmInput):
    location = data.location.strip()
    farming_goal = data.farming_goal.strip()
    farm_size = data.farm_size.strip()
    challenge = data.challenge.strip()

    recommendations = []

    challenge_lower = challenge.lower()
    goal_lower = farming_goal.lower()
    location_lower = location.lower()

    if "water" in challenge_lower or "drought" in challenge_lower:
        recommendations.append("Use drip irrigation, mulching, and water storage tanks to reduce water loss.")
        recommendations.append("Plant during cooler periods and avoid watering during midday heat.")

    if "tomato" in goal_lower or "tomatoes" in goal_lower:
        recommendations.append("Use tomato varieties that handle heat well and prepare raised beds with compost.")
        recommendations.append("Stake tomatoes early and monitor for pests like aphids, whiteflies, and tomato leaf miner.")

    if "maize" in goal_lower or "corn" in goal_lower:
        recommendations.append("Choose drought-tolerant maize seed and plant after reliable rainfall starts.")
        recommendations.append("Apply fertilizer in stages instead of all at once to reduce waste.")

    if "vegetable" in goal_lower or "vegetables" in goal_lower:
        recommendations.append("Start with fast-growing vegetables like spinach, cabbage, onions, and tomatoes.")
        recommendations.append("Use crop rotation to reduce diseases and improve soil health.")

    if "limpopo" in location_lower:
        recommendations.append("For Limpopo, prioritize heat-tolerant crops, water-saving systems, and soil moisture protection.")

    if "1 hectare" in farm_size.lower() or "one hectare" in farm_size.lower():
        recommendations.append("Divide the 1 hectare into sections: production area, nursery area, compost area, and water storage area.")

    recommendations.append("Do soil testing before planting to understand pH, nutrients, and fertilizer needs.")
    recommendations.append("Keep records of expenses, rainfall, planting dates, sales, and crop performance.")
    recommendations.append("Start small, test what works, then scale after your first successful harvest.")

    return {
        "location": location,
        "farming_goal": farming_goal,
        "farm_size": farm_size,
        "challenge": challenge,
        "recommendations": recommendations,
        "next_steps": [
            "Create a simple planting calendar.",
            "Estimate startup costs.",
            "Find local buyers before harvesting.",
            "Track every farming activity weekly."
        ],
        "status": "Farm analysis completed successfully"
    }
