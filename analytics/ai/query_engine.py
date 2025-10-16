"""
AI Query Engine for Natural Language to SQL Translation

This module uses OpenAI and LangChain to translate natural language questions
into SQL queries and summarize results.
"""

from typing import Dict, List, Optional, Tuple
import logging
from django.conf import settings

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from analytics.database import ch_manager

logger = logging.getLogger(__name__)


class QueryEngine:
    """
    AI-powered query engine for translating natural language to SQL.
    """

    def __init__(self):
        """Initialize the query engine with OpenAI LLM."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured in settings")

        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,  # Deterministic for SQL generation
            openai_api_key=settings.OPENAI_API_KEY
        )

        self.schema_cache = None
        self.load_schema()

    def load_schema(self):
        """Load database schema for context."""
        try:
            schema_info = self.get_schema_description()
            self.schema_cache = schema_info
            logger.info("Database schema loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load schema: {str(e)}")
            self.schema_cache = "Schema unavailable"

    def get_schema_description(self) -> str:
        """
        Get a human-readable description of the database schema.

        Returns:
            String describing the database structure
        """
        try:
            tables = ch_manager.get_all_tables()

            schema_desc = "# Sales Analytics Database Schema\n\n"

            for table in tables:
                if table.startswith('v_'):  # Skip views
                    continue

                schema = ch_manager.get_schema(table)

                schema_desc += f"## Table: {table}\n"
                schema_desc += "Columns:\n"

                for col in schema:
                    schema_desc += f"- {col['name']} ({col['type']})\n"

                schema_desc += "\n"

            # Add table relationships
            schema_desc += """
## Table Relationships:

### Fact Table:
- **fact_orders**: Central transaction table
  - Links to dim_products via product_id
  - Links to dim_customers via customer_id
  - Links to dim_dates via date_id
  - Links to dim_payments via payment_id
  - Links to dim_promotions via promotion_id
  - Links to dim_locations via location_id

### Dimension Tables:
- **dim_products**: Product information (SKU, name, category, price)
- **dim_customers**: Customer details (name, email, location)
- **dim_dates**: Date dimension (year, month, quarter, etc.)
- **dim_payments**: Payment methods
- **dim_promotions**: Promotion/discount codes
- **dim_locations**: Geographic locations (province, city, region)

## Common Query Patterns:

1. Sales by Product:
   JOIN fact_orders f WITH dim_products p ON f.product_id = p.product_id

2. Sales by Location:
   JOIN fact_orders f WITH dim_locations l ON f.location_id = l.location_id

3. Sales by Time Period:
   JOIN fact_orders f WITH dim_dates d ON f.date_id = d.date_id

4. Customer Analysis:
   JOIN fact_orders f WITH dim_customers c ON f.customer_id = c.customer_id
"""

            return schema_desc

        except Exception as e:
            logger.error(f"Failed to generate schema description: {str(e)}")
            return "Schema generation failed"

    def generate_sql(self, question: str, language: str = "en") -> Tuple[str, str]:
        """
        Generate SQL query from natural language question.

        Args:
            question: Natural language question
            language: Language of the question ('en' or 'th')

        Returns:
            Tuple of (sql_query, explanation)

        Raises:
            Exception: If SQL generation fails
        """
        try:
            system_prompt = """You are an expert SQL query generator for a ClickHouse sales analytics database.

Your task is to convert natural language questions into valid ClickHouse SQL queries.

Guidelines:
1. Use only the tables and columns described in the schema
2. Generate syntactically correct ClickHouse SQL
3. Use appropriate aggregations (SUM, COUNT, AVG, etc.)
4. Include proper JOINs when referencing multiple tables
5. Add ORDER BY and LIMIT clauses when appropriate
6. Use date functions properly for date filtering
7. Always use meaningful column aliases
8. Avoid using SELECT * - specify columns explicitly
9. For "top N" questions, add ORDER BY with LIMIT
10. Use LIKE for pattern matching with % wildcards

Security Rules:
- NEVER use DELETE, UPDATE, DROP, or ALTER statements
- NEVER use system tables
- Only SELECT queries are allowed

Database Schema:
{schema}

Examples:
Question: "What are the top 5 best-selling products?"
SQL: SELECT p.product_name, SUM(f.quantity) as total_quantity, SUM(f.total_amount) as revenue
     FROM fact_orders f
     JOIN dim_products p ON f.product_id = p.product_id
     GROUP BY p.product_name
     ORDER BY total_quantity DESC
     LIMIT 5

Question: "Total sales in Bangkok?"
SQL: SELECT SUM(f.total_amount) as total_sales
     FROM fact_orders f
     JOIN dim_locations l ON f.location_id = l.location_id
     WHERE l.province = 'Bangkok'

Question: "Sales by month in 2024?"
SQL: SELECT d.year, d.month_name, SUM(f.total_amount) as monthly_sales
     FROM fact_orders f
     JOIN dim_dates d ON f.date_id = d.date_id
     WHERE d.year = 2024
     GROUP BY d.year, d.month, d.month_name
     ORDER BY d.month

