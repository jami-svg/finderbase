"use client";
import Link from "next/link";

export function Nav() {
  return (
    <div className="w-full border-b p-4 flex gap-4">
      <Link href="/">FinderBase</Link>
      <Link href="/capture">Capture</Link>
      <Link href="/library">Library</Link>
      <Link href="/auth">Auth</Link>
    </div>
  );
}
