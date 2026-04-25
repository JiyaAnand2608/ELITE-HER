const API_BASE = "http://localhost:8000";

export async function createSession() {
  const res = await fetch(`${API_BASE}/sessions`, { method: "POST" });
  return res.json();
}

export async function addFragment(sessionId: string, content: string) {
  const res = await fetch(`${API_BASE}/fragments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, content }),
  });
  return res.json();
}

export async function getFragments(sessionId: string) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/fragments`);
  return res.json();
}

export async function generatePDF(sessionId: string) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/generate-pdf`, { method: "POST" });
  return res.json();
}

export function getPdfFullUrl(pdfUrl: string) {
  return `${API_BASE}${pdfUrl}`;
}
