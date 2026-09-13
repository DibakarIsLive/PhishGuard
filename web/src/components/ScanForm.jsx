import { useState } from "react";

export default function ScanForm({ onSubmit, loading }) {
  const [url, setUrl] = useState("");
  function handleSubmit(event) { event.preventDefault(); if (url.trim()) onSubmit(url.trim()); }
  return <form className="scan-form" onSubmit={handleSubmit}>
    <label htmlFor="url">Paste a URL to analyze</label>
    <div className="input-row"><input id="url" value={url} onChange={(event) => setUrl(event.target.value)} placeholder="https://example.com/login" type="url" required /><button disabled={loading}>{loading ? "Analyzing…" : "Analyze URL"}</button></div>
    <small>PhishGuard analyzes URL characteristics locally; it does not visit the submitted website.</small>
  </form>;
}
