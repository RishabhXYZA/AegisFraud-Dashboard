"""
AegisFraud Analytics - Gemini AI Chatbot Engine

Uses Google's Gemini Interactions API to provide
natural-language fraud analytics assistance.

The chatbot receives controlled analytics context from
ai_tools.py.

IMPORTANT:
Gemini does NOT directly execute SQL or access the database.
"""

from google import genai

from backend.config import Config
from backend import ai_tools


class FraudChatbot:

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def __init__(self):
        """Initialize Gemini AI client."""

        self.api_key = Config.GEMINI_API_KEY
        self.model = Config.GEMINI_MODEL

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured in the .env file."
            )

        if not self.model:
            raise ValueError(
                "GEMINI_MODEL is not configured in the .env file."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

        # =====================================================================
        # SYSTEM INSTRUCTIONS
        # =====================================================================

        self.system_instructions = """
You are Aegis AI, the intelligent fraud analytics assistant
for the AegisFraud Intelligence dashboard.

Your job is to help users understand the fraud analytics
shown in the Aegis dashboard.

You can help with:

- Fraud detection
- Fraud prevention
- Transaction risk
- Risk scoring
- Fraud trends
- Payment channels
- Payment methods
- Card brands
- Card types
- FICO score analysis
- Transaction amounts
- Fraud losses
- Geographic fraud patterns
- Time-based fraud patterns
- Executive fraud insights
- Dashboard KPIs
- Fraud analytics
- Cybersecurity
- SQL query explanation
- SQL query result interpretation

====================================================================
CRITICAL DATA RULES
====================================================================

1. NEVER invent dashboard statistics.

2. When CURRENT AEGIS ANALYTICS DATA is provided, use that
   data as the source of truth.

3. Do not replace actual dashboard values with guesses.

4. If the requested information is not available in the
   supplied analytics context, explicitly say that the
   information is not currently available.

5. Do not claim that you queried the database yourself.

6. The analytics context supplied to you has been obtained
   through approved backend analytics functions.

7. You must not generate instructions for modifying,
   deleting, inserting, dropping, or altering database data.

8. Do not suggest that the user disable the SQL safety
   controls.

====================================================================
GRAPH / CHART ANALYSIS
====================================================================

When chart data is supplied:

- Analyze the actual values.
- Identify the highest and lowest categories where possible.
- Identify trends.
- Identify concentrations.
- Compare categories when appropriate.
- Explain what the pattern means from a fraud-risk perspective.
- Distinguish clearly between observation and interpretation.
- Do not invent values that are not present in the chart data.

If the user asks:

"What does the FICO graph show?"

then use the supplied FICO chart data.

If the user asks:

"Which payment channel has the highest fraud?"

use the supplied payment-channel chart data.

If the user asks:

"When does fraud happen most?"

use the supplied day/hour heatmap data.

====================================================================
EXECUTIVE INSIGHTS
====================================================================

When executive insights are supplied:

- Explain the signal.
- Explain why it matters.
- Explain the fraud-risk implication.
- Give practical interpretation.

Do not change the supplied metrics.

====================================================================
SQL EXPLORER
====================================================================

The Aegis dashboard contains a separate Safe SQL Query Explorer.

If a SQL query and/or its result are supplied in the conversation:

- Explain what the SQL does.
- Explain tables and joins.
- Explain filters.
- Explain GROUP BY / ORDER BY.
- Explain calculated columns.
- Interpret the returned results.
- Identify meaningful patterns.
- Do NOT execute the SQL yourself.
- Do NOT modify the SQL unless the user explicitly asks
  for an explanation or improvement.
- Treat the SQL result supplied by the application as data.

The SQL Explorer itself is protected separately by the
Aegis backend.

====================================================================
GENERAL FRAUD QUESTIONS
====================================================================

For general questions that do not depend on dashboard data,
you may use your general fraud analytics and cybersecurity
knowledge.

Clearly distinguish general knowledge from dashboard-specific
observations.

====================================================================
RESPONSE STYLE
====================================================================

Respond naturally and professionally.

For simple questions:
- Keep the answer concise.

For analytical questions:
- Explain the finding.
- Explain why it matters.
- Mention important supporting values.
- Give a practical interpretation.

Use bullet points or numbered lists when useful.

Do not unnecessarily repeat the entire dataset.

You are Aegis AI, an enterprise fraud analytics assistant.
"""

    # =========================================================================
    # BUILD ANALYTICS CONTEXT
    # =========================================================================

    def get_analytics_context(self, user_message):
        """
        Retrieve only the relevant approved analytics for the
        current user question.
        """

        try:

            return ai_tools.get_relevant_analytics_json(
                user_message
            )

        except Exception as exc:

            print("=" * 70)
            print("[Aegis Analytics Context Error]")
            print("Error Type:", type(exc).__name__)
            print("Error:", str(exc))
            print("=" * 70)

            return """
{
    "success": false,
    "error": "Analytics context is currently unavailable."
}
"""

    # =========================================================================
    # GENERATE RESPONSE
    # =========================================================================

    def generate_response(
        self,
        user_message,
        sql_query=None,
        sql_result=None
    ):
        """
        Generate an AI response using Gemini Interactions API.

        Optional:
            sql_query
            sql_result

        These allow the frontend to later send the SQL Explorer
        query/result to Aegis AI for explanation.
        """

        if not user_message or not user_message.strip():

            return (
                "Please enter a question so I can help you "
                "analyze the fraud data."
            )

        try:

            # ================================================================
            # GET RELEVANT ANALYTICS
            # ================================================================

            analytics_context = self.get_analytics_context(
                user_message
            )

            # ================================================================
            # SQL EXPLORER CONTEXT
            # ================================================================

            sql_context = ""

            if sql_query:

                sql_context += f"""
====================================================================
SQL EXPLORER QUERY
====================================================================

{sql_query}
"""

            if sql_result:

                sql_context += f"""
====================================================================
SQL EXPLORER RESULT
====================================================================

{sql_result}
"""

            # ================================================================
            # GEMINI PROMPT
            # ================================================================

            prompt = f"""
CURRENT AEGIS ANALYTICS CONTEXT
====================================================================

{analytics_context}

{sql_context}

====================================================================
USER QUESTION
====================================================================

{user_message}

====================================================================
INSTRUCTIONS
====================================================================

Answer the user's question as Aegis AI.

Use the supplied Aegis analytics data whenever
the question concerns the dashboard.

If chart data is supplied, analyze the actual chart values.

If executive insights are supplied, use those insights.

If SQL query/result context is supplied, explain or
interpret it without executing the SQL.

If the requested information is not available,
say so clearly rather than inventing a value.

For general fraud questions that do not depend on
dashboard data, provide a useful professional explanation.

Keep the response clear and appropriately concise.
"""

            # ================================================================
            # GEMINI INTERACTIONS API
            # ================================================================

            interaction = self.client.interactions.create(
                model=self.model,
                input=prompt,
                system_instruction=self.system_instructions
            )

            # ================================================================
            # RETURN RESPONSE
            # ================================================================

            if interaction.output_text:

                return interaction.output_text.strip()

            return (
                "I received an empty response from Gemini. "
                "Please try your question again."
            )

        except Exception as exc:

            print("=" * 70)
            print("[Aegis Gemini AI ERROR]")
            print("Error Type:", type(exc).__name__)
            print("Error:", str(exc))
            print("=" * 70)

            return (
                "### ⚠️ Aegis AI Connection Error\n\n"
                "I couldn't connect to the Gemini AI service "
                "right now.\n\n"
                "Please check the Gemini API configuration "
                "and try again."
            )

bot = FraudChatbot()