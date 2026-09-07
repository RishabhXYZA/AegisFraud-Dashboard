import os

from flask import Flask, render_template, jsonify, request

from backend.config import Config
from backend import database
from backend import query_registry
from backend import analytics
from backend.chatbot_engine import bot

BASE_DIR = os.path.dirname(
os.path.dirname(
        os.path.abspath(__file__)
    )
)

TEMPLATE_DIR = os.path.join(BASE_DIR,"templates")
STATIC_DIR = os.path.join(BASE_DIR,"static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

app.config.from_object(Config)


@app.route("/")
def index():
    """
    Render the main AegisFraud dashboard.
    """

    return render_template(
        "index.html"
    )

@app.route(
    "/api/kpis",
    methods=["GET"]
)
def api_kpis():
    """
    Retrieve top executive KPI metrics.
    """

    data = analytics.get_kpi_metrics()

    return jsonify({
        "success": True,
        "data": data
    })

@app.route(
    "/api/overview",
    methods=["GET"]
)
def api_overview():
    """
    Retrieve executive overview data
    and workflow information.
    """

    data = analytics.get_overview_data()

    return jsonify({
        "success": True,
        "data": data
    })

@app.route(
    "/api/insights",
    methods=["GET"]
)
def api_insights():
    """
    Retrieve executive business
    intelligence insights.
    """

    data = analytics.get_executive_insights_data()

    return jsonify({
        "success": True,
        "data": data
    })

@app.route(
    "/api/charts/division/<division_id>",
    methods=["GET"]
)
def api_charts_division(division_id):
    """
    Retrieve Plotly charts for a given
    fraud analytics division.

    Supported divisions:

    - division_1
    - division_2
    - division_3
    """

    data = analytics.get_division_charts_json(
        division_id
    )

    return jsonify({
        "success": True,
        "data": data
    })

@app.route(
    "/api/sql/modules",
    methods=["GET"]
)
def api_sql_modules():
    """
    Retrieve all categorized enterprise
    SQL modules from query_registry.py.
    """

    modules = query_registry.get_all_modules()

    return jsonify({
        "success": True,
        "modules": modules
    })

@app.route(
    "/api/sql/run",
    methods=["POST"]
)
def api_sql_run():
    """
    Execute read-only SQL queries.

    The SQL Explorer is allowed to execute
    SELECT and WITH queries.

    Complex analytical queries are supported,
    including:

    - CASE
    - JOIN
    - GROUP BY
    - ORDER BY
    - COUNT
    - SUM
    - AVG
    - ROUND
    - DISTINCT
    - Subqueries
    - CTEs using WITH

    Dangerous write/destructive operations
    are blocked.
    """

    # --------------------------------------------------------
    # Read request payload
    # --------------------------------------------------------

    payload = request.get_json(
        silent=True
    ) or {}

    sql = payload.get(
        "sql",
        ""
    ).strip()

    # --------------------------------------------------------
    # Reject empty SQL
    # --------------------------------------------------------

    if not sql:

        return jsonify({
            "success": False,
            "error": "No SQL query provided."
        }), 400

    # --------------------------------------------------------
    # Normalize SQL for security validation
    # --------------------------------------------------------

    normalized_sql = sql.strip()

    # --------------------------------------------------------
    # Remove leading SQL line comments
    # --------------------------------------------------------

    while normalized_sql.startswith("--"):

        newline_position = (
            normalized_sql.find("\n")
        )

        if newline_position == -1:

            return jsonify({
                "success": False,
                "error": "Invalid SQL query."
            }), 400

        normalized_sql = normalized_sql[
            newline_position + 1:
        ].strip()

    # --------------------------------------------------------
    # Remove leading SQL block comments
    # --------------------------------------------------------

    while normalized_sql.startswith("/*"):

        comment_end = (
            normalized_sql.find("*/")
        )

        if comment_end == -1:

            return jsonify({
                "success": False,
                "error": "Invalid SQL query."
            }), 400

        normalized_sql = normalized_sql[
            comment_end + 2:
        ].strip()

    # --------------------------------------------------------
    # Reject empty query after comments
    # --------------------------------------------------------

    if not normalized_sql:

        return jsonify({
            "success": False,
            "error": "Invalid SQL query."
        }), 400

    sql_upper = normalized_sql.upper()

    # ========================================================
    # MULTIPLE STATEMENT PROTECTION
    # ========================================================

    """
    Prevent queries such as:

        SELECT * FROM users;
        DROP TABLE users;

    Only one SQL statement is allowed.
    """

    statements = [
        statement.strip()
        for statement
        in normalized_sql.split(";")
        if statement.strip()
    ]

    if len(statements) > 1:

        return jsonify({
            "success": False,
            "error": (
                "Multiple SQL statements are "
                "not allowed."
            )
        }), 403

    # ========================================================
    # READ-ONLY QUERY PROTECTION
    # ========================================================

    """
    Only SELECT and WITH queries are allowed.

    This means analytical queries such as:

        SELECT
            CASE ...
            COUNT(...)
            SUM(...)
        FROM ...
        JOIN ...
        GROUP BY ...
        ORDER BY ...

    are completely valid.
    """

    is_select_query = (
        sql_upper == "SELECT"
        or sql_upper.startswith("SELECT ")
        or sql_upper.startswith("SELECT\n")
    )

    is_with_query = (
        sql_upper == "WITH"
        or sql_upper.startswith("WITH ")
        or sql_upper.startswith("WITH\n")
    )

    if not (
        is_select_query
        or is_with_query
    ):

        return jsonify({
            "success": False,
            "error": (
                "Only read-only SELECT "
                "queries are allowed."
            )
        }), 403

    # ========================================================
    # DANGEROUS SQL KEYWORD PROTECTION
    # ========================================================

    """
    Additional protection against database
    modification or administrative commands.

    These operations are not permitted through
    the public SQL Explorer.
    """

    forbidden_keywords = [
        "INSERT ",
        "UPDATE ",
        "DELETE ",
        "DROP ",
        "ALTER ",
        "TRUNCATE ",
        "CREATE ",
        "RENAME ",
        "GRANT ",
        "REVOKE ",
        "REPLACE ",
        "CALL ",
        "LOAD ",
        "LOCK ",
        "UNLOCK ",
        "FLUSH ",
        "KILL ",
        "SET "
    ]

    for keyword in forbidden_keywords:

        if keyword in sql_upper:

            return jsonify({
                "success": False,
                "error": (
                    "This SQL operation is "
                    "not allowed. Only "
                    "read-only queries can "
                    "be executed."
                )
            }), 403

    # ========================================================
    # EXECUTE SAFE READ-ONLY QUERY
    # ========================================================

    result = database.run_query_with_metrics(
        sql
    )

    return jsonify(result)

@app.route(
    "/api/chat",
    methods=["POST"]
)
def api_chat():
    """
    Aegis AI conversational endpoint.

    Supports:
    - General fraud questions
    - Dashboard analytics questions
    - Graph/chart analysis
    - Executive insights
    - Optional SQL Explorer query/result explanation
    """

    payload = request.get_json(silent=True) or {}

    # --------------------------------------------------------
    # Read user message
    # --------------------------------------------------------

    user_msg = payload.get("message","").strip()

    # --------------------------------------------------------
    # Optional SQL Explorer context
    # --------------------------------------------------------

    sql_query = payload.get("sql_query","")

    sql_result = payload.get("sql_result","")

    # --------------------------------------------------------
    # Reject empty messages
    # --------------------------------------------------------

    if not user_msg:

        return jsonify({
            "success": False,
            "reply": "Please provide a question."
        }), 400

    # --------------------------------------------------------
    # Generate chatbot response
    # --------------------------------------------------------

    reply = bot.generate_response(
        user_message=user_msg,
        sql_query=sql_query,
        sql_result=sql_result
    )

    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return jsonify({
        "success": True,
        "reply": reply
    })

@app.route(
    "/api/db/status",
    methods=["GET"]
)
def api_db_status():
    """
    Check MySQL database connection status.

    This endpoint can check the database,
    but it cannot modify database configuration.
    """

    status_info = database.test_connection()

    return jsonify(
        status_info
    )

@app.route(
    "/api/db/config",
    methods=["POST"]
)
def api_db_config():
    """
    Database configuration changes are disabled.

    Database credentials are loaded from the
    local .env configuration.

    Public users cannot change:

    - Host
    - Port
    - Username
    - Password
    - Database
    """

    return jsonify({
        "success": False,
        "error": (
            "Database configuration changes "
            "are disabled."
        )
    }), 403

if __name__ == "__main__":
    print("=" * 65)
    print("AEGIS FRAUD ANALYTICS DASHBOARD - ""FLASK BACKEND")

    print("=" * 65)
    print(f"Project Root      : {BASE_DIR}")
    print(f"Template Directory: {TEMPLATE_DIR}")
    print(f"Static Directory  : {STATIC_DIR}")
    print("-" * 65)
    print("Server running at : ""http://127.0.0.1:5050")

    print(
        f"Connected Database: "
        f"{Config.MYSQL_HOST}:"
        f"{Config.MYSQL_PORT} "
        f"[{Config.MYSQL_DATABASE}]"
    )
    print("=" * 65)

    app.run(
        host="0.0.0.0",
        port=5050,
        debug=False
    )