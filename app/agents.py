# ==========================================
# Fast Specialist Agents for AgriAgent Global
# ==========================================


def safe_output(response):
    if getattr(response, "output_text", None):
        return response.output_text.strip()

    return "No response generated."


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
- Maximum 3 bullet points.
- Maximum 80 words.
- Be direct.
- Be practical.
- No long explanations.
- No repetition.
""",
        max_output_tokens=300
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
        "Identify the top climate, pest, financial, and market risks with mitigation actions."
    )
