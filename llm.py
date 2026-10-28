
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:3b"

ALLOWED_INTENTS = {
    "total_revenue",
    "top_product",
    "monthly_trend",
    "top_region",
    "compare_months",
    "unsupported",
}


def interpret_question(question):
    """Interpret a sales question without generating SQL."""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Classify the user's question about a sales database. "
                    "Return a JSON object containing only the intent field. "
                    "Allowed intents: total_revenue, top_product, "
                    "monthly_trend, top_region, compare_months, unsupported. "
                    "Use total_revenue for total sales or revenue questions. "
                    "Use top_product for the product with the highest revenue. "
                    "Use monthly_trend for monthly revenue trends or "
                    "highest/lowest revenue month questions. "
                    "Use top_region for regional sales comparisons. "
                    "Use compare_months for revenue changes between two months. "
                    "For unrelated or unsupported questions, use unsupported. "
                    "Never generate SQL."
                ),
            },
            {"role": "user", "content": question},
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()

        result = response.json()
        parsed = json.loads(result["message"]["content"])

        if parsed.get("intent") not in ALLOWED_INTENTS:
            return {"intent": "unsupported"}

        return {"intent": parsed["intent"]}

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
    ) as error:
        print("LLM interpretation error:", repr(error))
        return {"intent": "error"}
