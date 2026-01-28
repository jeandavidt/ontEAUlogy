#!/usr/bin/env python3
"""
OpenRouter Model Availability Checker

Usage: python check_openrouter_models.py <api_key>
"""

import sys
import json
import requests
from typing import Dict, List, Any


def get_available_models(api_key: str) -> List[Dict[str, Any]]:
    """Fetch available models from OpenRouter API"""
    url = "https://openrouter.ai/api/v1/models"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data.get("data", [])

    except requests.exceptions.RequestException as e:
        print(f"Error fetching models: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {e}")
        return []


def format_model_info(models: List[Dict[str, Any]]) -> str:
    """Format model information for display"""
    if not models:
        return "No models available or API key invalid"

    output = []
    output.append(f"Found {len(models)} available models:\n")

    for model in models:
        name = model.get("id", "Unknown")
        description = model.get("name", "No description")
        pricing = model.get("pricing", {})

        output.append(f"📱 {name}")
        output.append(f"   Description: {description}")

        if pricing:
            prompt_price = pricing.get("prompt", "N/A")
            completion_price = pricing.get("completion", "N/A")
            output.append(
                f"   Pricing: ${prompt_price}/1K tokens (prompt), ${completion_price}/1K tokens (completion)"
            )

        context_length = model.get("context_length", "N/A")
        if context_length != "N/A":
            output.append(f"   Context length: {context_length} tokens")

        output.append("")

    return "\n".join(output)


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_openrouter_models.py <api_key>")
        print("Example: python check_openrouter_models.py sk-or-v1-...")
        sys.exit(1)

    api_key = sys.argv[1]

    print("🔍 Checking OpenRouter model availability...")
    print(
        f"Using API key: {api_key[:12]}..."
        if len(api_key) > 12
        else "Using provided API key"
    )
    print()

    models = get_available_models(api_key)

    if models:
        print(format_model_info(models))
    else:
        print(
            "❌ Failed to retrieve models. Please check your API key and internet connection."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
