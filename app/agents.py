# ==========================================
# AgriAgent Global - Specialist Agents
# ==========================================


def safe_output(response):
    """Safely extract text from Azure OpenAI Responses API."""
    if getattr(response, "output_text", None):
        return response.output_text.strip()

    return "No response generated."


def call_agent(client, deployment, agent_name, farmer_data, task, max_tokens=300):
    """Reusable function for specialist agents."""
    response = client.responses.create(
        model=deployment,
        input=f"""
You are {agent_name}.

Farmer Data:
{farmer_data}

Task:
{task}

Rules:
- Maximum 3 bullet points.
- Maximum 80 words.
- Be direct.
- Be practical.
- Focus on food security, climate resilience, water scarcity, and income.
- Avoid repetition.
""",
        max_output_tokens=max_tokens
    )

    return safe_output(response)


def planner_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Planner Agent",
        farmer_data,
        "Create a short farm layout, production strategy, and scaling plan."
    )


def water_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Water Agent",
        farmer_data,
        "Recommend water-saving irrigation, storage, and conservation actions."
    )


def risk_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Risk Agent",
        farmer_data,
        "Identify climate, pest, financial, market, and operational risks with mitigation actions."
    )


def global_impact_agent(client, deployment, farmer_data):
    response = client.responses.create(
        model=deployment,
        input=f"""
You are Global Impact Agent.

Farmer Data:
{farmer_data}

Return exactly this format:

Food Security Score: /100
Climate Resilience Score: /100
Water Sustainability Score: /100
Economic Impact Score: /100

SDG Alignment:
- SDG 1: No Poverty
- SDG 2: Zero Hunger
- SDG 6: Clean Water
- SDG 8: Decent Work
- SDG 13: Climate Action

Rules:
- Explain each score in 1 short sentence.
- Keep it concise.
- Focus on global challenge impact.
""",
        max_output_tokens=400
    )

    return safe_output(response)
