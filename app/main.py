from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="AgriAgent AI",
    description="AI-powered farming guidance API for rural and aspiring farmers",
    version="1.0.0"
)

# CORS
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
    risks = []
    resources_needed = []

    challenge_lower = challenge.lower()
    goal_lower = farming_goal.lower()
    location_lower = location.lower()

    # Water challenges
    if "water" in challenge_lower or "drought" in challenge_lower:
        recommendations.append(
            "Use drip irrigation, mulching, and rainwater harvesting."
        )
        recommendations.append(
            "Water early morning or late afternoon to reduce evaporation."
        )
        risks.append(
            "Insufficient water may reduce crop yields."
        )

    # Tomatoes
    if "tomato" in goal_lower:
        recommendations.append(
            "Use heat-tolerant tomato varieties."
        )
        recommendations.append(
            "Prepare raised beds with compost-rich soil."
        )

        resources_needed.extend([
            "Tomato seedlings",
            "Compost",
            "Mulch",
            "Drip irrigation kit",
            "Pest control supplies"
        ])

    # Maize
    elif "maize" in goal_lower or "corn" in goal_lower:
        recommendations.append(
            "Use drought-resistant maize seed."
        )
        recommendations.append(
            "Plant after reliable rainfall."
        )

        resources_needed.extend([
            "Maize seed",
            "Fertilizer",
            "Basic irrigation system"
        ])

    # General vegetables
    elif "vegetable" in goal_lower:
        recommendations.append(
            "Start with spinach, onions, cabbage, and tomatoes."
        )

        resources_needed.extend([
            "Vegetable seeds",
            "Compost",
            "Water storage tank"
        ])

    # Limpopo specific
    if "limpopo" in location_lower:
        recommendations.append(
            "Focus on heat-tolerant crops and water conservation."
        )

    # Farm size guidance
    if "1 hectare" in farm_size.lower():
        recommendations.append(
            "Divide land into production, nursery, compost, and water-storage zones."
        )

    action_plan = [
        "Conduct a soil assessment.",
        "Prepare land and irrigation.",
        "Purchase inputs.",
        "Plant crops.",
        "Monitor weekly.",
        "Record costs and yields.",
        "Identify buyers before harvest."
    ]

    return {
        "farmer_profile": {
            "location": location,
            "farming_goal": farming_goal,
            "farm_size": farm_size,
            "challenge": challenge
        },
        "recommendations": recommendations,
        "risks": risks,
        "resources_needed": resources_needed,
        "action_plan": action_plan,
        "status": "Farm analysis completed successfully"
    }
