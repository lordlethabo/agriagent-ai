from openai import AzureOpenAI


def planner_agent(client, deployment, farmer_data):

    response = client.responses.create(
        model=deployment,
        input=f"""
        You are Planner Agent.

        Farmer Data:
        {farmer_data}

        Return:
        - Farm layout
        - Production strategy
        - Scaling strategy

        Maximum 5 bullet points.
        """
    )

    return response.output_text


def climate_agent(client, deployment, farmer_data):

    response = client.responses.create(
        model=deployment,
        input=f"""
        You are Climate Agent.

        Farmer Data:
        {farmer_data}

        Analyze:
        - Climate risks
        - Rainfall
        - Temperature
        - Drought

        Maximum 5 bullet points.
        """
    )

    return response.output_text


def water_agent(client, deployment, farmer_data):

    response = client.responses.create(
        model=deployment,
        input=f"""
        You are Water Agent.

        Farmer Data:
        {farmer_data}

        Recommend:
        - Irrigation
        - Water storage
        - Water conservation

        Maximum 5 bullet points.
        """
    )

    return response.output_text
