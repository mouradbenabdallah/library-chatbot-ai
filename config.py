import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", encoding="utf-8-sig")


# Configuration minimale partagee par l'application Flask.
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
