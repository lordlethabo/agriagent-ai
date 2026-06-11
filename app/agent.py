import os
import re
from fastapi import HTTPException
from openai import AzureOpenAI

from app.models import FarmInput
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


def infer_season_context(location: str) -> dict:
    location_lower = clean_text(location).lower()

    southern_keywords = [
        "south africa", "limpopo", "gauteng", "pretoria", "johannesburg",
        "botswana", "zimbabwe", "namibia", "mozambique",
        "australia", "new zealand", "argentina", "chile", "brazil"
    ]

    tropical_keywords = [
        "kenya", "nigeria", "ghana", "uganda", "tanzania", "ethiopia",
        "india", "indonesia", "philippines", "thailand", "malaysia", "colombia"
    ]

    if any(keyword in location_lower for keyword in southern_keywords):
        return {
            "hemisphere": "Southern Hemisphere",
            "current_season_estimate": "winter / dry-season period around June",
            "seasonal_guidance": (
                "Prioritize water storage, drought resilience, soil moisture conservation, "
                "off-season planning, irrigation readiness, and preparation for summer rainfall planting."
            )
        }

    if any(keyword in location_lower for keyword in tropical_keywords):
        return {
            "hemisphere": "Tropical or equatorial region",
            "current_season_estimate": "local wet and dry seasons vary by region",
            "seasonal_guidance": (
                "Verify local rainy season timing, prioritize drainage during wet periods, "
                "and use staggered planting to reduce rainfall uncertainty."
            )
        }

    return {
        "hemisphere": "Northern Hemisphere or unspecified region",
        "current_season_estimate": "summer / growing-season period around June",
        "seasonal_guidance": (
            "Assess heat stress, irrigation demand, pest pressure, and crop water needs. "
            "Use local planting calendars before acting."
        )
    }


def validate_farm_input(data: FarmInput):
    errors = []

    fields = {
        "location": clean_text(data.location),
        "farming_goal": clean_text(data.farming_goal),
        "farm_size": clean_text(data.farm_size),
        "challenge": clean_text(data.challenge),
    }

    for field, value in fields.items():
        if not value:
            errors.append(f"{field} is required.")
        elif len(value) < 4:
            errors.append(f"{field} is too short.")

    if fields["farming_goal"].lower() in VAGUE_TERMS:
        errors.append("farming_goal is too vague. Provide a specific farming objective.")

    if fields["challenge"].lower() in VAGUE_TERMS:
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


def calculate_confidence(data: FarmInput, validation_errors: list, risk_info: dict):
    confidence = 86

    fields = [
        clean_text(data.location),
        clean_text(data.farming_goal),
        clean_text(data.farm_size),
        clean_text(data.challenge),
    ]

    for field in fields:
        if len(field) < 10:
            confidence -= 5

    if validation_errors:
        confidence -= 20

    if risk_info["risk_level"] == "Medium":
        confidence -= 6

    if risk_info["risk_level"] == "High":
        confidence -= 14

    confidence -= 4

    return max(45, min(confidence, 90))


def build_assumptions(season_context: dict):
    return [
        "Analysis is based on the farmer profile provided by the user.",
        "Seasonal guidance is inferred from location and general regional climate patterns.",
        f"Estimated seasonal context: {season_context['current_season_estimate']}.",
        "No live weather, soil, satellite, or market-pricing data is currently connected.",
        "AI recommendations are advisory estimates, not guaranteed outcomes.",
        "Local soil tests, water access, planting calendars, and market prices may change the recommendation.",
    ]


def build_local_verification_steps():
    return [
        "Confirm crop choices with a local agricultural extension officer.",
        "Check the local planting calendar for the exact season and rainfall window.",
        "Run a soil test before major fertilizer or soil amendment decisions.",
        "Verify water availability, water quality, and irrigation feasibility locally.",
        "Check current local market prices and buyer demand before planting at scale.",
        "Consult qualified experts before chemical pesticide use, borehole drilling, or large loans.",
    ]


