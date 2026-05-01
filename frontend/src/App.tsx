import { useState } from "react";

import { analyzeCase, compareReports, getExportUrls, getMockCompareResponse, getMockReport, uploadSubmission } from "./lib/api";
import type { CompareResult, ReportResponse, ReviewPacket } from "./types";

type Screen = "dashboard" | "upload" | "review";
type ReviewTab = "overview" | "comparison";

const dashboardStats = [
  { label: "Total Cases", value: "07", tone: "default" },
  { label: "Incomplete Cases", value: "02", tone: "warn" },
  { label: "High Severity Cases", value: "03", tone: "critical" },
  { label: "Pending Reviews", value: "04", tone: "info" }
];

function App() {
  const [screen, setScreen] = useState<Screen>("dashboard");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadedReportId, setUploadedReportId] = useState<number | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(getMockReport());
  const [reviewTab, setReviewTab] = useState<ReviewTab>("overview");
  const [compareSourceId, setCompareSourceId] = useState("1");
  const [compareTargetId, setCompareTargetId] = useState("2");
  const [compareResult, setCompareResult] = useState<CompareResult | null>(getMockCompareResponse().result);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRedacted, setShowRedacted] = useState(false);

  const summary = (report?.summary ?? {}) as Record<string, unknown>;
  const reviewPacket = (summary.review_packet ?? {}) as ReviewPacket;
  const anonymization = (summary.anonymization ?? {}) as { matched_patterns?: string[] };
  const formFields = ((report?.entities ?? {}).form_fields ?? {}) as Record<string, string>;
  const exportUrls = report ? getExportUrls(report.id, reviewTab === "comparison" ? Number(compareSourceId) : undefined) : null;
  const piiLabels = (anonymization.matched_patterns ?? reviewPacket.pii_findings ?? []).map(formatPiiLabel);
  const interventionValue = cleanIntervention(formFields.intervention_type);

  const handleCompare = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await compareReports(Number(compareSourceId), Number(compareTargetId));
      setCompareResult(response.result);
      setReviewTab("comparison");
      setScreen("review");
    } catch {
      setError("Live comparison unavailable. Showing the sample comparison state instead.");
      setCompareResult(getMockCompareResponse().result);
      setReviewTab("comparison");
      setScreen("review");
    } finally {
      setLoading(false);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!selectedFile) {
      setError("Select a .txt or .pdf submission first.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const upload = await uploadSubmission(selectedFile);
      setUploadedReportId(upload.report_id);
      const analyzed = await analyzeCase(upload.report_id);
      setReport(analyzed);
      setScreen("review");
    } catch {
      setError("Backend unavailable. Showing the sample review state instead.");
      setReport(getMockReport());
      setScreen("review");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">RegIntel AI</p>
          <h1>Officer Review Console</h1>
          <p className="sidebar-copy">
            Regulatory intake, completeness screening, and decision support for SAE submissions.
          </p>
        </div>

        <nav className="sidebar-nav">
          <button className={screen === "dashboard" ? "nav-link active" : "nav-link"} onClick={() => setScreen("dashboard")}>
            Dashboard
          </button>
          <button className={screen === "upload" ? "nav-link active" : "nav-link"} onClick={() => setScreen("upload")}>
            Upload / Analyze
          </button>
          <button className={screen === "review" ? "nav-link active" : "nav-link"} onClick={() => setScreen("review")}>
            Review Results
          </button>
        </nav>

        <div className="sidebar-panel">
          <span className="panel-label">Current Report</span>
          <strong>{report?.original_filename ?? "No submission loaded"}</strong>
          <span className="muted">Report ID: {uploadedReportId ?? report?.id ?? "Sample"}</span>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Safety Monitoring Dashboard</p>
            <h2>
              {screen === "dashboard" && "Operational Overview"}
              {screen === "upload" && "Case Upload / Analyze"}
              {screen === "review" && "Review Results"}
            </h2>
          </div>

          <div className="topbar-actions">
            {screen === "review" && exportUrls ? (
              <>
                <a className="ghost-button button-link" href={exportUrls.json} target="_blank" rel="noreferrer">
                  Export JSON
                </a>
                <a className="primary-button button-link" href={exportUrls.pdf} target="_blank" rel="noreferrer">
                  Export Officer Packet
                </a>
              </>
            ) : null}
            <button className="primary-button" onClick={() => setScreen("upload")}>
              Upload Submission
            </button>
          </div>
        </header>

        {error ? <div className="banner warning">{error}</div> : null}

        {screen === "dashboard" ? (
          <section className="dashboard-grid">
            {dashboardStats.map((stat) => (
              <article key={stat.label} className={`stat-card tone-${stat.tone}`}>
                <span>{stat.label}</span>
                <strong>{stat.value}</strong>
              </article>
            ))}
            <article className="hero-card">
              <div>
                <p className="eyebrow">Triage Queue</p>
                <h3>Move new submissions from intake to officer-ready review in one pass.</h3>
                <p>
                  The UI prioritizes incomplete filings, serious outcomes, and privacy findings so the officer sees risk
                  before narrative text.
                </p>
              </div>
              <button className="primary-button" onClick={() => setScreen("upload")}>
                Upload Submission
              </button>
            </article>
          </section>
        ) : null}

        {screen === "upload" ? (
          <section className="upload-layout">
            <article className="upload-card">
              <p className="eyebrow">Screen 2</p>
              <h3>Upload .txt or .pdf</h3>
              <p className="muted">
                The backend accepts SAE narratives and form-derived documents. Upload one file, then run the full review
                pipeline.
              </p>

              <label className="upload-dropzone">
                <input
                  type="file"
                  accept=".txt,.pdf"
                  onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                />
                <span>{selectedFile ? selectedFile.name : "Choose a submission file"}</span>
                <small>Supported: `.txt`, `.pdf`</small>
              </label>

              <button className="primary-button full-width" onClick={handleUploadAndAnalyze} disabled={loading}>
                {loading ? "Analyzing..." : "Analyze Case"}
              </button>
            </article>

            <article className="upload-card subdued">
              <p className="eyebrow">Expected Flow</p>
              <ul className="plain-list">
                <li>1. Upload submission</li>
                <li>2. Parse and anonymize</li>
                <li>3. Run completeness rules</li>
                <li>4. Classify severity</li>
                <li>5. Generate officer recommendation</li>
              </ul>
            </article>
          </section>
        ) : null}

        {screen === "review" ? (
          <>
            <div className="segment-bar">
              <button
                className={reviewTab === "overview" ? "segment-button active" : "segment-button"}
                onClick={() => setReviewTab("overview")}
              >
                Review Results
              </button>
              <button
                className={reviewTab === "comparison" ? "segment-button active" : "segment-button"}
                onClick={() => setReviewTab("comparison")}
              >
                Version Comparison
              </button>
            </div>

            {reviewTab === "overview" ? (
          <section className="review-grid">
            <article className="review-card">
              <div className="card-header">
                <p className="eyebrow">A</p>
                <h3>Case Summary</h3>
              </div>
              <div className="detail-list">
                <div>
                  <span>Patient type</span>
                  <strong>Masked adult participant</strong>
                </div>
                <div>
                  <span>Event</span>
                  <strong>{formFields.adverse_event_terms ?? "Unknown"}</strong>
                </div>
                <div>
                  <span>Intervention</span>
                  <strong>{interventionValue}</strong>
                </div>
                <div>
                  <span>Intervention discontinued</span>
                  <strong>{extractDiscontinuedFlag(formFields.intervention_type) ?? "Unknown"}</strong>
                </div>
                <div>
                  <span>Severity</span>
                  <strong>{formatSeverity(report?.classification.label ?? "Unknown")}</strong>
                </div>
                <div>
                  <span>Report type</span>
                  <strong>{reviewPacket.report_type ?? formFields.type_of_report ?? "Unknown"}</strong>
                </div>
              </div>
            </article>

            <article className="review-card">
              <div className="card-header">
                <p className="eyebrow">B</p>
                <h3>Completeness Check</h3>
              </div>
              <div className="score-ring">
                <strong>{report?.completeness.score ?? "--"}%</strong>
                <span>Review Readiness</span>
              </div>
              <div className="tag-group">
                {(report?.completeness.missing_fields ?? []).map((field) => (
                  <span className="tag danger" key={field}>
                    {field}
                  </span>
                ))}
                {(report?.completeness.recommended_missing_fields ?? []).map((field) => (
                  <span className="tag muted-tag" key={field}>
                    {field}
                  </span>
                ))}
              </div>
            </article>

            <article className="review-card">
              <div className="card-header">
                <p className="eyebrow">C</p>
                <h3>PII / PHI Detection</h3>
              </div>
              <div className="tag-group">
                {piiLabels.map((item) => (
                  <span className="tag alert" key={item}>
                    {item}
                  </span>
                ))}
              </div>
              <button className="ghost-button" type="button" onClick={() => setShowRedacted((current) => !current)}>
                {showRedacted ? "Hide Redacted Version" : "View Redacted Version"}
              </button>
              {showRedacted ? (
                <pre className="redacted-panel">
                  {report?.anonymized_text || "Redacted content will appear here after analysis."}
                </pre>
              ) : null}
            </article>

            <article className="review-card">
              <div className="card-header">
                <p className="eyebrow">D</p>
                <h3>Severity Classification</h3>
              </div>
              <strong className="severity-hero">{formatSeverity(report?.classification.label ?? "Unknown")}</strong>
              <div className="detail-list">
                <div>
                  <span>Confidence</span>
                  <strong>{Math.round((report?.classification.confidence ?? 0) * 100)}%</strong>
                </div>
                <div>
                  <span>Basis</span>
                  <strong>{report?.classification.triggered_rules?.[0] ?? "Rule-based classification"}</strong>
                </div>
                <div>
                  <span>Evidence snippet</span>
                  <strong>{String(summary.narrative_excerpt ?? "No narrative available").slice(0, 130)}...</strong>
                </div>
              </div>
            </article>

            <article className="review-card recommendation-card">
              <div className="card-header">
                <p className="eyebrow">E</p>
                <h3>Officer Recommendation</h3>
              </div>
              <div className="status-badge-row">
                <span className={`status-badge ${badgeTone(reviewPacket.recommendation?.priority ?? "Medium")}`}>
                  {reviewPacket.recommendation?.priority ?? "Medium"} Priority
                </span>
              </div>
              <strong className="recommendation">
                {reviewPacket.recommendation?.status ?? formatRecommendation(report?.completeness.review_recommendation ?? "manual_review")}
              </strong>
              <p>{reviewPacket.recommendation?.action ?? String(summary.case_overview ?? "No case overview available.")}</p>
              <div className="detail-list recommendation-meta">
                <div>
                  <span>Priority</span>
                  <strong>{reviewPacket.recommendation?.priority ?? "Medium"}</strong>
                </div>
              </div>
              <div className="basis-block">
                <span>Basis for recommendation</span>
                <ul className="plain-list compact">
                  {(reviewPacket.recommendation?.basis ?? []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </article>
          </section>
            ) : (
              <section className="compare-layout">
                <article className="review-card comparison-controls">
                  <div className="card-header">
                    <p className="eyebrow">Compare Inputs</p>
                    <h3>Version Comparison</h3>
                  </div>
                  <div className="compare-inputs">
                    <label>
                      <span>Previous Report ID</span>
                      <input value={compareSourceId} onChange={(event) => setCompareSourceId(event.target.value)} />
                    </label>
                    <label>
                      <span>Updated Report ID</span>
                      <input value={compareTargetId} onChange={(event) => setCompareTargetId(event.target.value)} />
                    </label>
                  </div>
                  <button className="primary-button" onClick={handleCompare} disabled={loading}>
                    {loading ? "Comparing..." : "Run Comparison"}
                  </button>
                </article>

                <article className="review-card comparison-banner">
                  <p className="eyebrow">Summary Banner</p>
                  <strong className="recommendation">
                    {compareResult?.summary_banner ?? "No comparison loaded"}
                  </strong>
                </article>

                <article className="review-card comparison-table-card">
                  <div className="card-header">
                    <p className="eyebrow">Changed Fields</p>
                    <h3>Material Updates</h3>
                  </div>
                  <div className="table-wrap">
                    <table className="compare-table">
                      <thead>
                        <tr>
                          <th>Field</th>
                          <th>Previous Value</th>
                          <th>Updated Value</th>
                          <th>Impact</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(compareResult?.changed_fields ?? []).map((item) => (
                          <tr key={item.field}>
                            <td>{item.label}</td>
                            <td>{item.old}</td>
                            <td>{item.new}</td>
                            <td>{item.impact}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </article>

                <article className="review-card recommendation-card">
                  <div className="card-header">
                    <p className="eyebrow">Officer Summary</p>
                    <h3>LLM-Assisted Explanation</h3>
                  </div>
                  <strong className="recommendation">
                    {compareResult?.officer_summary.summary_banner ?? "No comparison summary"}
                  </strong>
                  <p>{compareResult?.officer_summary.officer_summary ?? "No officer-facing summary available."}</p>
                </article>
              </section>
            )}
          </>
        ) : null}
      </main>
    </div>
  );
}

function formatRecommendation(value: string) {
  switch (value) {
    case "return_for_correction":
      return "Incomplete submission";
    case "priority_medical_review":
      return "Requires urgent medical review";
    case "approve_for_officer_review":
    case "ready_for_officer_review":
      return "Ready for medical review";
    default:
      return "Requires follow-up clarification";
  }
}

function cleanIntervention(value?: string) {
  if (!value) return "Unknown";
  const firstLine = value.split("\n")[0] ?? value;
  return firstLine.replace(/^Medication:\s*/i, "").replace(/^Device:\s*/i, "").trim() || firstLine.trim();
}

function extractDiscontinuedFlag(value?: string) {
  if (!value) return null;
  const match = value.match(/Was study intervention discontinued due to event\?\s*(Yes|No)/i);
  return match?.[1] ?? null;
}

function formatPiiLabel(value: string) {
  switch (value) {
    case "patient_name":
      return "Name detected";
    case "phone":
      return "Phone detected";
    case "email":
      return "Email detected";
    case "address":
      return "Address detected";
    default:
      return value.replace(/_/g, " ");
  }
}

function formatSeverity(value: string) {
  return value
    .split("-")
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" - ");
}

function badgeTone(priority: string) {
  if (priority.toLowerCase() === "high") return "badge-high";
  if (priority.toLowerCase() === "medium") return "badge-medium";
  return "badge-low";
}

export default App;
