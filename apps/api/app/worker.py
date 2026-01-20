import asyncio
from datetime import datetime
from .db import supabase
from .settings import settings
from .scrape import scrape_one
from .storage import upload_screenshot

async def process_job(job):
    job_id = job["id"]
    user_id = job["user_id"]
    url = job["url"]

    # Mark running
    supabase.table("scrape_jobs").update({
        "status": "running",
        "started_at": datetime.utcnow().isoformat()
    }).eq("id", job_id).execute()

    try:
        page, screenshot = await scrape_one(url)

        # Upsert page row
        # screenshot path: <user_id>/<page_id>.png
        # Use scraped_pages unique (user_id,url) to upsert safely
        up = supabase.table("scraped_pages").upsert({
            "user_id": user_id,
            "url": page.url,
            "domain": page.domain,
            "scraped_at": datetime.utcnow().isoformat(),
            "title": page.title,
            "summary": page.summary,
            "markdown": page.markdown,
            "company_name": page.company_name,
            "language": page.language,
            "status_code": page.status_code,
            "seo": page.seo.model_dump(),
            "contacts": page.contacts.model_dump(),
            "socials": page.socials.model_dump(),
        }, on_conflict="user_id,url").execute()

        page_id = up.data[0]["id"]
        screenshot_path = f"{user_id}/{page_id}.png"
        upload_screenshot(screenshot_path, screenshot, "image/png")

        # update page with screenshot_path
        supabase.table("scraped_pages").update({
            "screenshot_path": screenshot_path
        }).eq("id", page_id).execute()

        supabase.table("scrape_jobs").update({
            "status": "done",
            "finished_at": datetime.utcnow().isoformat()
        }).eq("id", job_id).execute()

    except Exception as e:
        supabase.table("scrape_jobs").update({
            "status": "failed",
            "error": str(e),
            "finished_at": datetime.utcnow().isoformat()
        }).eq("id", job_id).execute()

async def loop():
    while True:
        res = supabase.table("scrape_jobs")\
            .select("*")\
            .eq("status", "queued")\
            .order("created_at", desc=False)\
            .limit(1)\
            .execute()

        if res.data:
            await process_job(res.data[0])
        else:
            await asyncio.sleep(settings.WORKER_POLL_SECONDS)

if __name__ == "__main__":
    asyncio.run(loop())
