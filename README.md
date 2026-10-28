# InsightIQ — AI Sales Intelligence Assistant

InsightIQ is an AI-powered sales analytics application that enables users to explore sales data by asking questions in natural language. Instead of writing SQL queries or manually analyzing spreadsheets, users can ask business questions and receive answers generated from actual sales database queries.

The application combines a Flask backend, SQLite database, local Large Language Model (LLM), and an interactive web dashboard to make sales analysis easier and more accessible.

## Features

- **Natural Language Question Answering:** Ask questions about sales data using everyday English.
- **Total Revenue Analysis:** Calculate total revenue across completed transactions.
- **Top-Performing Product:** Identify the product generating the highest revenue.
- **Monthly Revenue Trends:** Analyze revenue across different months and identify the highest- and lowest-revenue months.
- **Regional Sales Analysis:** Compare revenue across regions and identify the leading region.
- **Month-to-Month Comparison:** Calculate the revenue difference and percentage change between two specified months.
- **Interactive Dashboard:** View key performance indicators, monthly trends, regional comparisons, and product rankings.
- **Local AI Integration:** Use Qwen 2.5 3B through Ollama to interpret questions without requiring a paid LLM API.
- **Data Validation:** Reject invalid records and handle missing values during data preparation.
- **Input Validation:** Handle empty questions, excessively long inputs, invalid month comparisons, and unsupported questions.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Backend | Python, Flask |
| Database | SQLite |
| Data Processing | Pandas |
| AI / LLM | Qwen 2.5 3B |
| Local LLM Runtime | Ollama |
| HTTP Requests | Requests |
| Testing | Python, Requests, Flask test client or API tests |

## System Architecture

```text
                 User
                   |
                   v
        Interactive Web Dashboard
          HTML, CSS, JavaScript
                   |
                   v
             Flask Backend
                   |
          +--------+---------+
          |                  |
          v                  v
   Local LLM via Ollama   Intent-Based Routing
   Qwen 2.5 3B            in Flask
          |                  |
          v                  v
   Question Intent       Validated Query
   Classification        and Business Logic
                             |
                             v
                       SQLite Database
                             |
                             v
                     Calculated Results
                             |
                             v
                    JSON API Response
                             |
                             v
                     Dashboard Display
```

The LLM classifies the user's question into a supported intent. Flask then executes the corresponding predefined database logic. The LLM does not generate or execute SQL, which keeps database access controlled and predictable.

## Project Structure

