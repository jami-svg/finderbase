"use client";
import { useState } from "react";
import { supabase } from "@/lib/supabaseClient";

export default function AuthPage() {
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");

  async function signIn() {
    setMsg("");
    const { error } = await supabase.auth.signInWithOtp({ email });
    if (error) setMsg(error.message);
    else setMsg("Check your email for the login link.");
  }

  async function signOut() {
    await supabase.auth.signOut();
    setMsg("Signed out.");
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Login</h1>
      <input className="border p-2 w-full" placeholder="you@domain.com" value={email} onChange={e=>setEmail(e.target.value)} />
      <button className="border px-3 py-2" onClick={signIn}>Send magic link</button>
      <button className="border px-3 py-2" onClick={signOut}>Sign out</button>
      {msg && <p>{msg}</p>}
    </div>
  );
}
