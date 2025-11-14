import { downloadProjectZip } from "../services/api";

export async function downloadZip(projectId) {
  const blob = await downloadProjectZip(projectId);
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `project-${projectId}.zip`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
