"""
AegisFraud Analytics - AI Analytics Tools

Controlled analytics layer for Aegis AI.

This module does NOT execute arbitrary SQL supplied by Gemini.
It only exposes approved analytics functions already defined
in analytics.py.

analytics.py remains unchanged.
"""

import json
import math

from backend import analytics


# =============================================================================
# GENERAL HELPERS
# =============================================================================

def _clean_value(value):
    """
    Convert database / Plotly / pandas values into JSON-safe Python values.
    """

    if value is None:
        return None

    # Handle dictionaries
    if isinstance(value, dict):
        return {
            str(k): _clean_value(v)
            for k, v in value.items()
        }

    # Handle lists / tuples
    if isinstance(value, (list, tuple)):
        return [_clean_value(v) for v in value]

    # Handle numpy-like scalar values
    if hasattr(value, "item"):
        try:
            return _clean_value(value.item())
        except Exception:
            pass

    # Handle NaN / infinity
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None

    return value


# =============================================================================
# KPI TOOL
# =============================================================================

def get_dashboard_kpis():
    """
    Return the current dashboard KPI metrics.
    """

    data = analytics.get_kpi_metrics()

    if not data:
        return {
            "success": False,
            "error": "Dashboard KPI data is unavailable."
        }

    if "error" in data:
        return {
            "success": False,
            "error": data["error"]
        }

    return {
        "success": True,
        "data": _clean_value(data)
    }


# =============================================================================
# EXECUTIVE INSIGHTS TOOL
# =============================================================================

def get_executive_insights():
    """
    Return executive-level fraud insights, signals,
    macro trends, governance gaps and strategic priorities.
    """

    data = analytics.get_executive_insights_data()

    if not data:
        return {
            "success": False,
            "error": "Executive insight data is unavailable."
        }

    return {
        "success": True,
        "data": _clean_value(data)
    }


# =============================================================================
# OVERVIEW TOOL
# =============================================================================

def get_dashboard_overview():
    """
    Return the dashboard overview including:
    - KPIs
    - executive briefing
    - risk pillars
    - fraud workflow
    """

    data = analytics.get_overview_data()

    if not data:
        return {
            "success": False,
            "error": "Dashboard overview data is unavailable."
        }

    return {
        "success": True,
        "data": _clean_value(data)
    }


# =============================================================================
# CHART CATALOG
# =============================================================================

CHART_ALIASES = {

    # Division 1
    "fraud_distribution": "v01_fraud_distribution",
    "overall_fraud": "v01_fraud_distribution",
    "fraud_share": "v01_fraud_distribution",
    "legitimate_vs_fraud": "v01_fraud_distribution",

    "payment_channel": "v04_fraud_payment_method",
    "payment_method": "v04_fraud_payment_method",
    "channel": "v04_fraud_payment_method",
    "fraud_channel": "v04_fraud_payment_method",

    "ticket_size": "v14_fraud_amount_distribution",
    "fraud_amount_band": "v14_fraud_amount_distribution",
    "fraud_amount_distribution": "v14_fraud_amount_distribution",

    "annual_fraud_rate": "v02_fraud_rate_year",
    "fraud_rate_year": "v02_fraud_rate_year",
    "yearly_fraud": "v02_fraud_rate_year",

    "volume_vs_fraud": "v03_volume_vs_fraud_year",
    "transaction_volume": "v03_volume_vs_fraud_year",
    "yearly_volume": "v03_volume_vs_fraud_year",

    # Division 2
    "day_hour": "v05_day_hour_heatmap",
    "heatmap": "v05_day_hour_heatmap",
    "time_heatmap": "v05_day_hour_heatmap",
    "fraud_time": "v05_day_hour_heatmap",

    "card_brand": "v07_fraud_card_brand",
    "brand": "v07_fraud_card_brand",

    "card_type": "v08_fraud_card_type",
    "debit_credit": "v08_fraud_card_type",

    "fico": "v09_fraud_fico_category",
    "fico_score": "v09_fraud_fico_category",
    "fico_band": "v09_fraud_fico_category",

    # Division 3
    "state": "v10_us_state_map",
    "geographic": "v10_us_state_map",
    "geography": "v10_us_state_map",
    "us_state": "v10_us_state_map",

    "annual_loss": "v18_yearly_total_vs_fraud_amount",
    "yearly_loss": "v18_yearly_total_vs_fraud_amount",
    "loss_vs_volume": "v18_yearly_total_vs_fraud_amount",

    "outliers": "v17_amount_box_plot",
    "amount_outliers": "v17_amount_box_plot",
    "box_plot": "v17_amount_box_plot",

    "overall_amount": "v13_overall_amount_distribution",
    "amount_distribution": "v13_overall_amount_distribution",
}


