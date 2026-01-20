import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_SCREENSHOTS_BUCKET = os.getenv("SUPABASE_SCREENSHOTS_BUCKET", "screenshots")

    WORKER_POLL_SECONDS = int(os.getenv("WORKER_POLL_SECONDS", "2"))
    SCRAPE_TIMEOUT_MS = int(os.getenv("SCRAPE_TIMEOUT_MS", "25000"))
    MAX_HTML_BYTES = int(os.getenv("MAX_HTML_BYTES", "3000000"))

settings = Settings()
