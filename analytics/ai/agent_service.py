"""
Autonomous Agent Service with ReAct Loop - Gemini Edition

This module implements an autonomous AI data analyst that can reason about problems,
use tools, observe results, and provide intelligent answers through a ReAct loop.

ReAct Pattern:
1. THOUGHT: Agent reasons about the problem
2. ACTION: Agent decides to use a tool (python_executor)
3. OBSERVATION: Agent sees the result of tool execution
4. Repeat until task is complete or max iterations reached
"""

import google.generativeai as genai
from django.conf import settings
from typing import Dict, List, Optional
import logging
import json
import pandas as pd
from .code_executor import CodeExecutor

logger = logging.getLogger(__name__)


class AgentService:
    """
    Autonomous agent that can reason and use tools to analyze data.
    """

    def __init__(self):
        """Initialize the agent service."""
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Import the proper types from google.ai.generativelanguage
        from google.ai import generativelanguage as glm

        # Define the python executor tool using proper proto types
        python_executor_tool = glm.Tool(
            function_declarations=[
                glm.FunctionDeclaration(
                    name='python_executor',
                    description='Execute Python code to analyze data and create visualizations. The DataFrame df is available along with pandas (pd), numpy (np), and matplotlib (plt).',
                    parameters=glm.Schema(
                        type=glm.Type.OBJECT,
                        properties={
                            'code': glm.Schema(
                                type=glm.Type.STRING,
                                description="Python code to execute. Use 'df' for the DataFrame, 'plt' for plotting. Save plots as 'output.png'."
                            ),
                            'reasoning': glm.Schema(
                                type=glm.Type.STRING,
                                description='Your reasoning for this code - what are you trying to accomplish?'
                            )
                        },
                        required=['code', 'reasoning']
                    )
                )
            ]
        )

        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-pro',
            tools=[python_executor_tool]
        )
        self.code_executor = CodeExecutor()
        self.max_iterations = 5  # Prevent infinite loops

    def get_data_context_summary(self, df: pd.DataFrame) -> str:
        """
        Generate a comprehensive data context summary for the agent.

        Args:
            df: DataFrame to analyze

        Returns:
            String with detailed data context
        """
        try:
            # Basic info
            rows, cols = df.shape

            # Column details
            columns_info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                non_null = df[col].count()
                null_count = df[col].isnull().sum()

                # Sample unique values for categorical columns
                if dtype == 'object' and df[col].nunique() < 20:
                    unique_vals = df[col].unique()[:5].tolist()
                    unique_str = f", examples: {unique_vals}"
                else:
                    unique_str = ""

                columns_info.append(
                    f"  - {col} ({dtype}): {non_null} non-null, {null_count} null{unique_str}"
                )

            columns_str = "\n".join(columns_info)

            # Statistical summary for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            stats_str = ""
            if numeric_cols:
                stats_df = df[numeric_cols].describe()
                stats_str = f"\n\nNumerical Statistics:\n{stats_df.to_string()}"

            # Sample data (first 5 rows)
            sample_str = f"\n\nSample Data (first 5 rows):\n{df.head(5).to_string()}"

            # Data quality insights
            duplicates = df.duplicated().sum()
            quality_str = f"\n\nData Quality:\n  - Total duplicates: {duplicates}"

            summary = f"""
Dataset Information:
- Total Rows: {rows:,}
- Total Columns: {cols}
- Memory Usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB

Columns:
{columns_str}
{stats_str}
{sample_str}
{quality_str}
"""
            return summary.strip()

        except Exception as e:
            logger.error(f"Error generating data context: {str(e)}")
            return f"Dataset with {len(df)} rows and {len(df.columns)} columns"

    def get_system_prompt(self, data_context: str) -> str:
        """
        Get the system prompt that defines the agent's behavior.

        Args:
            data_context: Summary of the data

        Returns:
            System prompt string
        """
        return f"""You are an autonomous AI Data Analyst Agent. Your role is to help users understand and analyze their data through intelligent reasoning and tool use.

DATA CONTEXT:
{data_context}

YOUR CAPABILITIES:
- You can REASON step-by-step about data analysis problems
- You have access to a Pandas DataFrame named 'df' with the user's data
- You can execute Python code to analyze data and create visualizations
- You can self-correct errors and try alternative approaches
- You provide clear, insightful answers based on data

YOUR TOOL:
You have access to the "python_executor" function that executes Python code.

Available in execution environment:
- df: The user's DataFrame (already loaded)
- pd: pandas library
- np: numpy library
- plt: matplotlib.pyplot
- Standard Python functions

Code Guidelines:
1. Use 'df' to access the DataFrame (column names may be in Thai/Unicode)
2. For visualizations:
   - Use plt.figure(figsize=(10, 6))
   - CRITICAL: For ANY plot with Thai/non-ASCII labels (pie, bar, scatter, etc.):
     * ALWAYS use safe_labels() helper to convert labels to ASCII format
     * Example: safe_payment_labels = safe_labels(payment_counts.index, prefix='Method')
     * Then use: plt.pie(values, labels=safe_payment_labels, ...)
     * This is REQUIRED to prevent encoding errors
   - For plot titles, axis labels: Use ENGLISH text (e.g., 'Sales Amount' not 'ยอดขาย')
   - Save plots as 'output.png' using plt.savefig('output.png', bbox_inches='tight', dpi=100)
   - Call plt.close() after saving
   - ALWAYS print the actual Thai data to console so user can see the mapping
3. For text results: use print() - Thai characters are fine in console output
4. For tables: use print(df.to_string()) or df.to_html() - Thai is fine here
5. Handle edge cases (missing values, empty data, etc.)
6. Column access: Use Thai column names directly in code (e.g., df['ยอดขาย'])
7. Filtering Thai text values:
   - FIRST check what values exist: print(df['column'].unique()) or df['column'].value_counts()
   - Strip whitespace: df['column'].str.strip()
   - Use contains for flexible matching: df[df['column'].str.contains('keyword', na=False)]
   - Example: df[df['ช่องทางการชำระเงิน'].str.strip() == 'QR พร้อมเพย์']
   - Or use: df['ช่องทางการชำระเงิน'].value_counts() to see all options first

CRITICAL - PIE CHARTS with Thai Text:

For ANY pie chart request, use EXACTLY this pattern (copy this code exactly!):

```python
# Step 1: Get the counts
payment_counts = df['column_name'].value_counts()

# Step 2: Create pie chart using the convenience function (ONE LINE!)
create_pie_chart(payment_counts.values, payment_counts.index, 'Chart Title', 'Label')

# Step 3: Print the Thai data for reference
print("Distribution:")
print(payment_counts)
```

EXAMPLE - "Create a pie chart of payment methods":
```python
payment_counts = df['ช่องทางการชำระเงิน'].value_counts()
create_pie_chart(payment_counts.values, payment_counts.index, 'Payment Methods Distribution', 'Payment')
print("Payment Methods Distribution:")
print(payment_counts)
```

That's it! Just 3 lines of code. Do NOT:
- Do NOT write any plt.figure() code
- Do NOT write any plt.pie() code
- Do NOT write any plt.savefig() code
- Do NOT write any plt.close() code
- Do NOT create labels manually with list comprehensions
- Do NOT use variables named 'i' or 'label' outside their scope

The create_pie_chart() function handles EVERYTHING automatically!

REASONING PROCESS:
1. ANALYZE the user's request carefully
2. PLAN your approach step-by-step
3. USE the python_executor tool to implement your plan
4. OBSERVE the results (you'll get stdout, errors, or plot paths)
5. If successful: Provide final answer to user
6. If error: Analyze the error, think about correction, try again

ERROR HANDLING:
- If you encounter an error, read it carefully
- Think about what went wrong
- Generate corrected code
- Try again (you have up to {self.max_iterations} attempts)
- Common issues:
  * "name 'i' is not defined" → You tried to create labels manually! Use create_pie_chart() instead
  * Thai text filtering fails → use value_counts() instead of direct filtering
  * Encoding/Unicode error in plots → use create_pie_chart() for pie charts
  * "text not in expected string format" → use create_pie_chart() instead of plt.pie()
  * Any pie chart error → Just use create_pie_chart() - it's foolproof!

IMPORTANT:
- Always think before acting
- Be precise with column names
- Check data types before operations
- Provide context with your answers
- If you create a plot, mention it in your response

FILTERING THAI TEXT - Best Practices:
Instead of: df[df['column'] == 'Thai text']  # May fail
Use: df['column'].value_counts()  # See what exists, then get count directly
Example:
  payment_counts = df['ช่องทางการชำระเงิน'].value_counts()
  qr_count = payment_counts.get('QR พร้อมเพย์', 0)

Remember: You are autonomous. Make decisions, correct mistakes, and deliver results."""

    def execute_tool_call(self, function_call, df: pd.DataFrame) -> Dict:
        """
        Execute a tool call from Gemini.

        Args:
            function_call: Function call from Gemini
            df: DataFrame to make available

        Returns:
            Execution result dictionary
        """
        try:
            # Extract arguments - Gemini returns them as a dict in 'args' attribute
            args = function_call.args
            code = args.get('code', '')
            reasoning = args.get('reasoning', '')

            logger.info(f"Executing code with reasoning: {reasoning}")

            # Execute the code
            result = self.code_executor.execute_code(code, df)
            return result

        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output": ""
            }

    def run_react_loop(
        self,
        user_message: str,
        df: pd.DataFrame,
        conversation_history: Optional[List[Dict]] = None,
        show_reasoning: bool = False
    ) -> Dict:
        """
        Run the ReAct loop: Thought → Action → Observation → repeat.

        Args:
            user_message: User's question/request
            df: DataFrame to analyze
            conversation_history: Previous messages in conversation
            show_reasoning: Whether to include reasoning steps in response

        Returns:
            Dict with final answer, reasoning steps, and any artifacts
        """
        try:
            # Generate data context
            data_context = self.get_data_context_summary(df)
            system_prompt = self.get_system_prompt(data_context)

            # Initialize chat session
            chat = self.model.start_chat(history=[])

            # Build the initial prompt
            full_prompt = f"{system_prompt}\n\nUser Request: {user_message}"

            # Add conversation history context if provided
            if conversation_history:
                history_text = "\n\nPrevious Conversation:\n"
                for msg in conversation_history[-10:]:  # Last 10 messages
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if content:  # Skip empty messages
                        history_text += f"{role}: {content}\n"
                full_prompt = f"{system_prompt}\n{history_text}\nCurrent User Request: {user_message}"

            # Track reasoning steps for transparency
            reasoning_steps = []
            plot_url = None
            final_output = ""

            # ReAct loop
            for iteration in range(self.max_iterations):
                logger.info(f"Agent iteration {iteration + 1}/{self.max_iterations}")

                try:
                    # Agent thinks and decides action
                    response = chat.send_message(full_prompt)

                    # Check if agent wants to use a tool
                    function_call_found = False

                    # Check each part of the response
                    for part in response.candidates[0].content.parts:
                        # Check for function call
                        if hasattr(part, 'function_call') and part.function_call:
                            function_call = part.function_call
                            function_call_found = True

                            # Extract reasoning and code
                            args = function_call.args
                            reasoning = args.get('reasoning', '')
                            code = args.get('code', '')

                            logger.info(f"Agent using tool: python_executor")
                            logger.info(f"Reasoning: {reasoning}")

                            # Record reasoning step
                            reasoning_steps.append({
                                "iteration": iteration + 1,
                                "reasoning": reasoning,
                                "action": "python_executor",
                                "code": code
                            })

                            # Execute the tool
                            execution_result = self.execute_tool_call(function_call, df)

                            # Prepare observation for agent
                            if execution_result['success']:
                                observation = f"✓ Execution successful!\n\nOutput:\n{execution_result['output']}"
                                if execution_result.get('plot_url'):
                                    plot_url = execution_result['plot_url']
                                    observation += f"\n\n✓ Plot saved: {plot_url}"

                                reasoning_steps[-1]['observation'] = 'Success'
                                reasoning_steps[-1]['output'] = execution_result['output']
                            else:
                                error_msg = execution_result.get('error', 'Unknown error')
                                observation = f"✗ Execution failed!\n\nError:\n{error_msg}"

                                # If there's a traceback, include relevant parts
                                if execution_result.get('error_trace'):
                                    # Get just the last few lines of traceback
                                    trace_lines = execution_result['error_trace'].split('\n')
                                    # Show the actual error line
                                    relevant_trace = '\n'.join(trace_lines[-5:])
                                    observation += f"\n\nError details:\n{relevant_trace}"

                                reasoning_steps[-1]['observation'] = 'Error'
                                reasoning_steps[-1]['error'] = error_msg

                            # Send function response back to agent using proper glm types
                            from google.ai import generativelanguage as glm

                            function_response = glm.Part(
                                function_response=glm.FunctionResponse(
                                    name='python_executor',
                                    response={'result': observation}
                                )
                            )

                            response = chat.send_message(function_response)

                            # Check if agent has a text response after function call
                            for response_part in response.candidates[0].content.parts:
                                if hasattr(response_part, 'text') and response_part.text:
                                    final_output = response_part.text
                                    logger.info(f"Agent finished after {iteration + 1} iterations")
                                    break

                            break  # Exit part loop

                    # If no function call, check for text response
                    if not function_call_found:
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'text') and part.text:
                                final_output = part.text
                                logger.info(f"Agent finished after {iteration + 1} iterations")
                                break

                    if final_output:
                        break

                except Exception as e:
                    logger.error(f"Iteration error: {str(e)}", exc_info=True)
                    # Try to continue or break if critical
                    if iteration == self.max_iterations - 1:
                        raise

            # Check if we hit max iterations without completion
            if not final_output:
                final_output = "I've analyzed your data but need more iterations to provide a complete answer. Please try asking in a different way or breaking down your request."

            return {
                "success": True,
                "message": final_output,
                "reasoning_steps": reasoning_steps if show_reasoning else [],
                "plot_url": plot_url,
                "iterations": len(reasoning_steps),
                "messages": []  # Gemini doesn't expose message history the same way
            }

        except Exception as e:
            logger.error(f"ReAct loop error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"I encountered an error while processing your request: {str(e)}"
            }


# Utility function to get agent instance
def get_agent_service() -> AgentService:
    """Get an AgentService instance."""
    return AgentService()
