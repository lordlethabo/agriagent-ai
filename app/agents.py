# ==========================================
# AgriAgent Global - Specialist Agents
# ==========================================


def safe_output(response):
    """
    Safely extract visible text from Azure OpenAI Responses API.
    """

    if getattr(response, "output_text", None):
        return response.output_text.strip()

    try:
        outputs = []

        for item in response.output:

            if hasattr(item, "content"):

                for content in item.content:

                    if hasattr(content, "text"):
                        outputs.append(content.text)

                    elif isinstance(content, dict):

                        if content.get("text"):
                            outputs.append(content["text"])

        if outputs:
            return "\n".join(outputs).strip()

    except Exception:
        pass

    return "Agent completed but returned no visible text."


def call_agent(
    client,
    deployment,
    agent_name,
    farmer_data,
    task
):
    """
    Generic specialist agent function.
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
- Return exactly 3 bullet points.
- Maximum 20 words per bullet.
- Do not explain reasoning.
- Return only the final answer.
- Focus on practical action.
- Focus on food security, climate resilience, water sustainability, and income generation.
""",
        max_output_tokens=1200,
        text={
            "verbosity": "low"
        }
    )

    return safe_output(response)


# ==========================================
# Planner Agent
# ==========================================
def planner_agent(
    client,
    deployment,
    farmer_data
):
    return call_agent(
        client,
        deployment,
        "Planner Agent",
        farmer_data,
        """
Create:
- Farm layout
- Production strategy
- Scaling strategy
"""
    )


# ==========================================
# Water Agent
# ==========================================
def water_agent(
    client,
    deployment,
    farmer_data
):
    return call_agent(
        client,
        deployment,
        "Water Agent",
        farmer_data,
        """
Recommend:
- Irrigation strategy
- Water storage
- Water conservation
"""
    )


# ==========================================
# Risk Agent
# ==========================================
def risk_agent(
    client,
    deployment,
    farmer_data
):
    return call_agent(
        client,
        deployment,
        "Risk Agent",
        farmer_data,
        """
Identify:
- Climate risks
- Pest risks
- Financial risks
- Market risks

Provide mitigation actions.
"""
    )


# ==========================================
# Global Impact Agent
# ==========================================
def global_impact_agent(
    client,
    deployment,
    farmer_data
):

    response = client.responses.create(
        model=deployment,
        input=f"""
You are Global Impact Agent.

Farmer Data:
{farmer_data}

Return:

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
- Keep responses concise.
- One sentence explanation per score.
- Focus on measurable impact.
- Do not explain reasoning.
""",
        max_output_tokens=1500,
        text={
            "verbosity": "low"
        }
    )

    return safe_output(response)
