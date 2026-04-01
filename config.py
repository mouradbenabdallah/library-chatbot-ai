import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://mourad:mourad123@localhost/library_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
```

**`.env`** ← mets tes vraies infos PostgreSQL
```
DATABASE_URL=postgresql://ton_user:ton_password@localhost/library_db
SECRET_KEY=change-this-in-production