```text
Insight-AI/
│
├── app.py                 # Flask application and API routes
├── database.py            # SQLite connections and analytical queries
├── llm.py                 # Local LLM question interpretation
├── setup_db.py            # Data cleaning and database initialization
│
├── data/
│   ├── sales.csv          # Input sales dataset
│   └── insightiq.db       # SQLite database
│
├── templates/
│   └── index.html         # Dashboard interface
│
├── tests/                 # Automated tests, if configured
│
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

*The structure above describes the intended project layout. Keep only files and folders that actually exist in your project.*

## Dataset and Data Preparation

The application uses a sales dataset containing transaction details such as:

- Transaction ID
- Order date
- Product
- Category
- Region
- Sales channel
- Quantity
- Unit price
- Discount amount
- Transaction status

The data preparation process validates the input records, handles invalid or missing values, and loads accepted records into SQLite.

### Data Cleaning Rules

- Records with zero quantity are rejected because they do not represent valid sales quantities.
- Records with missing unit prices are rejected because their revenue cannot be calculated.
- Revenue is calculated using:

  **Revenue = (Quantity × Unit Price) − Discount Amount**

- Revenue analytics include completed transactions only.
- Rejected records are reported during data preparation.

In the current dataset, 51 records were processed, 49 were accepted into the database, and 2 were rejected.

## AI-Powered Question Answering

InsightIQ uses the local Qwen 2.5 3B model through Ollama to interpret natural-language questions.

### Processing Workflow

1. The user enters a question in the dashboard.
2. The Flask backend validates the input.
3. The local LLM identifies the question's intent.
4. Flask maps the intent to predefined analytical logic.
5. SQLite retrieves the relevant sales data.
6. The backend calculates the answer and returns a JSON response.
7. The dashboard displays the result.

This approach combines natural-language interaction with deterministic database calculations, rather than relying on the LLM to invent numerical answers.

## Supported Questions

| Business Question | Analysis |
|---|---|
| What is the total revenue? | Calculates total revenue from completed transactions. |
| Which product generated the highest revenue? | Ranks products by revenue. |
| What is the monthly revenue trend? | Returns monthly revenue figures and identifies the highest- and lowest-revenue months. |
| Which region generated the highest sales? | Compares regional revenue. |
| How did revenue change between January 2026 and May 2026? | Calculates the absolute and percentage revenue change between the specified months. |

The application also handles unsupported questions and requests that do not provide valid comparison months.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Loads the dashboard. |
| GET | `/api/health` | Checks whether the API is running. |
| GET | `/api/summary` | Returns summary statistics. |
| GET | `/api/top-products` | Returns product revenue rankings. |
| GET | `/api/monthly-revenue` | Returns monthly revenue data. |
| GET | `/api/region-revenue` | Returns regional revenue data. |
| POST | `/api/ask` | Interprets a natural-language question and returns an answer. |

### Example API Request

```http
POST /api/ask
Content-Type: application/json
```

Request body:

```json
{
  "question": "Which product generated the highest revenue?"
}
```

Example response:

```json
{
  "question": "Which product generated the highest revenue?",
  "answer": "Monitor generated the highest revenue at ₹473,000.00."
}
```

The endpoint may also return structured data alongside the answer.

## Installation and Setup

### Prerequisites

Install the following:

- Python 3.10 or a compatible version
- Ollama
- Git (optional)

### 1. Clone or Download the Project

If the project is hosted on GitHub:

```bash
git clone <your-repository-url>
cd Insight-AI
```

Alternatively, open the project folder directly in your terminal.

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Ensure `requirements.txt` includes the packages actually used by the project, including Flask, Pandas, Requests, and any other required dependencies.

### 4. Start Ollama

Install Ollama and download the model:

```bash
ollama pull qwen2.5:3b
```

Make sure the Ollama service is running. The application expects the local Ollama API at:

```text
http://localhost:11434
```

The first model request may take longer while the model loads.

### 5. Initialize the Database

From the project root, run:

```bash
python setup_db.py
```

This prepares the sales data and creates or populates the SQLite database. Run this step whenever you need to rebuild the database from the source CSV.

### 6. Start the Flask Application

```bash
python app.py
```

Open the following address in your browser:

```text
http://127.0.0.1:5000
```

Keep the Flask terminal running while using the dashboard. Ollama must also be running for AI-based question interpretation.

## Testing

Test the API while the Flask application and Ollama are running.

### Example API Test

```bash
python -c "import requests; r=requests.post('http://127.0.0.1:5000/api/ask', json={'question':'What is the total revenue?'}); print(r.status_code); print(r.json())"
```

### Test Cases

| Test | Input | Expected Behavior |
|---|---|---|
| Total revenue | What is the total revenue? | Returns the calculated total revenue. |
| Top product | Which product generated the highest revenue? | Identifies the highest-revenue product. |
| Monthly trend | What is the monthly revenue trend? | Returns monthly revenue figures. |
| Top region | Which region generated the highest sales? | Identifies the leading region. |
| Month comparison | Compare January 2026 and May 2026. | Returns revenue change and percentage change. |
| Unsupported question | Who is the Prime Minister of India? | Returns a message describing supported questions. |
| Empty input | An empty question | Returns HTTP 400 with a validation message. |
| Invalid comparison | Compare three different months. | Requests exactly two valid months. |
| Invalid JSON | Missing or malformed request body | Returns an appropriate validation error. |
| AI service unavailable | Stop Ollama and submit a question. | Returns a service-unavailable response. |

Run these tests and record their actual results before claiming that all tests pass.

## Current Dataset Results

The following figures were obtained from the current dataset and database:

| Metric | Result |
|---|---:|
| Total revenue | ₹1,439,200.00 |
| Completed transactions | 48 |
| Distinct products | 7 |
| Distinct regions | 4 |
| Highest-revenue product | Monitor |
| Monitor revenue | ₹473,000.00 |
| Leading region | South |
| South region revenue | ₹411,200.00 |
| Highest-revenue month | May 2026 |
| May 2026 revenue | ₹318,500.00 |
| January 2026 revenue | ₹210,250.00 |

These results apply to the current dataset and may change when the input data is updated.

## Error Handling and Limitations

- The question must not be empty or exceed the configured character limit.
- The application supports a defined set of question types rather than arbitrary business questions.
- Month comparisons require two supported months and years.
- Answers depend on the quality and completeness of the source data.
- AI-based question interpretation requires the local Ollama service and the configured model.
- A local model may occasionally classify an ambiguous question incorrectly.
- The application uses predefined query logic; it does not currently provide unrestricted text-to-SQL generation.

## Future Enhancements

- Add more supported business questions, such as sales-channel performance and category-level revenue.
- Support revenue queries for an individual month.
- Add date-range filters and interactive dashboard controls.
- Provide downloadable reports in CSV or PDF format.
- Improve intent classification with more examples and fallback rules.
- Add authentication and role-based access control.
- Deploy the application to a cloud platform.
- Expand automated testing and continuous integration.

## Learning Outcomes

This project demonstrates practical experience with:

- Data cleaning and validation
- Relational database design and SQL aggregation
- Flask API development
- Local LLM integration
- Natural-language intent classification
- Frontend and backend integration
- Data visualization
- Input validation and error handling
- Testing and debugging

## Conclusion

InsightIQ demonstrates how natural-language processing can make traditional sales analytics more accessible. By combining a local language model with predefined SQL-based analytics, the application translates business questions into reliable, data-driven insights through an interactive dashboard.

---

**Project:** InsightIQ — AI Sales Intelligence Assistant

**Domain:** Business Intelligence, Data Analytics, and AI

**Developed using:** Python, Flask, SQLite, Pandas, Ollama, Qwen 2.5 3B, HTML, CSS, JavaScript, and Chart.js
