"""
ChatGPT Service for conversational AI

This module provides a proper ChatGPT integration for natural conversation
about sales data, using the OpenAI Chat Completions API.
"""

from openai import OpenAI
from django.conf import settings
from typing import List, Dict, Optional
import logging
import json

from ..database import ch_manager
from .query_engine import QueryEngine

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service for handling conversational AI using ChatGPT.
    Maintains context and can execute SQL queries when needed.
    """

    def __init__(self):
        """Initialize the chat service with OpenAI client."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.query_engine = QueryEngine()
        self.model = "gpt-4"  # or "gpt-3.5-turbo" for faster/cheaper responses

    def get_system_prompt(self) -> str:
        """
        Get the system prompt that defines the assistant's role and capabilities.
        """
        # Get database schema
        schema_info = self._get_schema_summary()

        return f"""You are an AI sales analytics assistant with access to a sales database.
You can help users understand their sales data through natural conversation.

CAPABILITIES:
1. Answer questions about sales data by querying the database
2. Provide insights and analysis
3. Have natural conversations about the data
4. Explain trends, patterns, and anomalies

DATABASE SCHEMA:
{schema_info}

AVAILABLE DATA INCLUDES:
- Orders and sales transactions
- Product information
- Customer details
- Locations and regions
- Payment methods
- Promotions and discounts
- Date/time information

INSTRUCTIONS:
- Be conversational and friendly
- When users ask about data, indicate you'll query the database
- Provide clear, actionable insights
- Ask clarifying questions when needed
- Use context from previous messages in the conversation
- If you need to query data, say "Let me check the database for that information"

Remember: You have real access to the sales database and can provide actual data-driven answers."""

    def _get_schema_summary(self) -> str:
        """Get a summary of the database schema."""
        try:
            tables = ch_manager.get_all_tables()
            schema_parts = []

            for table in tables[:10]:  # Limit to first 10 tables
                schema = ch_manager.get_schema(table)
                columns = [f"  - {col['name']} ({col['type']})" for col in schema[:5]]  # First 5 columns
                schema_parts.append(f"\n{table}:\n" + "\n".join(columns))

            return "\n".join(schema_parts)
        except Exception as e:
            logger.error(f"Error getting schema summary: {e}")
            return "Sales database with orders, products, customers, and related dimensions"

    def chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        auto_query: bool = True
    ) -> Dict:
        """
        Send a message and get a response, maintaining conversation context.

        Args:
            message: The user's message
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            auto_query: If True, automatically detect and execute database queries

        Returns:
            Dict with response and optional query results
        """
        try:
            # Build messages array for ChatGPT
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ]

            # Add conversation history
            messages.extend(conversation_history)

            # Add current message
            messages.append({"role": "user", "content": message})

            # Check if this looks like a data query
            needs_data = auto_query and self._needs_database_query(message)

            response_data = {
                "success": True,
                "message": "",
                "needs_data": needs_data,
                "query_results": None
            }

            if needs_data:
                # Execute query and include results in the conversation
                try:
                    query_result = self.query_engine.process_question(message, language='en')

                    if query_result.get('success'):
                        # Add query context to messages
                        data_context = f"""
I queried the database and found the following:

SQL Query: {query_result['sql']}
Results: {json.dumps(query_result['results'][:10], indent=2)}  # First 10 rows
Row Count: {query_result['row_count']}

Please provide a conversational response based on this data."""

                        messages.append({
                            "role": "system",
                            "content": data_context
                        })

                        response_data["query_results"] = query_result

                except Exception as e:
                    logger.error(f"Error executing query: {e}")
                    # Continue with conversation even if query fails

            # Get ChatGPT response
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )

            response_message = completion.choices[0].message.content
            response_data["message"] = response_message

            return response_data

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "I apologize, but I encountered an error. Please try again."
            }

    def _needs_database_query(self, message: str) -> bool:
        """
        Determine if a message requires querying the database.

        Uses simple heuristics to detect data-related questions.
        """
        # Keywords that suggest data query
        query_keywords = [
            'how many', 'how much', 'what are', 'show me', 'list',
            'top', 'best', 'worst', 'total', 'average', 'sum',
            'count', 'sales', 'revenue', 'products', 'customers',
            'orders', 'trend', 'compare', 'analysis', 'data',
            'statistics', 'report', 'in', 'by month', 'by region'
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in query_keywords)

    def simple_chat(self, message: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Simple chat without automatic query execution.
        Returns just the text response.
        """
        result = self.chat(message, conversation_history, auto_query=False)
        return result.get("message", "I apologize, but I couldn't generate a response.")
