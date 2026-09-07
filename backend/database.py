import os
import time
import mysql.connector
from mysql.connector import Error, pooling
import pandas as pd
from backend.config import Config

# Runtime override dictionary for fallback/testing
_RUNTIME_OVERRIDES = {}

def get_db_config():
    """Return dynamic configuration merging Config and runtime overrides."""
    return {
        "host": _RUNTIME_OVERRIDES.get("host") or Config.MYSQL_HOST,
        "port": int(_RUNTIME_OVERRIDES.get("port") or Config.MYSQL_PORT),
        "user": _RUNTIME_OVERRIDES.get("user") or Config.MYSQL_USER,
        "password": _RUNTIME_OVERRIDES.get("password") or Config.MYSQL_PASSWORD,
        "database": _RUNTIME_OVERRIDES.get("database") or Config.MYSQL_DATABASE,
        "autocommit": True
    }

def update_db_config(host=None, port=None, user=None, password=None, database=None):
    """Update runtime database credentials safely."""
    global _RUNTIME_OVERRIDES
    if host is not None:
        _RUNTIME_OVERRIDES["host"] = host
    if port is not None:
        _RUNTIME_OVERRIDES["port"] = int(port)
    if user is not None:
        _RUNTIME_OVERRIDES["user"] = user
    if password is not None:
        _RUNTIME_OVERRIDES["password"] = password
    if database is not None:
        _RUNTIME_OVERRIDES["database"] = database


def get_connection():
    """Create and return a raw MySQL connection."""
    return mysql.connector.connect(**get_db_config())


def test_connection():
    """Test MySQL connection and retrieve metadata."""
    cfg = get_db_config()
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
            "host": cfg["host"],
            "port": cfg["port"],
            "user": cfg["user"],
            "database": db_name or cfg["database"],
            "version": version,
            "tables": tables,
            "error": None
        }
    except Exception as e:
        return {
            "status": "error",
            "host": cfg["host"],
            "port": cfg["port"],
            "user": cfg["user"],
            "database": cfg["database"],
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