# =============================================================================
# FIND CHART
# =============================================================================

def _find_chart(chart_id):
    """
    Locate an approved chart function from analytics.DIVISIONS.

    No arbitrary Python function name is accepted.
    """

    for division in analytics.DIVISIONS.values():

        for chart in division["charts"]:

            if chart["id"] == chart_id:
                return chart["fn"], chart["name"]

    return None, None


# =============================================================================
# EXTRACT USEFUL DATA FROM PLOTLY FIGURE
# =============================================================================

def _extract_chart_data(fig):
    """
    Extract only analytical information from a Plotly figure.

    We intentionally do not send the complete Plotly object/template
    to Gemini because it contains unnecessary visualization metadata.
    """

    extracted = {
        "title": None,
        "traces": []
    }

    try:

        figure = fig.to_dict()

        # -------------------------------------------------------------
        # Title
        # -------------------------------------------------------------

        layout = figure.get("layout", {})

        title = layout.get("title")

        if isinstance(title, dict):
            extracted["title"] = title.get("text")

        elif title:
            extracted["title"] = str(title)

        # -------------------------------------------------------------
        # Traces
        # -------------------------------------------------------------

        for trace in figure.get("data", []):

            trace_data = {
                "type": trace.get("type"),
                "name": trace.get("name"),
            }

            # Standard x/y charts
            if "x" in trace:
                trace_data["x"] = _clean_value(trace["x"])

            if "y" in trace:
                trace_data["y"] = _clean_value(trace["y"])

            # Pie charts
            if "labels" in trace:
                trace_data["labels"] = _clean_value(trace["labels"])

            if "values" in trace:
                trace_data["values"] = _clean_value(trace["values"])

            # Heatmaps
            if "z" in trace:
                trace_data["z"] = _clean_value(trace["z"])

            # Heatmap axes
            if "x" in trace:
                trace_data["x"] = _clean_value(trace["x"])

            if "y" in trace:
                trace_data["y"] = _clean_value(trace["y"])

            # Box plots
            if "boxpoints" in trace:
                trace_data["boxpoints"] = _clean_value(
                    trace["boxpoints"]
                )

            if "text" in trace:
                trace_data["text"] = _clean_value(
                    trace["text"]
                )

            extracted["traces"].append(trace_data)

    except Exception as exc:

        return {
            "error": f"Unable to extract chart data: {str(exc)}"
        }

    return extracted


# =============================================================================
# GET CHART DATA
# =============================================================================

def get_chart_data(chart_id):
    """
    Execute one approved analytics chart and return its
    underlying analytical data.

    Example:
        get_chart_data("v09_fraud_fico_category")
    """

    # Allow aliases
    chart_id = CHART_ALIASES.get(
        chart_id.lower().strip(),
        chart_id
    )

    chart_function, chart_name = _find_chart(chart_id)

    if chart_function is None:

        return {
            "success": False,
            "error": (
                f"Chart '{chart_id}' is not an approved "
                "Aegis analytics chart."
            )
        }

    try:

        fig = chart_function()

        chart_data = _extract_chart_data(fig)

        return {
            "success": True,
            "chart_id": chart_id,
            "chart_name": chart_name,
            "data": chart_data
        }

    except Exception as exc:

        return {
            "success": False,
            "chart_id": chart_id,
            "chart_name": chart_name,
            "error": str(exc)
        }


# =============================================================================
# LIST AVAILABLE CHARTS
# =============================================================================

def get_available_charts():
    """
    Return a simple catalog of charts available to Aegis AI.
    """
    charts = []
    for division_id, division in analytics.DIVISIONS.items():
        for chart in division["charts"]:

            charts.append({
                "division": division_id,
                "chart_id": chart["id"],
                "name": chart["name"],
                "description": division["description"]
            })

    return {
        "success": True,
        "charts": charts
    }


# =============================================================================
# QUESTION → RELEVANT ANALYTICS
# =============================================================================

