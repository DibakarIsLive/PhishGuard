import { useEffect, useState } from "react";
import { getHistory } from "./services/api-client";
import { useScan } from "./hooks/useScan";
import ScanForm from "./components/ScanForm";
import ResultCard from "./components/ResultCard";
import HistoryList from "./components/HistoryList";
import "./global.css";

const featureHighlights = [
  {
    icon: "◌",
    title: "No page visits",
    text: "Analyze the address without opening it.",
  },
  {
    icon: "✦",
    title: "Explainable signals",
    text: "See the patterns behind every verdict.",
  },
  {
    icon: "↗",
    title: "Fast first pass",
    text: "Get a practical answer in seconds.",
  },
];

export default function App() {
  const { result, loading, error, submit } = useScan();
  const [history, setHistory] = useState([]);
  const [scanVersion, setScanVersion] = useState(0);

  async function handleSubmit(url) {
    const data = await submit(url);
    setScanVersion((version) => version + 1);
    return data;
  }

  useEffect(() => {
    let mounted = true;

    getHistory()
      .then((data) => {
        if (mounted) setHistory(data.results || []);
      })
      .catch(() => {
        if (mounted && !result) setHistory([]);
      });

    return () => {
      mounted = false;
    };
  }, [result]);

  return (
    <main className="app-shell">
      <div className="ambient-orb ambient-orb--blue" aria-hidden="true" />
      <div className="ambient-orb ambient-orb--mint" aria-hidden="true" />

      <header className="topbar">
        <a className="brand" href="#top" aria-label="PhishGuard home">
          <span className="brand-logo">
            <img src="/phishguard-shield-logo.png" alt="" />
          </span>
          <span className="brand-copy">
            <strong>PhishGuard</strong>
            <small>Explainable URL intelligence</small>
          </span>
        </a>

        <div className="topbar-meta">
          <span className="status-pill">
            <span className="status-dot" aria-hidden="true" />
            Network-free checks
          </span>
          <span className="phase-badge">
            Phase 1 <span>/</span> URL intelligence
          </span>
        </div>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="hero-kicker">
            <span aria-hidden="true" /> Practical phishing defense
          </p>
          <h1>
            See the signal
            <br />
            <em>before you click.</em>
          </h1>
          <p className="hero-text">
            PhishGuard turns the structure of a suspicious URL into a clear,
            human-readable second opinion—without visiting the website behind
            it.
          </p>

          <div className="hero-actions">
            <a className="text-link" href="#scan">
              Start an analysis <span aria-hidden="true">↓</span>
            </a>
            <span className="hero-divider" aria-hidden="true" />
            <span className="hero-caption">Built for careful decisions</span>
          </div>
        </div>

        <div className="scan-panel" id="scan">
          <div className="scan-panel-shine" aria-hidden="true" />
          <div className="scan-panel-header">
            <div>
              <p className="eyebrow">Start with the address</p>
              <h2>What should we inspect?</h2>
            </div>
            <span className="panel-icon" aria-hidden="true">
              ⌁
            </span>
          </div>
          <ScanForm onSubmit={handleSubmit} loading={loading} />
          {error && (
            <p className="error-message" role="alert">
              <span aria-hidden="true">!</span>
              {error}
            </p>
          )}
          <div className="scan-panel-note">
            <span className="note-icon" aria-hidden="true">
              ⌁
            </span>
            <span>
              Only URL characteristics are evaluated. PhishGuard never opens the
              submitted page.
            </span>
          </div>
        </div>
      </section>

      <section className="feature-strip" aria-label="PhishGuard capabilities">
        {featureHighlights.map((item) => (
          <div className="feature-item" key={item.title}>
            <span className="feature-icon" aria-hidden="true">
              {item.icon}
            </span>
            <div>
              <strong>{item.title}</strong>
              <p>{item.text}</p>
            </div>
          </div>
        ))}
      </section>

      <section className="workspace-section" id="results">
        <div className="section-intro">
          <div>
            <p className="eyebrow">Your analysis workspace</p>
            <h2>Evidence over guesswork.</h2>
          </div>
          <p className="section-description">
            Each result pairs a straightforward verdict with the URL signals
            that shaped it.
          </p>
        </div>

        <div className="results-grid">
          <ResultCard result={result} animationKey={scanVersion} />
          <HistoryList items={history} />
        </div>
      </section>

      <footer className="site-footer">
        <div className="footer-brand">
          <img src="/phishguard-shield-logo.png" alt="" />
          <span>PhishGuard</span>
        </div>
        <p>
          Informational URL analysis for safer decisions. Always verify
          important links independently.
        </p>
        <span className="footer-mark">PG / 01</span>
      </footer>
    </main>
  );
}
