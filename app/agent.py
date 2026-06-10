import os
import re
from fastapi import HTTPException
from openai import AzureOpenAI

from app.models import FarmInput
from app.weather import get_weather_context
from app.agents import (
    planner_agent,
    water_agent,
    risk_agent,
    global_impact_agent
)


SAFETY_NOTE = (
    "AgriAgent provides AI-assisted farming guidance, not professional agricultural advice. "
    "Farmers should confirm major decisions with local extension officers, agronomists, "
    "water specialists, or agricultural experts where possible."
)


HIGH_RISK_TERMS = [
    "chemical pesticide",
    "pesticide",
    "herbicide",
    "fungicide",
    "poison",
    "toxic",
    "borehole",
    "drilling",
    "loan",
    "debt",
    "large investment",
    "guaranteed profit",
    "guaranteed yield",
    "disease outbreak",
    "livestock disease",
    "crop disease",
    "contamination",
    "fertilizer overdose",
    "water rights",
    "land rights",
]


VAGUE_TERMS = [
    "help",
    "farming",
    "problem",
    "agriculture",
    "business",
    "farm",
    "crops",
]


def get_client():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview").strip()

    if not endpoint:
        raise HTTPException(status_code=500, detail="AZURE_OPENAI_ENDPOINT is missing.")

    if not api_key:
        raise HTTPException(status_code=500, detail="AZURE_OPENAI_API_KEY is missing.")

    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version
    )


def clean_text(value: str) -> str:
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def validate_farm_input(data: FarmInput):
    errors = []

    location = clean_text(data.location)
    goal = clean_text(data.farming_goal)
    farm_size = clean_text(data.farm_size)
    challenge = clean_text(data.challenge)

    required_fields = {
        "location": location,
        "farming_goal": goal,
        "farm_size": farm_size,
        "challenge": challenge,
    }

    for field, value in required_fields.items():
        if not value:
            errors.append(f"{field} is required.")
        elif len(value) < 4:
            errors.append(f"{field} is too short.")

    if goal.lower() in VAGUE_TERMS:
        errors.append("farming_goal is too vague. Provide a specific farming objective.")

    if challenge.lower() in VAGUE_TERMS:
        errors.append("challenge is too vague. Describe the main farming problem clearly.")

    return errors


def detect_risk_level(data: FarmInput):
    combined_text = " ".join([
        clean_text(data.location),
        clean_text(data.farming_goal),
        clean_text(data.farm_size),
        clean_text(data.challenge),
    ]).lower()

    matched_terms = [
        term for term in HIGH_RISK_TERMS
        if term in combined_text
    ]

    if len(matched_terms) >= 3:
        risk_level = "High"
    elif len(matched_terms) >= 1:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "risk_level": risk_level,
        "matched_risk_terms": matched_terms,
        "safety_warning": build_safety_warning(risk_level)
    }


def build_safety_warning(risk_level: str):
    if risk_level == "High":
        return (
            "High-risk farming decisions detected. Confirm chemical, water, financial, "
            "disease, or legal decisions with qualified local experts."
        )

    if risk_level == "Medium":
        return (
            "Some recommendations may involve technical or financial risk. "
            "Verify key decisions with local agricultural experts."
        )

    return "No major high-risk terms detected, but local verification is still recommended."


def calculate_confidence(data: FarmInput, validation_errors: list, risk_info: dict, weather_context: dict):
    confidence = 88

    fields = [
        clean_text(data.location),
        clean_text(data.farming_goal),
        clean_text(data.farm_size),
        clean_text(data.challenge),
    ]

    for field in fields:
        if len(field) < 10:
            confidence -= 6

    if validation_errors:
        confidence -= 20

    if risk_info["risk_level"] == "Medium":
        confidence -= 8

    if risk_info["risk_level"] == "High":
        confidence -= 16

    if weather_context.get("available"):
        confidence += 5
    else:
        confidence -= 7

    return max(45, min(confidence, 93))


def build_assumptions(weather_context: dict):
    assumptions = [
        "Analysis is based on the farmer profile provided by the user.",
        "AI recommendations are advisory estimates, not guaranteed outcomes.",
        "Local soil tests, water access, and market prices may change the recommendation.",
    ]

    if weather_context.get("available"):
        assumptions.append("Weather context is grounded using WeatherAPI data.")
    else:
        assumptions.append("Weather data was unavailable, so the system used general advisory mode.")

    return assumptions


def build_local_verification_steps():
    return [
        "Confirm crop choices with a local agricultural extension officer.",
        "Run a soil test before major fertilizer or soil amendment decisions.",
        "Verify water availability, water quality, and irrigation feasibility locally.",
        "Check current local market prices and buyer demand before planting at scale.",
        "Consult qualified experts before using chemical pesticides, drilling boreholes, or taking loans.",
    ]


def build_farmer_data(data: FarmInput, weather_context: dict) -> str:
    return f"""
Location: {clean_text(data.location)}
Farming Goal: {clean_text(data.farming_goal)}
Farm Size: {clean_text(data.farm_size)}
Main Challenge: {clean_text(data.challenge)}

Weather Context:
{weather_context.get("summary")}

Weather Data Available:
{weather_context.get("available")}

Safety and Grounding Rules:
- Use the weather context when making water and climate recommendations.
- Do not invent exact prices, laws, grants, yields, or guarantees.
- If live data is unavailable, clearly state that local verification is required.
- Avoid chemical, borehole drilling, legal, medical, or financial advice as certainty.
- Recommend local extension officers, soil tests, and market verification for major decisions.
"""


