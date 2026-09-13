import { useEffect, useState } from "react";
import { getHistory } from "./services/api-client";
import { useScan } from "./hooks/useScan";
import ScanForm from "./components/ScanForm";
import ResultCard from "./components/ResultCard";
import HistoryList from "./components/HistoryList";
import "./global.css";

export default function App() {
  const { result, loading, error, submit } = useScan();
  const [history, setHistory] = useState([]);
  useEffect(() => { getHistory().then((data) => setHistory(data.results || [])).catch(() => setHistory([])); }, [result]);
  return <main className="app-shell"><header className="topbar"><div className="brand"><span className="brand-mark">P</span><span>PhishGuard</span></div><span className="phase-badge">Phase 1 · URL intelligence</span></header><section className="hero"><div className="hero-copy"><p className="eyebrow">Understand the signal</p><h1>Know what is hiding<br /><em>behind the link.</em></h1><p className="hero-text">A practical phishing URL analyzer that turns suspicious patterns into a clear, human-readable explanation.</p></div><div className="scan-panel"><ScanForm onSubmit={submit} loading={loading} />{error && <p className="error-message">{error}</p>}</div></section><section className="results-grid"><ResultCard result={result} /><HistoryList items={history} /></section><footer>PhishGuard uses network-free URL analysis. Predictions are informational and should not replace security controls.</footer></main>;
}
