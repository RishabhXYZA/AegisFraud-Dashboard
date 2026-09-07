import os
from dotenv import load_dotenv

# Project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Load .env from project root
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:

    # ============================================================
    # MySQL Database Configuration
    # ============================================================
    MYSQL_HOST = os.getenv("MYSQL_HOST", "")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "49188"))
    MYSQL_USER = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "fraud_detection")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


    # ============================================================
    # Flask Application Settings
    # ============================================================
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    JSON_SORT_KEYS = False
    DEBUG = os.getenv("DEBUG","False").lower() in ("true", "1")