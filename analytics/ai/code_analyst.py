"""
Code Analyst Service - Generates and executes Python/Pandas code for data analysis

This module provides AI-powered code generation for analyzing uploaded CSV files.
Uses Gemini API to generate Python code that manipulates DataFrames and creates visualizations.
"""

import google.generativeai as genai
from django.conf import settings
from typing import Dict, Optional, List
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class CodeAnalystService:
    """
    Service for generating Python code to analyze data using AI.
    """

    def __init__(self):
        """Initialize the code analyst service with Gemini client."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def get_data_context_summary(self, df: pd.DataFrame) -> str:
        """
        Generate a concise data context summary for the AI.

        Args:
            df: DataFrame to analyze

        Returns:
            String with data context information
        """
        try:
            # Column info
            columns_info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                non_null = df[col].count()
                total = len(df)
                columns_info.append(f"  - {col} ({dtype}): {non_null}/{total} non-null")

            columns_str = "\n".join(columns_info)

            # Statistical summary for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            stats_str = ""
            if len(numeric_cols) > 0:
                stats_df = df[numeric_cols].describe()
                stats_str = "\n\nNumerical Statistics:\n" + stats_df.to_string()

            # Sample data
            sample_str = "\n\nSample Data (first 5 rows):\n" + df.head(5).to_string()

            summary = f"""
Dataset Information:
- Total Rows: {len(df)}
- Total Columns: {len(df.columns)}

Columns:
{columns_str}
{stats_str}
{sample_str}
"""
            return summary

        except Exception as e:
            logger.error(f"Error generating data context: {str(e)}")
            return "Data context unavailable"

    def get_system_prompt(self, data_context: str) -> str:
        """
        Get the system prompt for code generation.

        Args:
            data_context: Summary of the data

        Returns:
            System prompt string
        """
        return f"""You are an expert data analyst and Python programmer. The user has uploaded a CSV dataset and needs help analyzing it.

DATASET CONTEXT:
{data_context}

YOUR TASK:
Generate Python code to answer the user's question. The DataFrame is already loaded as 'df'.

INSTRUCTIONS:
1. Use ONLY the pre-loaded DataFrame variable named 'df'
2. Use pandas for data manipulation (column names may be in Thai/Unicode)
3. Use matplotlib.pyplot (imported as plt) for visualizations
4. When creating plots:
   - CRITICAL: For PIE CHARTS, ONLY use create_pie_chart() function!
     * Pattern: create_pie_chart(counts.values, counts.index, 'Title', 'Prefix')
     * This is ONE function call - do NOT write plt.figure, plt.pie, plt.savefig
     * Example: create_pie_chart(payment_counts.values, payment_counts.index,
                                'Payment Distribution', 'Payment')
   - For OTHER plots (bar, line, scatter) with Thai labels:
     * Use: safe_labels(label_array, prefix='Category')
     * Then use safe labels in your plot
   - For plot titles/axis labels: Use ENGLISH text (e.g., 'Sales Amount' not 'ยอดขาย')
   - ALWAYS print original Thai data to console
   - NEVER manually create labels with list comprehensions or loops
5. For text answers: print the result (Thai characters are OK in console output)
6. For tables: use df.to_html() or print the DataFrame (Thai is fine here)
7. Write clean, well-commented code
8. Handle edge cases (empty data, missing values, etc.)
9. Column access: Use Thai column names directly (e.g., df['ยอดขาย'].sum())
10. Filtering Thai text:
    - First explore values: print(df['column'].unique()) or df['column'].value_counts()
    - Use value_counts() for counting: payment_counts.get('QR พร้อมเพย์', 0)
    - Use .str.contains() for flexible matching if needed

OUTPUT FORMAT:
Respond with ONLY the Python code in a code block. No explanations outside the code.
Start with ```python and end with ```

EXAMPLE:
User: "What are the top 5 products by revenue?"
Your response (even if columns are in Thai):
```python
# Group by product and sum revenue (use actual Thai column names)
top_products = df.groupby('product_name')['total_amount'].sum().nlargest(5)

# Create bar chart with ENGLISH labels
plt.figure(figsize=(10, 6))
top_products.plot(kind='barh')
plt.xlabel('Revenue')  # English labels
plt.ylabel('Product')  # English labels
plt.title('Top 5 Products by Revenue')  # English title
plt.tight_layout()
plt.savefig('output.png', bbox_inches='tight', dpi=100)
plt.close()

# Print summary (Thai is OK in console output)
print("Top 5 Products by Revenue:")
print(top_products)
```

Note: If columns are 'ชื่อสินค้า' and 'ยอดขาย', use them in code but keep plot labels in English:
```python
top_products = df.groupby('ชื่อสินค้า')['ยอดขาย'].sum().nlargest(5)
plt.xlabel('Sales Amount')  # English, not 'ยอดขาย'
```

