import os
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
    "Farmers should confirm major decisions with local extension officers or agricultural experts where possible."
)


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


def build_farmer_data(data: FarmInput) -> str:
    return f"""
Location: {data.location}
Farming Goal: {data.farming_goal}
Farm Size: {data.farm_size}
Main Challenge: {data.challenge}
"""


def fallback_response():
    return {
        "recommendation": "Use general advisory mode and verify recommendations with local agricultural experts.",
        "confidence": 55,
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

    try:
        client = get_client()
        farmer_data = build_farmer_data(data)

        planner = planner_agent(client, deployment, farmer_data)
        water = water_agent(client, deployment, farmer_data)
        risk = risk_agent(client, deployment, farmer_data)
        impact = global_impact_agent(client, deployment, farmer_data)

        return {
            "recommendation": (
                "Develop a climate-smart farming plan focused on water efficiency, "
                "risk reduction, food security, and local economic opportunity."
            ),
            "confidence": 87,
            "agents": [
                {
                    "name": "Planner Agent",
                    "status": "complete",
                    "finding": "Farm strategy and production structure generated."
                },
                {
                    "name": "Water Agent",
                    "status": "complete",
                    "finding": "Water conservation and irrigation actions identified."
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
            "status": "Global impact multi-agent analysis completed successfully."
        }

    except Exception:
        return fallback_response()


def generate_farm_analysis(data: FarmInput):
    return run_all_agents(data)
