import { AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react"
import type { ScanResult } from "../lib/api"

export default function ResultCard({ result }: { result: ScanResult }) {
  const isThreat = result.verdict === "phishing"
  const Icon = isThreat ? AlertTriangle : CheckCircle2
  return <section className={`result-card ${isThreat ? "danger" : "safe"}`} aria-live="polite">
    <div className="result-top"><div className="verdict"><Icon size={29}/><div><p className="eyebrow">Scan result</p><h2>{isThreat ? "Potential phishing detected" : "No strong phishing indicators"}</h2></div></div><div className="score"><strong>{result.risk_score}%</strong><span>risk score</span></div></div>
    <p className="checked-url">{result.url}</p>
    <div className="meter"><span style={{ width: `${result.risk_score}%` }} /></div>
    <div className="result-meta"><span>Confidence: <b>{Math.round(result.confidence * 100)}%</b></span><span>Category: <b>{result.category}</b></span></div>
    <div className="explanation"><h3><ShieldAlert size={18}/> Why this result?</h3>{result.explanations.map((item, index) => <article key={index}><div><b>{item.feature}</b><p>{item.reason}</p></div>{item.impact > 0 && <span className="impact">+{item.impact}</span>}</article>)}</div>
    <p className="model-note">Analysis: {result.model_used}. This tool supports decisions; it cannot guarantee that a site is safe.</p>
  </section>
}
