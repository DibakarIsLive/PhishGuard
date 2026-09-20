import { useRef, useState } from "react";

export default function ScanForm({ onSubmit, loading }) {
  const [url, setUrl] = useState("");
  const inputRef = useRef(null);

  async function handlePasteFromClipboard() {
    if (!navigator.clipboard?.readText) return;

    try {
      const clipboardText = await navigator.clipboard.readText();
      const value = clipboardText.trim();
      if (!value) return;

      setUrl(value);
      inputRef.current?.focus();
      inputRef.current?.setSelectionRange(value.length, value.length);
    } catch {
      // Clipboard access can be denied by the browser or unavailable outside a secure context.
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    const value = url.trim();
    if (!value || loading) return;

    const request = onSubmit(value);
    if (request?.catch) request.catch(() => {});
  }

  return (
    <form
      className="scan-form"
      onSubmit={handleSubmit}
      aria-label="Analyze a URL"
    >
      <label htmlFor="url">Paste a URL to analyze</label>
      <div className="input-row">
        <button
          className="input-prefix"
          type="button"
          onClick={handlePasteFromClipboard}
          aria-label="Paste the last copied text from the clipboard"
          title="Paste from clipboard"
        >
          <span aria-hidden="true">↗</span>
        </button>
        <input
          ref={inputRef}
          id="url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="example.com/login"
          type="text"
          inputMode="url"
          autoComplete="off"
          spellCheck="false"
          required
          aria-label="Website URL"
        />
        <button
          type="submit"
          disabled={loading || !url.trim()}
          aria-busy={loading}
        >
          <span>{loading ? "Reading signal" : "Analyze URL"}</span>
          <span className="button-arrow" aria-hidden="true">
            →
          </span>
        </button>
      </div>
      <small className="form-helper">
        <span className="helper-lock" aria-hidden="true">
          ✦
        </span>
        Try a full address or just a domain. We normalize it before analysis.
      </small>
    </form>
  );
}