def get_relevant_analytics(user_question):
    """
    Determine which approved analytics should be supplied to Gemini.

    This is intentionally deterministic.

    Gemini is NOT allowed to choose arbitrary SQL or arbitrary
    Python functions.
    """

    question = (user_question or "").lower()

    context = {
        "kpis": None,
        "overview": None,
        "executive_insights": None,
        "charts": []
    }

    # -----------------------------------------------------------------
    # Always provide KPIs
    # -----------------------------------------------------------------

    kpi_result = get_dashboard_kpis()

    if kpi_result.get("success"):
        context["kpis"] = kpi_result["data"]

    # -----------------------------------------------------------------
    # Executive / strategic questions
    # -----------------------------------------------------------------

    executive_keywords = [
        "executive",
        "insight",
        "insights",
        "risk",
        "strategy",
        "strategic",
        "recommendation",
        "recommendations",
        "governance",
        "portfolio",
        "major risk",
        "key risk",
        "overall dashboard",
        "overall analysis",
    ]

    if any(keyword in question for keyword in executive_keywords):

        result = get_executive_insights()

        if result.get("success"):
            context["executive_insights"] = result["data"]

    # -----------------------------------------------------------------
    # Overview / briefing questions
    # -----------------------------------------------------------------

    overview_keywords = [
        "overview",
        "briefing",
        "health",
        "portfolio health",
        "dashboard summary",
        "summarize dashboard",
        "summary",
    ]

    if any(keyword in question for keyword in overview_keywords):

        result = get_dashboard_overview()

        if result.get("success"):
            context["overview"] = result["data"]

    # -----------------------------------------------------------------
    # Chart mappings
    # -----------------------------------------------------------------

    chart_keywords = {

        "v01_fraud_distribution": [
            "fraud share",
            "fraud distribution",
            "fraud vs legitimate",
            "legitimate vs fraud",
            "overall fraud",
        ],

        "v04_fraud_payment_method": [
            "payment channel",
            "payment method",
            "payment type",
            "channel",
            "online",
            "chip",
            "swipe",
        ],

        "v14_fraud_amount_distribution": [
            "ticket size",
            "amount band",
            "fraud amount",
            "fraud amount distribution",
            "transaction amount",
        ],

        "v02_fraud_rate_year": [
            "fraud rate by year",
            "annual fraud rate",
            "yearly fraud rate",
            "fraud rate trend",
            "fraud trend",
        ],

        "v03_volume_vs_fraud_year": [
            "volume vs fraud",
            "transaction volume",
            "fraud volume",
            "transactions over time",
            "volume over time",
        ],

        "v05_day_hour_heatmap": [
            "day and hour",
            "day hour",
            "heatmap",
            "time heatmap",
            "when does fraud happen",
            "fraud timing",
            "fraud time",
            "hour",
            "hours",
            "off-hours",
        ],

        "v07_fraud_card_brand": [
            "card brand",
            "visa",
            "mastercard",
            "amex",
            "discover",
            "brand",
        ],

        "v08_fraud_card_type": [
            "card type",
            "debit vs credit",
            "debit",
            "credit card",
        ],

        "v09_fraud_fico_category": [
            "fico",
            "fico score",
            "fico band",
            "credit score",
            "credit score band",
        ],

        "v10_us_state_map": [
            "state",
            "states",
            "geographic",
            "geography",
            "location",
            "hotspot",
            "hotspots",
            "map",
        ],

        "v18_yearly_total_vs_fraud_amount": [
            "annual loss",
            "yearly loss",
            "loss vs volume",
            "fraud loss by year",
            "fraud amount by year",
            "financial loss",
        ],

        "v17_amount_box_plot": [
            "outlier",
            "outliers",
            "box plot",
            "amount outlier",
            "transaction outlier",
        ],

        "v13_overall_amount_distribution": [
            "overall amount",
            "amount distribution",
            "transaction distribution",
            "ticket distribution",
        ],
    }

    # -----------------------------------------------------------------
    # Identify relevant charts
    # -----------------------------------------------------------------

    selected_chart_ids = []

    for chart_id, keywords in chart_keywords.items():

        if any(keyword in question for keyword in keywords):

            if chart_id not in selected_chart_ids:
                selected_chart_ids.append(chart_id)

    # -----------------------------------------------------------------
    # If user explicitly asks for graph/chart/visualization analysis
    # but no exact chart matched, provide chart catalog.
    # -----------------------------------------------------------------

    graph_words = [
        "graph",
        "graphs",
        "chart",
        "charts",
        "visual",
        "visualization",
        "plot",
    ]

    if (
        any(word in question for word in graph_words)
        and not selected_chart_ids
    ):

        catalog = get_available_charts()

        context["available_charts"] = catalog.get(
            "charts",
            []
        )

    # -----------------------------------------------------------------
    # Execute selected approved charts
    # -----------------------------------------------------------------

    for chart_id in selected_chart_ids:

        result = get_chart_data(chart_id)

        if result.get("success"):

            context["charts"].append(result)

    return {
        "success": True,
        "context": _clean_value(context)
    }


# =============================================================================
# COMPACT JSON FOR GEMINI
# =============================================================================

def get_relevant_analytics_json(user_question):
    """
    Return analytics context as compact JSON text.

    This is useful for passing the controlled analytics context
    directly into Gemini.
    """
    result = get_relevant_analytics(user_question)
    return json.dumps(
        result,
        indent=2,
        ensure_ascii=False,
        default=str
    )