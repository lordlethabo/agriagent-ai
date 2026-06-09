import os
from fastapi import HTTPException
from openai import AzureOpenAI

from app.models import FarmInput
from app.agents import (
    planner_agent,
    water_agent,
    crop_agent,
    risk_agent,
    coordinator_agent
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


def run_all_agents(data: FarmInput):
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()

    if not deployment:
        raise HTTPException(status_code=500, detail="AZURE_OPENAI_DEPLOYMENT is missing.")

    client = get_client()
    farmer_data = build_farmer_data(data)

    # Fast multi-agent mode:
    # 4 specialist agents + 1 coordinator agent
    agent_results = {
        "planner_agent": planner_agent(client, deployment, farmer_data),
        "water_agent": water_agent(client, deployment, farmer_data),
        "crop_agent": crop_agent(client, deployment, farmer_data),
        "risk_agent": risk_agent(client, deployment, farmer_data),
    }

    final_strategy = coordinator_agent(
        client,
        deployment,
        farmer_data,
        agent_results
    )

    return {
        "agent_results": agent_results,
        "final_strategy": final_strategy
    }


def generate_farm_analysis(data: FarmInput):
    results = run_all_agents(data)
    return results["final_strategy"]