def build_farmer_data(data: FarmInput, season_context: dict) -> str:
    return f"""
Location: {clean_text(data.location)}
Farming Goal: {clean_text(data.farming_goal)}
Farm Size: {clean_text(data.farm_size)}
Main Challenge: {clean_text(data.challenge)}

Season and Location Context:
Hemisphere / Region: {season_context["hemisphere"]}
Estimated Season: {season_context["current_season_estimate"]}
Seasonal Guidance: {season_context["seasonal_guidance"]}

Safety and Grounding Rules:
- Use the season and location context when making climate, water, crop, and risk recommendations.
- Do not invent exact weather, prices, laws, grants, yields, or guarantees.
- If exact local data is unavailable, say local verification is required.
- Avoid chemical, borehole drilling, legal, medical, or financial advice as certainty.
- Recommend local extension officers, soil tests, planting calendars, and market verification for major decisions.
"""


def run_all_agents(data: FarmInput):
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()

    if not deployment:
        raise HTTPException(status_code=500, detail="AZURE_OPENAI_DEPLOYMENT is missing.")

    season_context = infer_season_context(data.location)
    validation_errors = validate_farm_input(data)
    risk_info = detect_risk_level(data)
    confidence = calculate_confidence(data, validation_errors, risk_info)

    if validation_errors:
        return {
            "recommendation": "Improve the farm profile inputs before using the AI advisory result.",
            "confidence": confidence,
            "risk_level": risk_info["risk_level"],
            "matched_risk_terms": risk_info["matched_risk_terms"],
            "safety_warning": risk_info["safety_warning"],
            "season_context": season_context,
            "validation_errors": validation_errors,
            "assumptions": build_assumptions(season_context),
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
            "safety_note": SAFETY_NOTE,
            "status": "Input validation warning."
        }

    try:
        client = get_client()
        farmer_data = build_farmer_data(data, season_context)

        planner = planner_agent(client, deployment, farmer_data)
        water = water_agent(client, deployment, farmer_data)
        risk = risk_agent(client, deployment, farmer_data)
        impact = global_impact_agent(client, deployment, farmer_data)

        return {
            "recommendation": (
                "Develop a season-aware climate-smart farming plan focused on water efficiency, "
                "risk reduction, food security, and local economic opportunity."
            ),
            "confidence": confidence,
            "risk_level": risk_info["risk_level"],
            "matched_risk_terms": risk_info["matched_risk_terms"],
            "safety_warning": risk_info["safety_warning"],
            "season_context": season_context,
            "assumptions": build_assumptions(season_context),
            "local_verification_steps": build_local_verification_steps(),
            "agents": [
                {
                    "name": "Season and Location Agent",
                    "status": "complete",
                    "finding": (
                        f"{season_context['hemisphere']} detected. "
                        f"{season_context['current_season_estimate']}."
                    )
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
                    "finding": "Season-aware water conservation and irrigation actions identified."
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
            "status": "Season-aware global impact multi-agent analysis completed successfully."
        }

    except Exception:
        return {
            "recommendation": "Use general advisory mode and verify recommendations with local agricultural experts.",
            "confidence": 55,
            "risk_level": risk_info["risk_level"],
            "matched_risk_terms": risk_info["matched_risk_terms"],
            "safety_warning": risk_info["safety_warning"],
            "season_context": season_context,
            "assumptions": build_assumptions(season_context),
            "local_verification_steps": build_local_verification_steps(),
            "agents": [
                {
                    "name": "Fallback Agent",
                    "status": "warning",
                    "finding": "Some AI services were unavailable, so general advisory mode was used."
                }
            ],
            "agent_results": {
                "fallback_agent": "General advisory mode activated because the full agent workflow could not complete."
            },
            "safety_note": SAFETY_NOTE,
            "status": "Fallback advisory mode activated."
        }


def generate_farm_analysis(data: FarmInput):
    return run_all_agents(data)
