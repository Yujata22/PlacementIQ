from __future__ import annotations

import json
import re
from typing import Any

import requests

from backend.agents.tools import (
    get_assignment_explanation,
    get_container_details,
    get_critical_inventory,
    get_network_summary,
)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "deepseek-r1:8b"


def ask_llm(prompt: str) -> str:
    """Send a prompt to the locally running Ollama model."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            },
            timeout=180,
        )

        response.raise_for_status()
        payload = response.json()

        return payload.get(
            "response",
            "The model returned an empty response.",
        )

    except requests.exceptions.ConnectionError:
        return (
            "Could not connect to Ollama. "
            "Start it with `ollama serve`."
        )

    except requests.exceptions.Timeout:
        return (
            "The local model took too long to respond. "
            "Try again or use a smaller Ollama model."
        )

    except requests.exceptions.RequestException as exc:
        return f"Ollama request failed: {exc}"


def extract_container_id(question: str) -> str | None:
    """Extract IDs such as CONT001 or CONT_1001 from a question."""

    match = re.search(
        r"\bCONT_?\d+\b",
        question.upper(),
    )

    return match.group(0) if match else None


def route_question(question: str) -> str:
    """Determine which PlacementIQ tool should answer the question."""

    normalized_question = question.lower()

    assignment_terms = [
        "why was",
        "why is",
        "assigned",
        "assignment",
        "recommended",
        "recommendation",
    ]

    container_terms = [
        "container details",
        "inside container",
        "container contains",
        "what is in",
        "which skus",
    ]

    risk_terms = [
        "critical",
        "lowest coverage",
        "most at risk",
        "inventory risk",
        "shortage",
        "days of cover",
        "days-of-cover",
    ]

    summary_terms = [
        "summary",
        "summarize",
        "network overview",
        "network status",
        "current network",
    ]

    if any(term in normalized_question for term in assignment_terms):
        return "assignment_explanation"

    if any(term in normalized_question for term in container_terms):
        return "container_details"

    if any(term in normalized_question for term in risk_terms):
        return "critical_inventory"

    if any(term in normalized_question for term in summary_terms):
        return "network_summary"

    return "network_summary"


def build_grounded_prompt(
    question: str,
    intent: str,
    tool_result: Any,
) -> str:
    """Build a prompt grounded only in PlacementIQ tool output."""

    serialized_result = json.dumps(
        tool_result,
        indent=2,
        default=str,
    )

    return f"""
You are PlacementIQ, an AI-powered supply chain planning copilot.

User Question:
{question}

Selected Intent:
{intent}

PlacementIQ Tool Output:
{serialized_result}

Instructions:
- Answer only using the supplied tool output.
- Do not invent containers, FCs, costs, SKUs, or metrics.
- Explain risks, tradeoffs, and planning implications.
- Be concise and decision-oriented.
- If data is missing, clearly state what is missing.
"""


def answer_planning_question(
    question: str,
    containers: list[dict[str, Any]],
    fulfillment_centers: list[dict[str, Any]],
    inventory_coverage: list[dict[str, Any]],
    container_skus: list[dict[str, Any]],
    optimization_result: dict[str, Any],
) -> dict[str, Any]:
    """Route a planning question and explain the result."""

    intent = route_question(question)
    container_id = extract_container_id(question)

    if intent == "critical_inventory":

        tool_result = get_critical_inventory(
            inventory_coverage=inventory_coverage,
            threshold_days=7,
        )

    elif intent == "container_details":

        if container_id is None:
            return {
                "intent": intent,
                "answer": (
                    "Please provide a container ID "
                    "(example: CONT001)."
                ),
                "tool_result": None,
            }

        tool_result = get_container_details(
            container_id=container_id,
            containers=containers,
            container_skus=container_skus,
        )

    elif intent == "assignment_explanation":

        if container_id is None:
            return {
                "intent": intent,
                "answer": (
                    "Please provide a container ID "
                    "(example: CONT001)."
                ),
                "tool_result": None,
            }

        tool_result = get_assignment_explanation(
            container_id=container_id,
            optimization_result=optimization_result,
        )

    else:

        tool_result = get_network_summary(
            containers=containers,
            fulfillment_centers=fulfillment_centers,
            inventory_coverage=inventory_coverage,
        )

    prompt = build_grounded_prompt(
        question=question,
        intent=intent,
        tool_result=tool_result,
    )

    answer = ask_llm(prompt)

    return {
        "intent": intent,
        "answer": answer,
        "tool_result": tool_result,
    }