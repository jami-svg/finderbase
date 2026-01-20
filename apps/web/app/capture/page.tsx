"use client";
import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabaseClient";

export default function CapturePage() {
  const [url, setUrl] = useState("https://firecrawl.dev");
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>("");

  async function capture() {
    setError("");
    setStatus("");
    setJobId(null);

    const { data: { session } } = await supabase.auth.getSession();
    const uid = session?.user?.id;
    if (!uid) { setError("Please login first."); return; }

    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/capture`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-user-id": uid },
      body: JSON.stringify({ url })
    });
    if (!res.ok) { setError(await res.text()); return; }
    const json = await res.json();
    setJobId(json.job_id);
    setStatus("queued");
  }

  useEffect(() => {
    if (!jobId) return;
    let timer = setInterval(async () => {
      const { data: { session } } = await supabase.auth.getSession();
      const uid = session?.user?.id;
      if (!uid) return;

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/jobs/${jobId}`, {
        headers: { "x-user-id": uid }
      });
      if (!res.ok) return;
      const job = await res.json();
      setStatus(job.status);
      if (job.status === "failed") setError(job.error || "failed");
      if (job.status === "done" || job.status === "failed") clearInterval(timer);
    }, 1500);

    return () => clearInterval(timer);
  }, [jobId]);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Capture</h1>
      <input className="border p-2 w-full" value={url} onChange={e=>setUrl(e.target.value)} />
      <button className="border px-3 py-2" onClick={capture}>Capture</button>
      {jobId && <p>Job: {jobId}</p>}
      {status && <p>Status: {status}</p>}
      {error && <p className="text-red-600">{error}</p>}
    </div>
  );
}
