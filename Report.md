
# AI Development Report
## InsightIQ — AI Sales Intelligence Assistant

### 1. AI Tools Used

- **ChatGPT:** Used as a development assistant to understand the project requirements, plan the application architecture, troubleshoot errors, improve code, and prepare documentation.
- **Ollama with Qwen 2.5 3B:** Used as the local Large Language Model (LLM) to interpret natural-language sales questions and classify them into supported intents.

### 2. How AI Was Used During Development

ChatGPT assisted with designing the application workflow, developing the Flask API structure, implementing input validation, and debugging Python and database integration issues.

Ollama runs the Qwen 2.5 3B model locally. The model interprets questions such as “Which product generated the highest revenue?” and classifies them into predefined intents. The Flask backend then executes the corresponding database query using SQLite and returns the calculated result to the user.

AI assistance was also used to improve error handling, test different question formats, and prepare the README and project documentation.

### 3. Problems Encountered

**a. Backend connection error**

The API initially returned a connection error because the Flask server was not running when the request was sent.

**b. Local LLM integration**

The application required a running Ollama service and the correct model configuration to interpret questions successfully.

**c. Natural-language interpretation**

Some questions contained ambiguous wording or an incorrect number of months for comparison. These inputs required validation and appropriate fallback responses.

**d. Data quality issues**

The source dataset contained two invalid records: one with zero quantity and another with a missing unit price. These records were rejected during data preparation.

**e. Response formatting**

Some generated responses had missing spaces between words. The response strings were corrected to improve readability.

### 4. How the Problems Were Debugged

- Started the Flask application in a separate terminal and verified the API using HTTP requests.
- Tested the Ollama service and independently checked the `interpret_question()` function before integrating it with Flask.
- Used API requests to test supported questions, alternative phrasings, unsupported questions, empty input, and invalid month comparisons.
- Inspected rejected dataset records and applied validation rules before inserting accepted data into SQLite.
- Reviewed Python string concatenation and corrected response formatting.
- Compared API responses against database results to verify that the returned revenue figures were correct.

### Conclusion

AI tools helped accelerate development, debugging, testing, and documentation. The final application combines local LLM-based intent classification with predefined SQL analytics, allowing users to ask sales-related questions in natural language while keeping numerical calculations grounded in the database.
