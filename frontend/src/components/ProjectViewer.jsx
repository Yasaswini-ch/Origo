import React, { useState } from "react";
import { downloadZip } from "../utils/download";

export default function ProjectViewer({ output, loading }) {
  const [downloadError, setDownloadError] = useState("");

  const projectId = output && typeof output === "object" ? output.project_id || output.projectId : undefined;
  const frontendFiles = output && output.frontend_files ? output.frontend_files : undefined;
  const backendFiles = output && output.backend_files ? output.backend_files : undefined;
  const readme = output && output.README ? output.README : "";

  const handleDownload = async () => {
    setDownloadError("");
    if (!projectId) {
      setDownloadError("No project_id found in response.");
      return;
    }
    try {
      await downloadZip(projectId);
    } catch (e) {
      setDownloadError(e instanceof Error ? e.message : "Failed to download ZIP");
    }
  };

  if (!output) {
    return <p className="text-sm text-gray-500">No output yet. Generate a project to see results.</p>;
  }

  return (
    <div className="flex flex-col h-full text-sm gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Project Output</h2>
        {projectId && (
          <span className="text-xs text-gray-500">project_id: {projectId}</span>
        )}
      </div>

      <div className="flex gap-2 mb-1">
        <button
          type="button"
          onClick={handleDownload}
          disabled={loading}
          className="px-3 py-1 rounded bg-green-600 text-white text-xs hover:bg-green-700 disabled:opacity-60"
        >
          Download ZIP
        </button>
      </div>
      {downloadError && <p className="text-xs text-red-600">{downloadError}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 flex-1 overflow-hidden">
        <div className="border rounded p-2 overflow-auto">
          <h3 className="font-semibold mb-1 text-xs">frontend_files</h3>
          <pre className="text-[11px] whitespace-pre-wrap break-words">
            {frontendFiles ? JSON.stringify(frontendFiles, null, 2) : "(none)"}
          </pre>
        </div>
        <div className="border rounded p-2 overflow-auto">
          <h3 className="font-semibold mb-1 text-xs">backend_files</h3>
          <pre className="text-[11px] whitespace-pre-wrap break-words">
            {backendFiles ? JSON.stringify(backendFiles, null, 2) : "(none)"}
          </pre>
        </div>
      </div>

      <div className="border rounded p-2 h-32 overflow-auto">
        <h3 className="font-semibold mb-1 text-xs">README</h3>
        <pre className="text-[11px] whitespace-pre-wrap break-words">{readme || "(no README)"}</pre>
      </div>
    </div>
  );
}
