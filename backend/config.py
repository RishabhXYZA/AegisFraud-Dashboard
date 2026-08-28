import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class Config:
    # MySQL Database Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Cos^2@+Sin^2@=1")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "fraud_detection")

    # App Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "fraud_detection_secret_key_2026")
    JSON_SORT_KEYS = False
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")