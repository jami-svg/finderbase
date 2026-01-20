from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from .db import supabase

app = FastAPI(title="FinderBase API")

class CaptureIn(BaseModel):
    url: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/capture")
def capture(body: CaptureIn, x_user_id: str = Header(default=None)):
    """
    Consumer product:
    - frontend sends x-user-id (Supabase auth.uid())
    - we create a job for worker
    """
    if not x_user_id:
        raise HTTPException(401, "Missing x-user-id header")
    url = body.url.strip()
    if not url.startswith("http"):
        raise HTTPException(400, "URL must start with http/https")

    job = supabase.table("scrape_jobs").insert({
        "user_id": x_user_id,
        "url": url,
        "status": "queued",
    }).execute()

    return {"job_id": job.data[0]["id"]}

@app.get("/jobs/{job_id}")
def job_status(job_id: str, x_user_id: str = Header(default=None)):
    if not x_user_id:
        raise HTTPException(401, "Missing x-user-id header")

    res = supabase.table("scrape_jobs")\
        .select("*")\
        .eq("id", job_id)\
        .eq("user_id", x_user_id)\
        .maybe_single()\
        .execute()

    if not res.data:
        raise HTTPException(404, "Job not found")

    return res.data
