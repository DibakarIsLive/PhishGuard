const labels = { phishing: "High risk", suspicious: "Needs review", legitimate: "Likely safe" };

export default function ResultCard({ result }) {
  if (!result) return <section className="empty-state"><span>◈</span><h2>Your analysis will appear here</h2><p>Submit a URL to see its verdict, confidence, and contributing signals.</p></section>;
  return <section className={`result-card ${result.verdict}`}><div className="result-heading"><div><p className="eyebrow">Analysis result</p><h2>{labels[result.verdict]}</h2></div><strong>{Math.round(result.confidence * 100)}%</strong></div><p className="scanned-url">{result.url}</p><div className="reasons"><h3>What influenced this result</h3><ul>{result.explanations.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul></div></section>;
}
