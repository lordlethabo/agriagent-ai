import os
from fastapi import HTTPException
from openai import AzureOpenAI

from app.models import FarmInput
from app.prompts import SYSTEM_PROMPT


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


def build_user_prompt(data: FarmInput) -> str:
    return f"""
{SYSTEM_PROMPT}

Farmer Profile:
- Location: {data.location}
- Farming Goal: {data.farming_goal}
- Farm Size: {data.farm_size}
- Main Challenge: {data.challenge}

Create a complete multi-agent farming plan.

STRICT OUTPUT RULES:
- Complete every section.
- Maximum 5 bullet points per section.
- Maximum 120 words per section.
- No long essays.
- Avoid repeating the same advice.
- Be practical and specific.

Sections required:
1. Executive Summary
2. Planner Agent Analysis
3. Climate Agent Analysis
4. Water Agent Analysis
5. Crop Agent Analysis
6. Finance Agent Analysis
7. Market Agent Analysis
8. Risk Agent Analysis
9. Food Security Impact Analysis
10. Final Recommended Farming Strategy
11. 30-Day Action Plan
12. 90-Day Action Plan
13. Key Metrics To Track
"""


def extract_response_text(response) -> str:
    if getattr(response, "output_text", None):
        return response.output_text.strip()

    text_parts = []

    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                text_parts.append(text)
            elif isinstance(content, dict) and content.get("text"):
                text_parts.append(content["text"])

    return "\n".join(text_parts).strip()


def generate_farm_analysis(data: FarmInput) -> str:
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()

    if not deployment:
        raise HTTPException(status_code=500, detail="AZURE_OPENAI_DEPLOYMENT is missing.")

    client = get_client()

    try:
        response = client.responses.create(
            model=deployment,
            input=build_user_prompt(data),
            max_output_tokens=4000
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
