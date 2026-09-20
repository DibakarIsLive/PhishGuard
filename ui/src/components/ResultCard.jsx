const verdictMeta = {
  phishing: {
    badge: "High risk",
    title: "This link deserves caution.",
    summary: "The URL contains patterns commonly associated with phishing attempts.",
    tone: "danger",
    symbol: "!",
  },
  suspicious: {
    badge: "Needs review",
    title: "Take a closer look.",
    summary: "The URL has signals that deserve a careful manual review.",
    tone: "warning",
    symbol: "?",
  },
  legitimate: {
    badge: "No obvious structural red flags",
    title: "No obvious structural red flags found.",
    summary: "The URL looks structurally ordinary, but this analysis is not a safety guarantee.",
    tone: "safe",
    symbol: "✓",
  },
};

function getConfidence(result) {
  const value = Number(result?.confidence);
  if (!Number.isFinite(value)) return 0;
  return Math.round(Math.max(0, Math.min(1, value)) * 100);
}

export default function ResultCard({ result, animationKey = 0 }) {
  if (!result) {
    return (
      <section className="empty-state" key="empty" aria-live="polite">
        <div className="empty-state-icon" aria-hidden="true">⌁</div>
        <p className="eyebrow">Waiting for a URL</p>
        <h2>Your analysis will appear here.</h2>
        <p>Submit an address to see its verdict, confidence, and contributing signals.</p>
        <span className="empty-state-line" aria-hidden="true" />
      </section>
    );
  }

  const verdict = String(result.verdict || "suspicious").toLowerCase();
  const meta = verdictMeta[verdict] || verdictMeta.suspicious;
  const confidence = getConfidence(result);
  const reasons = Array.isArray(result.explanations?.reasons)
    ? result.explanations.reasons
    : [];
  const featureCount = Object.keys(result.features || {}).length;

  return (
    <section className={`result-card result-card--${meta.tone}`} key={`result-${animationKey}`} aria-live="polite">
      <div className="result-topline">
        <div>
          <p className="eyebrow">Latest analysis</p>
          <span className={`verdict-badge verdict-badge--${meta.tone}`}>
            <span aria-hidden="true">{meta.symbol}</span>{meta.badge}
          </span>
        </div>
        <div
          className="confidence-ring"
          style={{ "--confidence": `${confidence * 3.6}deg` }}
          aria-label={`${confidence}% confidence`}
        >
          <strong>{confidence}<small>%</small></strong>
          <span>confidence</span>
        </div>
      </div>

      <div className="result-summary">
        <span className="result-symbol" aria-hidden="true">{meta.symbol}</span>
        <div>
          <h2>{meta.title}</h2>
          <p>{meta.summary}</p>
        </div>
      </div>

      <div className="confidence-track" aria-hidden="true">
        <span style={{ width: `${confidence}%` }} />
      </div>

      <div className="url-detail">
        <span className="detail-label">URL analyzed</span>
        <code>{result.url}</code>
      </div>

      <div className="result-stats">
        <div>
          <span className="detail-label">Verdict</span>
          <strong>{meta.badge}</strong>
        </div>
        <div>
          <span className="detail-label">Signals checked</span>
          <strong>{featureCount || "—"}</strong>
        </div>
      </div>

      <div className="reasons">
        <div className="reasons-heading">
          <div>
            <p className="eyebrow">The why</p>
            <h3>Signals behind this result</h3>
          </div>
          <span>{reasons.length.toString().padStart(2, "0")}</span>
        </div>
        {reasons.length > 0 ? (
          <ul>
            {reasons.map((reason, index) => (
              <li key={`${reason}-${index}`}>
                <span className="reason-index">0{index + 1}</span>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">No detailed signal notes were returned for this analysis.</p>
        )}
      </div>
    </section>
  );
}
