from .db import supabase
from .settings import settings

def upload_screenshot(path: str, content: bytes, content_type: str = "image/png"):
    # path example: f"{user_id}/{page_id}.png"
    bucket = settings.SUPABASE_SCREENSHOTS_BUCKET
    supabase.storage.from_(bucket).upload(
        path=path,
        file=content,
        file_options={"content-type": content_type, "upsert": "true"},
    )
    return path

def create_signed_url(path: str, expires_in: int = 3600) -> str:
    bucket = settings.SUPABASE_SCREENSHOTS_BUCKET
    res = supabase.storage.from_(bucket).create_signed_url(path, expires_in)
    return res.get("signedURL")
