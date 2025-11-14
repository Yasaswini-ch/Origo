const API_BASE = "http://localhost:8000";

export async function generateProject(payload) {
  const response = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to generate project");
  }
  return response.json();
}

export async function generateComponent(payload) {
  const response = await fetch(`${API_BASE}/generate/component`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to generate component");
  }
  return response.json();
}

export async function generatePreview(payload) {
  const response = await fetch(`${API_BASE}/generate/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to generate preview");
  }
  return response.json();
}

export async function downloadProjectZip(projectId) {
  const response = await fetch(`${API_BASE}/projects/${encodeURIComponent(projectId)}/download`);
  if (!response.ok) {
    throw new Error("Failed to download project zip");
  }
  return response.blob();
}
