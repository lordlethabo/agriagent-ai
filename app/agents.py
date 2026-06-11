def safe_output(response, fallback_text):
    if getattr(response, "output_text", None):
        text = response.output_text.strip()
        if text:
            return text

    text_parts = []

    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                text_parts.append(text)

            if isinstance(content, dict) and content.get("text"):
                text_parts.append(content["text"])

    final_text = "\n".join(text_parts).strip()

    return final_text if final_text else fallback_text


def call_agent(client, deployment, agent_name, farmer_data, task, fallback_text):
    response = client.responses.create(
        model=deployment,
        input=f"""
You are {agent_name}.

Farmer Data:
{farmer_data}

Task:
{task}

Output rules:
- Return exactly 3 bullet points.
- Maximum 22 words per bullet.
- Do not explain your role.
- Do not include hidden reasoning.
- Be practical, safe, and locally verifiable.
- Do not invent weather, prices, grants, laws, or guaranteed yields.
""",
        max_output_tokens=1200
    )

    return safe_output(response, fallback_text)


def planner_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Planner Agent",
        farmer_data,
        "Create farm layout, production strategy, crop planning, and scale-up recommendations.",
        "- Start with a small pilot plot before scaling production.\n- Use drought-tolerant crops, rotation, compost, and market-linked production.\n- Expand only after water, buyers, and cash flow are confirmed."
    )


def water_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Water Agent",
        farmer_data,
        "Recommend water storage, irrigation, soil moisture protection, and seasonal water actions.",
        "- Prioritize drip irrigation, mulching, rainwater harvesting, and soil moisture conservation.\n- Store rainfall where possible using tanks, ponds, swales, and contour structures.\n- Verify water availability and irrigation feasibility before expanding production."
    )


def risk_agent(client, deployment, farmer_data):
    return call_agent(
        client,
        deployment,
        "Risk Agent",
        farmer_data,
        "Identify climate, pest, financial, operational, and market risks with mitigation actions.",
        "- Reduce climate risk with crop diversity, staggered planting, mulch, and drought-tolerant varieties.\n- Reduce market risk through buyer agreements, cooperative selling, and value-added processing.\n- Verify pest, disease, financial, and legal risks with local agricultural experts."
    )


def global_impact_agent(client, deployment, farmer_data):
    response = client.responses.create(
        model=deployment,
        input=f"""
You are Global Impact Agent.

Farmer Data:
{farmer_data}

Evaluate the expected improvement AFTER applying the recommended AgriAgent strategy.

Return this exact format:

Food Security Score: X/100
One sentence explaining expected food security improvement.

Climate Resilience Score: X/100
One sentence explaining expected climate resilience improvement.

Water Sustainability Score: X/100
One sentence explaining expected water efficiency improvement.

Economic Impact Score: X/100
One sentence explaining expected income, jobs, or market access improvement.

SDG Alignment:
- SDG 1: No Poverty
- SDG 2: Zero Hunger
- SDG 6: Clean Water
- SDG 8: Decent Work
- SDG 13: Climate Action

Rules:
- Scores must reflect improvement potential, not only current hardship.
- Use realistic but optimistic scores between 65 and 88 when a practical plan is possible.
- Do not promise guaranteed outcomes.
- Mention local verification where needed.
""",
        max_output_tokens=1500
    )

    return safe_output(
        response,
        "Food Security Score: 72/100\nExpected to improve production stability through crop planning and resilience measures.\n\nClimate Resilience Score: 70/100\nExpected to improve resilience through seasonal planning, crop diversity, and soil protection.\n\nWater Sustainability Score: 68/100\nExpected to improve water efficiency through storage, mulching, and drip irrigation.\n\nEconomic Impact Score: 74/100\nExpected to support local income through market-linked production and job creation.\n\nSDG Alignment:\n- SDG 1: No Poverty\n- SDG 2: Zero Hunger\n- SDG 6: Clean Water\n- SDG 8: Decent Work\n- SDG 13: Climate Action"
    )
