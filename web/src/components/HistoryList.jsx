const verdictLabels = {
  phishing: "High risk",
  suspicious: "Review",
  legitimate: "Likely safe",
};

function formatDate(value) {
  if (!value) return "Date unavailable";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Date unavailable";
  return date.toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}

export default function HistoryList({ items }) {
  return (
    <section className="history">
      <div className="section-heading">
        <div>
          <p className="eyebrow">A quick trail</p>
          <h2>Recent scans</h2>
        </div>
        <span className="history-count">{items.length.toString().padStart(2, "0")} saved</span>
      </div>

      {items.length === 0 ? (
        <div className="history-empty">
          <span className="history-empty-icon" aria-hidden="true">◌</span>
          <h3>Your scan trail is clear.</h3>
          <p>Completed checks will appear here when the history service is available.</p>
        </div>
      ) : (
        <div className="history-list" aria-live="polite">
          {items.map((item, index) => {
            const verdict = String(item.verdict || "suspicious").toLowerCase();
            return (
              <div className="history-item" key={item.id || `${item.url}-${index}`}>
                <span className={`history-status history-status--${verdict}`} aria-hidden="true">
                  {verdict === "phishing" ? "!" : verdict === "legitimate" ? "✓" : "?"}
                </span>
                <div className="history-item-copy">
                  <strong title={item.url}>{item.url}</strong>
                  <small>{formatDate(item.created_at)}</small>
                </div>
                <span className={`history-verdict history-verdict--${verdict}`}>
                  {verdictLabels[verdict] || "Review"}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
