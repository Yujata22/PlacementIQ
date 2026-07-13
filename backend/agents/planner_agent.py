import requests


OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_llm(prompt: str) -> str:

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "deepseek-r1:8b",
            "prompt": prompt,
            "stream": False,
        },
    )

    return response.json()["response"]

from backend.agents.tools import (
    get_network_summary,
)

def answer_network_summary():

    containers = [
        {
            "container_id": "CONT001",
            "total_units": 5000,
        },
        {
            "container_id": "CONT002",
            "total_units": 7000,
        },
    ]

    fulfillment_centers = [
        {
            "fc_code": "FC_SOCAL",
        },
        {
            "fc_code": "FC_DALLAS",
        },
    ]

    inventory_coverage = [
        {
            "fc_code": "FC_DALLAS",
            "days_of_cover": 5,
        }
    ]

    summary = get_network_summary(
        containers,
        fulfillment_centers,
        inventory_coverage,
    )

    prompt = f"""
You are PlacementIQ.

You are a supply chain planning copilot.

Explain this network summary:

{summary}

Focus on:
1. Network size
2. Inventory risks
3. Operational recommendations
"""

    return ask_llm(prompt)