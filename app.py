
import re
from datetime import datetime

from flask import Flask, jsonify, request, render_template

from database import (
    get_summary,
    get_top_products,
    get_monthly_revenue,
    get_region_revenue,
)

from llm import interpret_question


app = Flask(__name__)


# -------------------- Homepage --------------------

@app.route("/")
def home():
    return render_template("index.html")


# -------------------- API Health Check --------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "InsightIQ API is running"
    })


# -------------------- Dashboard APIs --------------------

@app.route("/api/summary", methods=["GET"])
def summary():
    return jsonify(get_summary())


@app.route("/api/top-products", methods=["GET"])
def top_products():
    return jsonify(get_top_products())


@app.route("/api/monthly-revenue", methods=["GET"])
def monthly_revenue():
    return jsonify(get_monthly_revenue())


@app.route("/api/region-revenue", methods=["GET"])
def region_revenue():
    return jsonify(get_region_revenue())


# -------------------- Natural Language Q&A --------------------

@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Please provide a valid JSON request."
        }), 400

    question = data.get("question", "")

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "error": "Please enter a valid question."
        }), 400

    question = question.strip()

    if len(question) > 500:
        return jsonify({
            "error": "Please keep your question under 500 characters."
        }), 400

    # Ask the local LLM to classify the question.
    interpretation = interpret_question(question)
    intent = interpretation.get("intent")

    if intent == "error":
        return jsonify({
            "question": question,
            "answer": (
                "The local AI interpreter is unavailable. "
                "Please check that Ollama is running and try again."
            )
        }), 503

    # Only allow supported intents.
    allowed_intents = {
        "total_revenue",
        "top_product",
        "monthly_trend",
        "top_region",
        "compare_months",
        "unsupported",
    }

    if intent not in allowed_intents:
        return jsonify({
            "question": question,
            "answer": "I couldn't interpret that question reliably."
        }), 200

    # 1. Compare revenue between two months.
    if intent == "compare_months":
        month_pattern = (
            r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|"
            r"apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
            r"aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|"
            r"nov(?:ember)?|dec(?:ember)?)\s+\d{4}\b"
        )

        months = re.findall(month_pattern, question.lower())

        if len(months) != 2:
            return jsonify({
                "question": question,
                "answer": (
                    "Please specify two months and years, for example: "
                    "How did revenue change between January 2026 "
                    "and May 2026?"
                )
            }), 200

        parsed_months = []

        for month in months:
            parsed = None

            for fmt in ("%B %Y", "%b %Y"):
                try:
                    parsed = datetime.strptime(
                        month.title(), fmt
                    ).strftime("%Y-%m")
                    break
                except ValueError:
                    continue

            if parsed is None:
                return jsonify({
                    "question": question,
                    "answer": "I couldn't understand the month format."
                }), 200

            parsed_months.append(parsed)

        first_month, second_month = parsed_months

        if first_month == second_month:
            return jsonify({
                "question": question,
                "answer": "Please choose two different months."
            }), 200

        monthly_data = {
            row["month"]: row["revenue"]
            for row in get_monthly_revenue()
        }

        if (
            first_month not in monthly_data
            or second_month not in monthly_data
        ):
            return jsonify({
                "question": question,
                "answer": (
                    "Revenue data is unavailable for one or both months."
                )
            }), 200

        first_revenue = monthly_data[first_month]
        second_revenue = monthly_data[second_month]
        change = second_revenue - first_revenue

        if first_revenue != 0:
            percentage_text = (
                f" ({change / first_revenue * 100:+.2f}%)"
            )
        else:
            percentage_text = ""

        if change > 0:
            direction = "increased"
        elif change < 0:
            direction = "decreased"
        else:
            direction = "did not change"

        answer = (
            f"Revenue {direction} by ₹{abs(change):,.2f}"
            f"{percentage_text} from {first_month} "
            f"(₹{first_revenue:,.2f}) to {second_month} "
            f"(₹{second_revenue:,.2f})."
        )

        return jsonify({
            "question": question,
            "answer": answer,
            "data": {
                "first_month": first_month,
                "first_revenue": first_revenue,
                "second_month": second_month,
                "second_revenue": second_revenue,
                "change": round(change, 2),
            }
        })

    # 2. Total revenue.
    if intent == "total_revenue":
        result = get_summary()

        answer = (
            f"Total revenue is ₹{result['total_revenue']:,.2f} "
            f"across {result['total_transactions']} completed transactions."
        )
        return jsonify({
            "question": question,
            "answer": answer,
            "data": result,
        })

    # 3. Product with the highest revenue.
    if intent == "top_product":
        results = get_top_products()

        if not results:
            answer = "No product revenue data is available."
        else:
            top = results[0]
            answer = (
                f"{top['Product']} generated the highest revenue "
                f"at ₹{top['revenue']:,.2f}."
            )

        return jsonify({
            "question": question,
            "answer": answer,
            "data": results,
        })

    # 4. Monthly revenue trend.
    if intent == "monthly_trend":
        results = get_monthly_revenue()

        if not results:
            answer = "No monthly revenue data is available."
        else:
            highest = max(results, key=lambda row: row["revenue"])
            lowest = min(results, key=lambda row: row["revenue"])

            answer = (
                f"{highest['month']} had the highest monthly revenue "
                f"at ₹{highest['revenue']:,.2f}. "
                f"{lowest['month']} had the lowest at "
                f"₹{lowest['revenue']:,.2f}."
            )

        return jsonify({
            "question": question,
            "answer": answer,
            "data": results,
        })

    # 5. Region with the highest sales.
    if intent == "top_region":
        results = get_region_revenue()

        if not results:
            answer = "No regional revenue data is available."
        else:
            top = results[0]
            answer = (
                f"{top['Region']} generated the highest sales revenue "
                f"at ₹{top['revenue']:,.2f}."
            )

        return jsonify({
            "question": question,
            "answer": answer,
            "data": results,
        })

    # 6. Unsupported questions.
    return jsonify({
        "question": question,
        "answer": (
            "I can answer questions about total revenue, the top product, "
            "monthly revenue trends, the leading sales region, and revenue "
            "changes between two months."
        )
    }), 200


# -------------------- Run Application --------------------

if __name__ == "__main__":
    app.run(debug=True)
