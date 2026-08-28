# ============================================================
# AEGIS FRAUD DETECTION ANALYTICAL DASHBOARD
# Flask Backend Server
# ============================================================

import os
from flask import Flask, render_template, jsonify, request
from config import Config
import database
import query_registry
import analytics
from chatbot_engine import bot


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")


app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

app.config.from_object(Config)

@app.route("/")
def index():
    """Render main dashboard single-page interface."""
    return render_template("index.html")

@app.route("/api/kpis", methods=["GET"])
def api_kpis():
    """Retrieve top executive KPI metrics."""
    data = analytics.get_kpi_metrics()

    return jsonify({
        "success": True,
        "data": data
    })

@app.route("/api/overview", methods=["GET"])
def api_overview():
    """Retrieve executive overview data & workflow."""
    data = analytics.get_overview_data()

    return jsonify({
        "success": True,
        "data": data
    })

@app.route("/api/insights", methods=["GET"])
def api_insights():
    """Retrieve executive business intelligence insights."""
    data = analytics.get_executive_insights_data()

    return jsonify({
        "success": True,
        "data": data
    })

@app.route("/api/charts/division/<division_id>", methods=["GET"])
def api_charts_division(division_id):
    """
    Retrieve Plotly charts for a given fraud analytics division.

    Supported divisions:
    - division_1
    - division_2
    - division_3
    """

    data = analytics.get_division_charts_json(division_id)

    return jsonify({
        "success": True,
        "data": data
    })

@app.route("/api/sql/modules", methods=["GET"])
def api_sql_modules():
    """Retrieve all categorized enterprise SQL modules."""

    modules = query_registry.get_all_modules()

    return jsonify({
        "success": True,
        "modules": modules
    })

@app.route("/api/sql/run", methods=["POST"])
def api_sql_run():
    """
    Execute a selected or custom SQL query against MySQL
    and return results with execution metrics.
    """
    payload = request.get_json() or {}

    sql = payload.get("sql", "").strip()
    query_id = payload.get("query_id")

    # If SQL was not directly supplied,
    # retrieve it from the query registry.
    if not sql and query_id:

        q_obj = query_registry.get_query_by_id(query_id)
        if q_obj:
            sql = q_obj["sql"]

    # Reject empty SQL requests.
    if not sql:
        return jsonify({
            "success": False,
            "error": "No SQL query provided."
        }), 400

    result = database.run_query_with_metrics(sql)
    return jsonify(result)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Virtual Avatar conversational endpoint."""

    payload = request.get_json() or {}

    user_msg = payload.get("message", "").strip()

    if not user_msg:
        return jsonify({
            "success": False,
            "reply": "Please provide a question."
        }), 400

    reply = bot.generate_response(user_msg)

    return jsonify({
        "success": True,
        "reply": reply
    })


@app.route("/api/db/status", methods=["GET"])
def api_db_status():
    """Check MySQL database connection status."""
    status_info = database.test_connection()
    return jsonify(status_info)

@app.route("/api/db/config", methods=["POST"])
def api_db_config():
    """
    Update and test MySQL connection credentials dynamically.
    """

    payload = request.get_json() or {}

    host = payload.get("host")
    port = payload.get("port")
    user = payload.get("user")
    password = payload.get("password")
    db_name = payload.get("database")

    database.update_db_config(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name
    )

    status_info = database.test_connection()

    return jsonify(status_info)


if __name__ == "__main__":

    print("=" * 65)
    print("AEGIS FRAUD ANALYTICS DASHBOARD - FLASK BACKEND")
    print("=" * 65)

    print(f"Project Root      : {BASE_DIR}")
    print(f"Template Directory: {TEMPLATE_DIR}")
    print(f"Static Directory  : {STATIC_DIR}")

    print("-" * 65)

    print("Server running at : http://127.0.0.1:5050")
    print("Connected Database: MySQL localhost:3306 [fraud_detection]")

    print("=" * 65)

    app.run(
        host="0.0.0.0",
        port=5050,
        debug=False
    )