export default function Home() {
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Save the web. Search it later.</h1>
      <p>Paste a URL. Get a clean readable version + screenshot. Build your personal library.</p>
      <div className="space-x-3">
        <a className="underline" href="/capture">Start capturing</a>
        <a className="underline" href="/library">View library</a>
      </div>
    </div>
  );
}
