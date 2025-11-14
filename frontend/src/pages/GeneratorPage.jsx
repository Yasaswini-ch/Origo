import React from "react";
import useGenerator from "../hooks/useGenerator";
import GeneratorForm from "../components/GeneratorForm";
import ProjectViewer from "../components/ProjectViewer";

export default function GeneratorPage() {
  const { loading, error, output, generate, generateComponent, generatePreview } = useGenerator();

  const handleGenerateProject = async (values) => {
    await generate(values);
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 p-4">
      <div className="max-w-5xl mx-auto space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Micro-SaaS Generator</h1>
          <span className="text-xs text-gray-500">Backend: http://localhost:8000</span>
        </header>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-3 bg-white rounded shadow p-4">
            <h2 className="text-lg font-semibold">Generate Project</h2>
            <GeneratorForm onGenerate={handleGenerateProject} loading={loading} />
            {error && <p className="text-sm text-red-600">{error}</p>}
          </div>

          <div className="bg-white rounded shadow p-4">
            <ProjectViewer
              output={output}
              loading={loading}
              generateComponent={generateComponent}
              generatePreview={generatePreview}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
