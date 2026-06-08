import os
from fastapi import HTTPException
from openai import AzureOpenAI
from app.models import FarmInput
from app.prompts import SYSTEM_PROMPT


def get_client():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview").strip()

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
Farmer details:
Location: {data.location}
Farming goal: {data.farming_goal}
Farm size: {data.farm_size}
Main challenge: {data.challenge}

Create a practical farming plan with:

1. Farmer Profile Summary
2. Best Farming Recommendation
3. Crop Suitability
4. Step-by-Step Action Plan
5. Required Resources
6. Risks and Warnings
7. Water and Climate Strategy
8. Cost-Saving Tips
9. Beginner-Friendly Explanation

Use simple language.
Be practical.
Do not give vague advice.
"""


def extract_text(response) -> str:
    message = response.choices[0].message

    if isinstance(message.content, str):
        return message.content

    if isinstance(message.content, list):
        parts = []
        for item in message.content:
            if isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            elif hasattr(item, "text"):
                parts.append(item.text)
        return "\n".join(parts)

    return str(message.content)


def generate_farm_analysis(data: FarmInput) -> str:
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()

    if not deployment:
        raise HTTPException(status_code=500, detail="AZURE_OPENAI_DEPLOYMENT is missing.")

    client = get_client()

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(data)}
            ],
            max_completion_tokens=1500
        )

        ai_text = extract_text(response).strip()

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
