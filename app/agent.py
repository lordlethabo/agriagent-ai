def generate_farm_analysis(data: FarmInput):

    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()

    client = get_client()
    farmer_data = build_farmer_data(data)

    planner = planner_agent(client, deployment, farmer_data)
    water = water_agent(client, deployment, farmer_data)
    risk = risk_agent(client, deployment, farmer_data)

    return f"""
PLANNER AGENT

{planner}

================================

WATER AGENT

{water}

================================

RISK AGENT

{risk}
"""
