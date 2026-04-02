import os
from dotenv import load_dotenv

load_dotenv()


# Configuration minimale partagee par l'application Flask.
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")