Return ONLY the SQL query without any explanation or markdown formatting.
"""

            user_prompt = f"Generate a SQL query for this question: {question}"

            messages = [
                SystemMessage(content=system_prompt.format(schema=self.schema_cache)),
                HumanMessage(content=user_prompt)
            ]

            response = self.llm.invoke(messages)
            sql_query = response.content.strip()

            # Remove markdown code blocks if present
            if sql_query.startswith('```'):
                sql_query = sql_query.split('```')[1]
                if sql_query.startswith('sql'):
                    sql_query = sql_query[3:]
                sql_query = sql_query.strip()

            # Validate the query
            self.validate_sql(sql_query)

            # Generate explanation
            explanation = self.explain_sql(sql_query, question)

            logger.info(f"Generated SQL for question: {question}")
            logger.debug(f"SQL: {sql_query}")

            return sql_query, explanation

        except Exception as e:
            logger.error(f"SQL generation failed: {str(e)}")
            raise

    def validate_sql(self, sql: str):
        """
        Validate SQL query for security and correctness.

        Args:
            sql: SQL query to validate

        Raises:
            ValueError: If query is invalid or unsafe
        """
        sql_upper = sql.upper()

        # Security checks
        dangerous_keywords = ['DELETE', 'UPDATE', 'DROP', 'ALTER', 'TRUNCATE', 'CREATE', 'INSERT']

        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                raise ValueError(f"Forbidden SQL operation: {keyword}")

        # Must be a SELECT query
        if not sql_upper.strip().startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed")

        # No system table access
        if 'SYSTEM.' in sql_upper:
            raise ValueError("Access to system tables is forbidden")

        logger.debug("SQL validation passed")

    def explain_sql(self, sql: str, question: str) -> str:
        """
        Generate a human-readable explanation of the SQL query.

        Args:
            sql: SQL query
            question: Original question

        Returns:
            Explanation string
        """
        try:
            prompt = f"""Given this question: "{question}"
And this SQL query:
{sql}

Provide a brief, user-friendly explanation of what the query does and what results to expect.
Keep it under 2 sentences."""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()

        except Exception as e:
            logger.warning(f"Failed to generate explanation: {str(e)}")
            return "Query explanation unavailable"

    def execute_query(self, sql: str) -> Dict:
        """
        Execute SQL query and return results.

        Args:
            sql: SQL query to execute

        Returns:
            Dictionary with query results and metadata

        Raises:
            Exception: If query execution fails
        """
        try:
            # Execute with column names
            data, columns = ch_manager.execute_with_column_names(sql)

            # Convert to list of dicts
            results = []
            for row in data:
                results.append(dict(zip(columns, row)))

            logger.info(f"Query executed successfully, returned {len(results)} rows")

            return {
                'success': True,
                'rows': results,
                'row_count': len(results),
                'columns': columns,
                'sql': sql
            }

        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'sql': sql
            }

    def summarize_results(self, results: List[Dict], question: str) -> str:
        """
        Generate a natural language summary of query results.

        Args:
            results: List of result dictionaries
            question: Original question

        Returns:
            Natural language summary

        Raises:
            Exception: If summarization fails
        """
        try:
            if not results:
                return "No results found for your question."

            # Prepare results for summarization (limit to avoid token overflow)
            results_preview = results[:100]  # First 100 rows

            prompt = f"""Given this question: "{question}"

And these query results:
{results_preview}

Provide a concise, business-friendly summary of the findings in 2-3 sentences.
Focus on key insights and actionable information.

If there are specific numbers, mention them. If there are top items, list them.
"""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            summary = response.content.strip()

            logger.info("Results summarized successfully")

            return summary

        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            return f"Found {len(results)} results. Please review the data table for details."

    def process_question(self, question: str, language: str = "en") -> Dict:
        """
        Process a natural language question through the complete pipeline.

        Args:
            question: Natural language question
            language: Language code ('en' or 'th')

        Returns:
            Dictionary with SQL, results, and summary

        Raises:
            Exception: If processing fails
        """
        try:
            logger.info(f"Processing question: {question}")

            # Generate SQL
            sql, explanation = self.generate_sql(question, language)

            # Execute query
            query_result = self.execute_query(sql)

            if not query_result['success']:
                return {
                    'success': False,
                    'error': query_result['error'],
                    'sql': sql,
                    'explanation': explanation
                }

            # Summarize results
            summary = self.summarize_results(query_result['rows'], question)

            return {
                'success': True,
                'question': question,
                'sql': sql,
                'explanation': explanation,
                'results': query_result['rows'],
                'row_count': query_result['row_count'],
                'columns': query_result['columns'],
                'summary': summary
            }

        except Exception as e:
            logger.error(f"Question processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'question': question
            }


# Singleton instance
query_engine = None


def get_query_engine() -> QueryEngine:
    """Get or create the query engine instance."""
    global query_engine

    if query_engine is None:
        query_engine = QueryEngine()

    return query_engine
