import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from core.config import settings

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / "app.log"

file_handler = RotatingFileHandler(
    log_file, maxBytes=5_000_000, backupCount=5, encoding="utf-8"
)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
file_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

missing_env = []
if not settings.DATABASE_URL:
    missing_env.append("DATABASE_URL")
if not settings.GROK_API_URL:
    missing_env.append("GROK_API_URL")
if missing_env:
    logger.error(f"Missing critical environment variables: {', '.join(missing_env)}")
