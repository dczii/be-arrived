import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    environment = os.getenv("ENVIRONMENT", "development")
    port = int(os.getenv("PORT", 8000))
    intercom_access_token = os.getenv("INTERCOM_ACCESS_TOKEN", "")


env = Settings()
