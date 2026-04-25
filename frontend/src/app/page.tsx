"use client";

import { useState, useEffect } from "react";
import { createSession, addFragment, generatePDF, getFragments, getPdfFullUrl } from "./api";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [fragments, setFragments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [followUp, setFollowUp] = useState<string | null>(null);
  const [pdfLink, setPdfLink] = useState<string | null>(null);

  // Initialize session or load from localStorage
  useEffect(() => {
    const init = async () => {
      const savedSession = localStorage.getItem("fragment_session_id");
      if (savedSession) {
        setSessionId(savedSession);
        // Load existing fragments
        const data = await getFragments(savedSession);
        setFragments(data);
      } else {
        const { session_id } = await createSession();
        setSessionId(session_id);
        localStorage.setItem("fragment_session_id", session_id);
      }
    };
    init();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content || !sessionId) return;

    setLoading(true);
    setFollowUp(null);
    try {
      const fragment = await addFragment(sessionId, content);
      setFragments((prev) => [fragment, ...prev]);
      setFollowUp(fragment.follow_up_question);
      setContent("");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!sessionId) return;
    setExporting(true);
    try {
      const { pdf_url } = await generatePDF(sessionId);
      setPdfLink(pdf_url);
    } catch (err) {
      console.error(err);
    } finally {
      setExporting(false);
    }
  };

  return (
    <main className="container fade-in">
      <div className="progress-bar" style={{ width: `${Math.min(fragments.length * 10, 100)}%` }}></div>
      
      <header style={{ marginBottom: "3rem", textAlign: "center" }}>
        <h1 style={{ fontSize: "3.5rem", marginBottom: "0.5rem" }}>Fragment First.</h1>
        <p style={{ color: "var(--accent-pink)", fontStyle: "italic" }}>
          Because trauma doesn't remember in order.
        </p>
      </header>

      <section className="premium-card">
        <h2 style={{ marginBottom: "1.5rem" }}>What do you remember?</h2>
        <form onSubmit={handleSubmit}>
          <textarea
            className="fragment-input"
            placeholder="Share a piece of sound, a smell, or a feeling..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={3}
            disabled={loading}
          />
          <div style={{ marginTop: "1.5rem", display: "flex", justifyContent: "flex-end" }}>
            <button className="btn btn-primary" type="submit" disabled={loading || !content}>
              {loading ? "Processing..." : "Add Fragment"}
            </button>
          </div>
        </form>

        {followUp && (
          <div className="follow-up-container fade-in">
            <p style={{ display: "flex", alignItems: "center" }}>
              <span style={{ marginRight: "10px", fontSize: "1.2rem" }}>✨</span>
              {followUp}
            </p>
          </div>
        )}
      </section>

      {fragments.length > 0 && (
        <section className="fade-in">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h3>Your Recorded Pieces</h3>
            <button className="btn" style={{ background: "rgba(255,255,255,0.1)", fontSize: "0.8rem" }} onClick={handleExport} disabled={exporting}>
              {exporting ? "Structuring Account..." : "Export Legal Account"}
            </button>
          </div>
          
          {pdfLink && (
            <div className="premium-card" style={{ padding: "1rem", borderColor: "var(--accent-orange)" }}>
              <p>✓ Your structured account is ready.</p>
              <a href={getPdfFullUrl(pdfLink)} target="_blank" className="btn btn-primary" style={{ marginTop: "0.5rem", display: "inline-block", fontSize: "0.8rem", textDecoration: "none" }}>
                Download PDF
              </a>
            </div>
          )}

          <div style={{ display: "grid", gap: "1rem" }}>
            {fragments.map((f, i) => (
              <div key={f.id} className="premium-card" style={{ margin: 0, padding: "1.5rem" }}>
                <p style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>"{f.content}"</p>
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                  {f.tagged_time && <span className="tag tag-time">{f.tagged_time}</span>}
                  {f.tagged_location && <span className="tag tag-location">{f.tagged_location}</span>}
                  {f.tagged_person && <span className="tag tag-person">{f.tagged_person}</span>}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {!fragments.length && !loading && (
        <div style={{ textAlign: "center", opacity: 0.5, marginTop: "2rem" }}>
          <p>No pieces recorded yet. Start with a smell, a sound, or a color.</p>
        </div>
      )}

      <footer style={{ marginTop: "auto", padding: "4rem 0 2rem", fontSize: "0.8rem", opacity: 0.4 }}>
        <p>© 2026 Fragment First • Trauma-Informed AI Interface • Statement 10: Open Innovation</p>
      </footer>
    </main>
  );
}
