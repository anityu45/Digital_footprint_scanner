import os
from dotenv import load_dotenv

load_dotenv()

# JWT
SECRET_KEY: str = os.getenv("SECRET_KEY", "your-very-secret-key-is-not-safe-in-code")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7  

# MySQL
DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
DB_USER: str = os.getenv("DB_USER", "root")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root@123")
DB_NAME: str = os.getenv("DB_NAME", "osint_db")

# Redis / Celery
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# OSINT External Config (Zero Hardcoding)
XON_API_KEY: str = os.getenv("XON_API_KEY", "")
SHERLOCK_URL: str = os.getenv("SHERLOCK_DATA_URL", "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock_project/resources/data.json")

# FIXED: Default limit changed to 500 so it checks all sites (including GitHub) instead of stopping at 'C'
SHERLOCK_SITE_LIMIT: int = int(os.getenv("SHERLOCK_SITE_LIMIT", "500"))

# App
ENV: str = os.getenv("ENV", "development").strip().lower()
ALLOWED_ORIGINS: list[str] = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8501"
).split(",")