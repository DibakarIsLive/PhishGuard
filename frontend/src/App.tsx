import { FormEvent, useEffect, useState } from "react"
import { Activity, ArrowRight, Clock3, LoaderCircle, ScanSearch, ShieldCheck, ShieldX } from "lucide-react"
import ResultCard from "./components/ResultCard"
import { checkUrl, getHistory, type ScanResult } from "./lib/api"

const examples = ["https://www.google.com", "http://192.168.1.10/secure-login/verify-account", "https://paypal-account-verify.xyz/signin"]
export default function App() {
  const [url, setUrl] = useState("")
  const [result, setResult] = useState<ScanResult | null>(null)
  const [history, setHistory] = useState<ScanResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const loadHistory = () => getHistory().then(setHistory).catch(() => undefined)
  useEffect(() => { void loadHistory() }, [])
  async function scan(event: FormEvent) {
    event.preventDefault(); setError(""); setResult(null)
    if (!url.trim()) { setError("Paste or type a website address first."); return }
    setLoading(true)
    try { setResult(await checkUrl(url)); loadHistory() } catch (err) { setError(err instanceof Error ? err.message : "The scan could not be completed.") } finally { setLoading(false) }
  }
  return <main>
    <nav><a className="brand" href="#top"><ShieldCheck size={26}/><span>Phish<span>Guard</span></span></a><div><a href="#scanner">Scanner</a><a href="#how">How it works</a></div></nav>
    <header id="top" className="hero"><div className="pill"><Activity size={15}/> Explainable phishing detection</div><h1>Know where a link leads<br/><em>before you trust it.</em></h1><p>PhishGuard examines suspicious URL patterns in seconds and shows the reasons behind every risk score.</p><a className="primary-link" href="#scanner">Check a URL <ArrowRight size={18}/></a><div className="trust-row"><span><ShieldCheck/> Private analysis</span><span><Activity/> Instant results</span><span><ScanSearch/> Clear explanations</span></div></header>
    <section id="scanner" className="scanner-wrap"><div className="section-title"><p className="eyebrow">URL security scan</p><h2>Paste a link. Get an explanation.</h2></div><form onSubmit={scan}><label htmlFor="url">Website address</label><div className="input-row"><input id="url" value={url} onChange={event => setUrl(event.target.value)} placeholder="https://example.com/login" autoComplete="off"/><button disabled={loading}>{loading ? <LoaderCircle className="spin"/> : <ScanSearch/>}{loading ? "Analyzing" : "Analyze URL"}</button></div>{error && <p className="error" role="alert">{error}</p>}</form><div className="examples"><span>Try an example:</span>{examples.map(example => <button key={example} onClick={() => { setUrl(example); setResult(null) }}>{example.replace("https://", "").replace("http://", "")}</button>)}</div>{result && <ResultCard result={result}/>}</section>
    <section id="how" className="how"><div><p className="eyebrow">Designed for clarity</p><h2>Security signals, not a black box.</h2><p>We inspect URL structure locally: unusual domains, hidden destinations, impersonation patterns, URL shorteners, and other common phishing signals.</p></div><div className="steps"><article><span>01</span><h3>Inspect</h3><p>Extract relevant features from the URL without opening the website.</p></article><article><span>02</span><h3>Assess</h3><p>Combine indicators into a transparent, consistent risk score.</p></article><article><span>03</span><h3>Explain</h3><p>Show the strongest signals so you can make an informed choice.</p></article></div></section>
    <section className="history"><div className="section-title"><p className="eyebrow"><Clock3 size={15}/> Recent activity</p><h2>Scan history</h2></div>{history.length ? <div className="history-list">{history.map(item => <article key={item.id ?? item.url + item.checked_at}><div className={`history-icon ${item.verdict}`} >{item.verdict === "phishing" ? <ShieldX/> : <ShieldCheck/>}</div><div><b>{item.url}</b><p>{item.category}</p></div><span className={item.verdict}>{item.risk_score}% risk</span></article>)}</div> : <p className="empty">Your completed URL checks will appear here.</p>}</section>
    <footer>PhishGuard · A final-year cybersecurity and explainable ML project</footer>
  </main>
}