FILTERING Thai text values - IMPORTANT:
User: "How many people paid with QR พร้อมเพย์?"
```python
# Method 1: First check what values exist
print("Payment methods available:")
print(df['ช่องทางการชำระเงิน'].value_counts())

# Method 2: Use value_counts to get the count directly
payment_counts = df['ช่องทางการชำระเงิน'].value_counts()
qr_count = payment_counts.get('QR พร้อมเพย์', 0)
print(f"Number of QR พร้อมเพย์ payments: {qr_count}")

# Method 3: If exact match doesn't work, use contains
# qr_count = df[df['ช่องทางการชำระเงิน'].str.contains('QR', na=False)].shape[0]
```

PIE CHARTS with Thai labels - MANDATORY SIMPLE PATTERN:

For ANY pie chart, use EXACTLY this 3-line pattern:

```python
# Get counts
counts = df['column_name'].value_counts()

# Create chart (ONE line - handles everything!)
create_pie_chart(counts.values, counts.index, 'Chart Title', 'Prefix')

# Print Thai data
print("Distribution:")
print(counts)
```

EXAMPLE - "Create a pie chart of payment methods":
```python
payment_counts = df['ช่องทางการชำระเงิน'].value_counts()
create_pie_chart(payment_counts.values, payment_counts.index, 'Payment Methods Distribution', 'Payment')
print("Payment Methods Distribution:")
print(payment_counts)
```

THAT'S IT! Just 3 lines. Do NOT add any other plotting code!

❌ NEVER do this:
```python
# WRONG - don't write plt.figure, plt.pie, plt.savefig manually
plt.figure(figsize=(10, 6))
plt.pie(...)
```

❌ NEVER do this:
```python
# WRONG - don't create labels manually
labels = [f'Payment {i+1}' for i in range(len(counts))]
```

✅ ALWAYS do this:
```python
# RIGHT - use create_pie_chart()
create_pie_chart(counts.values, counts.index, 'Title', 'Prefix')
```

Now, respond to the user's request with executable Python code."""

    def generate_code(
        self,
        question: str,
        data_context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate Python code to answer a question about the data.

        Args:
            question: User's question about the data
            data_context: Summary of the DataFrame
            conversation_history: Previous messages in the conversation

        Returns:
            Dict with generated code and metadata
        """
        try:
            # Build the prompt
            system_prompt = self.get_system_prompt(data_context)

            # If there's conversation history, include it
            full_prompt = system_prompt + "\n\n"

            if conversation_history:
                full_prompt += "Previous Conversation:\n"
                for msg in conversation_history[-6:]:  # Last 6 messages
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if content:
                        full_prompt += f"{role}: {content}\n"
                full_prompt += "\n"

            full_prompt += f"User: {question}"

            # Call Gemini API
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more deterministic code
                    max_output_tokens=2000,
                )
            )

            response_text = response.text

            # Extract code from response
            code = self._extract_code(response_text)

            return {
                "success": True,
                "code": code,
                "raw_response": response_text
            }

        except Exception as e:
            logger.error(f"Code generation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "code": None
            }

    def _extract_code(self, response: str) -> str:
        """
        Extract Python code from the AI response.

        Args:
            response: AI's response text

        Returns:
            Extracted Python code
        """
        # Look for code between ```python and ```
        if "```python" in response:
            parts = response.split("```python")
            if len(parts) > 1:
                code_part = parts[1].split("```")[0]
                return code_part.strip()

        # Look for code between ``` and ```
        elif "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                return parts[1].strip()

        # If no code blocks, return the whole response
        return response.strip()

    def analyze_data(
        self,
        question: str,
        df: pd.DataFrame,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Complete analysis: generate code, execute it, and return results.

        Args:
            question: User's question
            df: DataFrame to analyze
            conversation_history: Previous conversation messages

        Returns:
            Dict with code, execution results, and any generated plots
        """
        try:
            # Generate data context summary
            data_context = self.get_data_context_summary(df)

            # Generate code
            code_result = self.generate_code(question, data_context, conversation_history)

            if not code_result["success"]:
                return code_result

            # Import the code executor
            from .code_executor import CodeExecutor

            # Execute the code
            executor = CodeExecutor()
            execution_result = executor.execute_code(code_result["code"], df)

            # Combine results
            return {
                "success": execution_result["success"],
                "code": code_result["code"],
                "output": execution_result.get("output", ""),
                "error": execution_result.get("error"),
                "plot_path": execution_result.get("plot_path"),
                "plot_url": execution_result.get("plot_url"),
                "execution_time": execution_result.get("execution_time", 0)
            }

        except Exception as e:
            logger.error(f"Data analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "code": None
            }
