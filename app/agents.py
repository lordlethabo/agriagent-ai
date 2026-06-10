def safe_output(response):
    if getattr(response, "output_text", None):
        return response.output_text.strip()

    text_parts = []

    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                text_parts.append(text)

    if text_parts:
        return "\n".join(text_parts).strip()

    return "Agent completed but returned no visible text."


def call_agent(client, deployment, agent_name, farmer_data, task):
    response = client.responses.create(
        model=deployment,
        input=f"""
You are {agent_name}.

Farmer Data:
{farmer_data}

Task:
{task}

Rules:
- Return exactly 3 bullet points.
- Maximum 20 words per bullet.
- Return only the final answer.
- Be practical.
- Focus on food security, climate resilience, water sustainability, and income.
""",
        max_output_tokens=1200,
        text={"verbosity": "low"}
    )

    return safe_output(response)


def planner_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Planner Agent",
        farmer_data,
        "Create farm layout, production strategy, and scaling plan."
    )


def water_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Water Agent",
        farmer_data,
        "Recommend irrigation, storage, and water conservation actions."
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

Return this exact format:

Food Security Score: X/100
Climate Resilience Score: X/100
Water Sustainability Score: X/100
Economic Impact Score: X/100

SDG Alignment:
- SDG 1: No Poverty
- SDG 2: Zero Hunger
- SDG 6: Clean Water
- SDG 8: Decent Work
- SDG 13: Climate Action

Rules:
- One sentence explanation per score.
- Keep it concise.
- Return only final answer.
""",
        max_output_tokens=1500,
        text={"verbosity": "low"}
    )

    return safe_output(response)
