import os
import time
import mysql.connector
from mysql.connector import Error, pooling
import pandas as pd
from backend.config import Config

# Path to Aiven MySQL CA certificate
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CA_CERT_PATH = os.path.join(BASE_DIR, "certificates", "aiven-ca.pem")


# Global active configuration
DB_CONFIG = {
    "host": Config.MYSQL_HOST,
    "port": Config.MYSQL_PORT,
    "user": Config.MYSQL_USER,
    "password": Config.MYSQL_PASSWORD,
    "database": Config.MYSQL_DATABASE,
    "autocommit": True
}


def update_db_config(host=None, port=None, user=None, password=None, database=None):
    """Update runtime database credentials."""
    global DB_CONFIG
    if host is not None:
        DB_CONFIG["host"] = host
    if port is not None:
        DB_CONFIG["port"] = int(port)
    if user is not None:
        DB_CONFIG["user"] = user
    if password is not None:
        DB_CONFIG["password"] = password
    if database is not None:
        DB_CONFIG["database"] = database


def get_connection():
    """Create and return a raw MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


def test_connection():
    """Test MySQL connection and retrieve metadata."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION(), DATABASE();")
        version, db_name = cursor.fetchone()

        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()
        return {
            "status": "connected",
            "host": DB_CONFIG["host"],
            "port": DB_CONFIG["port"],
            "user": DB_CONFIG["user"],
            "database": db_name or DB_CONFIG["database"],
            "version": version,
            "tables": tables,
            "error": None
        }
    except Exception as e:
        return {
            "status": "error",
            "host": DB_CONFIG["host"],
            "port": DB_CONFIG["port"],
            "user": DB_CONFIG["user"],
            "database": DB_CONFIG["database"],
            "version": None,
            "tables": [],
            "error": str(e)
        }


def run_query(sql, params=None):
    """Execute a query and return a pandas DataFrame."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=columns)
        else:
            df = pd.DataFrame()
        cursor.close()
        return df
    finally:
        conn.close()


def run_query_with_metrics(sql, params=None, max_rows=1000):
    """
    Execute a query for the SQL Query Explorer.
    Returns: { columns, rows, row_count, execution_time_ms, truncated }
    """
    start_time = time.time()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Clean query: strip multiple USE statements if present or handle multiple statements
        statements = [s.strip() for s in sql.strip().split(';') if s.strip()]

        last_description = None
        rows = []
        for stmt in statements:
            if stmt.upper().startswith("USE "):
                continue
            cursor.execute(stmt, params or ())
            if cursor.description:
                last_description = cursor.description
                rows = cursor.fetchall()

        execution_time_ms = round((time.time() - start_time) * 1000, 2)

        if last_description:
            columns = [col[0] for col in last_description]
            total_count = len(rows)
            truncated = total_count > max_rows

            # Format row data safely for JSON serialization
            serialized_rows = []
            for r in rows[:max_rows]:
                row_dict = {}
                for col_name, val in zip(columns, r):
                    if isinstance(val, (int, float, str, bool)) or val is None:
                        row_dict[col_name] = val
                    else:
                        row_dict[col_name] = str(val)
                serialized_rows.append(row_dict)

            cursor.close()
            return {
                "success": True,
                "columns": columns,
                "rows": serialized_rows,
                "row_count": total_count,
                "displayed_count": len(serialized_rows),
                "execution_time_ms": execution_time_ms,
                "truncated": truncated,
                "error": None
            }
        else:
            cursor.close()
            return {
                "success": True,
                "columns": ["Result"],
                "rows": [{"Result": f"Query executed successfully ({cursor.rowcount} rows affected)."}],
                "row_count": cursor.rowcount,
                "displayed_count": 1,
                "execution_time_ms": execution_time_ms,
                "truncated": False,
                "error": None
            }
    except Exception as e:
        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "displayed_count": 0,
            "execution_time_ms": execution_time_ms,
            "truncated": False,
            "error": str(e)
        }
    finally:
        conn.close()
