# ==========================================
# Specialist Agents for AgriAgent Global
# ==========================================


def safe_output(response):
    """
    Safely extracts text from Azure OpenAI Responses API.
    """
    if getattr(response, "output_text", None):
        return response.output_text.strip()

    return "No response generated."


def call_agent(client, deployment, agent_name, farmer_data, task):
    """
    Generic function used by all specialist agents.
    """
    response = client.responses.create(
        model=deployment,
        input=f"""
You are {agent_name}.

Farmer Data:
{farmer_data}

Task:
{task}

Rules:
- Maximum 5 bullet points.
- Maximum 120 words.
- Be practical.
- Avoid vague advice.
- Do not repeat other agents.
"""
    )

    return safe_output(response)


def planner_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Planner Agent",
        farmer_data,
        "Create the farm layout, production strategy, and scaling plan."
    )


def climate_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Climate Agent",
        farmer_data,
        "Analyze drought, heat, rainfall uncertainty, and climate risks."
    )


def water_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Water Agent",
        farmer_data,
        "Recommend irrigation, water storage, and water conservation methods."
    )


def crop_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Crop Agent",
        farmer_data,
        "Recommend suitable crops, crop rotation, and planting strategy."
    )


def finance_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Finance Agent",
        farmer_data,
        "Estimate startup priorities, cost-saving ideas, funding options, and ROI targets."
    )


def market_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Market Agent",
        farmer_data,
        "Recommend buyer types, market access strategy, pricing approach, and value-add options."
    )


def risk_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Risk Agent",
        farmer_data,
        "Identify climate, pest, financial, market, and operational risks with mitigation actions."
    )


def food_security_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Food Security Impact Agent",
        farmer_data,
        "Explain how this plan improves food security, income, climate resilience, and sustainability."
    )


def coordinator_agent(client, deployment, farmer_data, agent_results):
    """
    Combines all specialist agent outputs into one final strategy.
    """
    response = client.responses.create(
        model=deployment,
        input=f"""
You are the Coordinator Agent.

Farmer Data:
{farmer_data}

Specialist Agent Results:
{agent_results}

Create the final practical farming strategy.

Return:

1. Final Recommended Strategy
2. 30-Day Action Plan
3. 90-Day Action Plan
4. Key Metrics To Track

Rules:
- Maximum 5 bullet points per section.
- Be practical.
- Avoid repetition.
- Focus on action.
"""
    )

    return safe_output(response)
