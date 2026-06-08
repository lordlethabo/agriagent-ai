import os
from fastapi import HTTPException
from openai import AzureOpenAI

from app.models import FarmInput
from app.prompts import SYSTEM_PROMPT


# ==========================================
# Create Azure OpenAI Client
# ==========================================
def get_client():

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    api_version = os.getenv(
        "AZURE_OPENAI_API_VERSION",
        "2025-04-01-preview"
    ).strip()

    if not endpoint:
        raise HTTPException(
            status_code=500,
            detail="AZURE_OPENAI_ENDPOINT is missing."
        )

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="AZURE_OPENAI_API_KEY is missing."
        )

    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version
    )


# ==========================================
# Build Farmer Prompt
# ==========================================
def build_user_prompt(data: FarmInput) -> str:

    return f"""
{SYSTEM_PROMPT}

Farmer Profile

Location:
{data.location}

Farming Goal:
{data.farming_goal}

Farm Size:
{data.farm_size}

Main Challenge:
{data.challenge}

Create a detailed AI farming plan.

Include:

1. Farmer Profile Summary

2. Recommended Farming Strategy

3. Best Crops To Grow

4. Climate Suitability

5. Water Management Strategy

6. Pest And Disease Prevention

7. Equipment Needed

8. Estimated Startup Resources

9. Step-by-Step Action Plan

10. Risks And Mitigation

11. Cost Saving Tips

12. Long-Term Growth Strategy

13. Beginner-Friendly Explanation

Keep recommendations practical.

Focus on South African farming conditions.

Use simple language.
"""


# ==========================================
# Extract Text From GPT-5 Response
# ==========================================
def extract_response_text(response):

    if hasattr(response, "output_text"):
        if response.output_text:
            return response.output_text

    text_parts = []

    if hasattr(response, "output"):

        for item in response.output:

            if hasattr(item, "content"):

                for content in item.content:

                    if hasattr(content, "text"):
                        text_parts.append(content.text)

                    elif isinstance(content, dict):
                        if "text" in content:
                            text_parts.append(content["text"])

    return "\n".join(text_parts).strip()


# ==========================================
# Generate AI Farming Plan
# ==========================================
def generate_farm_analysis(data: FarmInput):

    deployment = os.getenv(
        "AZURE_OPENAI_DEPLOYMENT",
        ""
    ).strip()

    if not deployment:
        raise HTTPException(
            status_code=500,
            detail="AZURE_OPENAI_DEPLOYMENT is missing."
        )

    client = get_client()

    try:

        response = client.responses.create(
            model=deployment,
            input=build_user_prompt(data),
            max_output_tokens=2000
        )

        ai_text = extract_response_text(response)

        if not ai_text:

            raise HTTPException(
                status_code=500,
                detail="Azure OpenAI returned an empty response."
            )

        return ai_text

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Azure OpenAI request failed: {str(e)}"
        )
