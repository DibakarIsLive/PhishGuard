import { useState } from "react";
import { scanUrl } from "../services/api-client";

export function useScan() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(url) {
    setLoading(true); setError("");
    try { const data = await scanUrl(url); setResult(data); return data; }
    catch (err) { setError(err.message); throw err; }
    finally { setLoading(false); }
  }
  return { result, loading, error, submit };
}