def fallback_response(data: FarmInput = None, weather_context: dict = None):
    risk_info = (
        detect_risk_level(data)
        if data is not None
        else {
            "risk_level": "Medium",
            "matched_risk_terms": [],
            "safety_warning": "Some services are unavailable. Verify all major decisions locally."
        }
    )

    if weather_context is None:
        weather_context = {
            "available": False,
            "summary": "Weather data unavailable."
        }

    return {
        "recommendation": "Use general advisory mode and verify recommendations with local agricultural experts.",
        "confidence": 55,
        "risk_level": risk_info["risk_level"],
        "matched_risk_terms": risk_info["matched_risk_terms"],
        "safety_warning": risk_info["safety_warning"],
        "weather_context": weather_context,
        "assumptions": build_assumptions(weather_context),
        "local_verification_steps": build_local_verification_steps(),
        "agents": [
            {
                "name": "Fallback Agent",
                "status": "warning",
                "finding": "Some AI services or data sources were unavailable."
            }
        ],
        "agent_results": {
            "fallback_agent": "General advisory mode activated because the full agent workflow could not complete."
        },
        "global_challenge_positioning": (
            "AgriAgent Global supports food security, climate resilience, "
            "water sustainability, and rural economic opportunity."
        ),
        "safety_note": SAFETY_NOTE,
        "status": "Fallback advisory mode activated."
    }


def run_all_agents(data: FarmInput):
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()

    if not deployment:
        raise HTTPException(status_code=500, detail="AZURE_OPENAI_DEPLOYMENT is missing.")

    weather_context = get_weather_context(data.location)
    validation_errors = validate_farm_input(data)
    risk_info = detect_risk_level(data)
    confidence = calculate_confidence(data, validation_errors, risk_info, weather_context)

    if validation_errors:
        return {
            "recommendation": "Improve the farm profile inputs before using the AI advisory result.",
            "confidence": confidence,
            "risk_level": risk_info["risk_level"],
            "matched_risk_terms": risk_info["matched_risk_terms"],
            "safety_warning": risk_info["safety_warning"],
            "weather_context": weather_context,
            "validation_errors": validation_errors,
            "assumptions": build_assumptions(weather_context),
            "local_verification_steps": build_local_verification_steps(),
            "agents": [
                {
                    "name": "Input Validation Agent",
                    "status": "warning",
                    "finding": "The farm profile needs clearer information before reliable analysis."
                }
            ],
            "agent_results": {
                "validation_agent": "Input validation failed. Please provide more specific farm information."
            },
            "global_challenge_positioning": (
                "AgriAgent Global supports food security, climate resilience, "
                "water sustainability, and rural economic opportunity."
            ),
            "safety_note": SAFETY_NOTE,
            "status": "Input validation warning."
        }

    try:
        client = get_client()
        farmer_data = build_farmer_data(data, weather_context)

        planner = planner_agent(client, deployment, farmer_data)
        water = water_agent(client, deployment, farmer_data)
        risk = risk_agent(client, deployment, farmer_data)
        impact = global_impact_agent(client, deployment, farmer_data)

        return {
            "recommendation": (
                "Develop a weather-grounded climate-smart farming plan focused on water efficiency, "
                "risk reduction, food security, and local economic opportunity."
            ),
            "confidence": confidence,
            "risk_level": risk_info["risk_level"],
            "matched_risk_terms": risk_info["matched_risk_terms"],
            "safety_warning": risk_info["safety_warning"],
            "weather_context": weather_context,
            "assumptions": build_assumptions(weather_context),
            "local_verification_steps": build_local_verification_steps(),
            "agents": [
                {
                    "name": "Weather Data Agent",
                    "status": "complete" if weather_context.get("available") else "warning",
                    "finding": weather_context.get("summary")
                },
                {
                    "name": "Input Validation Agent",
                    "status": "complete",
                    "finding": "Farm profile contains enough information for advisory analysis."
                },
                {
                    "name": "Safety Agent",
                    "status": "complete",
                    "finding": f"Risk level assessed as {risk_info['risk_level']}."
                },
                {
                    "name": "Planner Agent",
                    "status": "complete",
                    "finding": "Farm strategy and production structure generated."
                },
                {
                    "name": "Water Agent",
                    "status": "complete",
                    "finding": "Weather-grounded water conservation and irrigation actions identified."
                },
                {
                    "name": "Risk Agent",
                    "status": "complete",
                    "finding": "Climate, pest, financial, and market risks assessed."
                },
                {
                    "name": "Global Impact Agent",
                    "status": "complete",
                    "finding": "Food security, climate, water, and economic impact scored."
                },
                {
                    "name": "Coordinator Agent",
                    "status": "complete",
                    "finding": "Specialist outputs combined into a final advisory package."
                }
            ],
            "agent_results": {
                "planner_agent": planner,
                "water_agent": water,
                "risk_agent": risk,
                "global_impact_agent": impact
            },
            "global_challenge_positioning": (
                "AgriAgent Global supports food security, climate resilience, "
                "water sustainability, and rural economic opportunity."
            ),
            "safety_note": SAFETY_NOTE,
            "status": "Weather-grounded global impact multi-agent analysis completed successfully."
        }

    except Exception:
        return fallback_response(data, weather_context)


def generate_farm_analysis(data: FarmInput):
    return run_all_agents(data)
