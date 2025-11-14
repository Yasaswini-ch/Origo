import React, { useState } from "react";

export default function GeneratorForm({ onGenerate, loading }) {
  const [idea, setIdea] = useState("");
  const [targetUsers, setTargetUsers] = useState("");
  const [features, setFeatures] = useState("");
  const [stack, setStack] = useState("react+tailwind | fastapi");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!idea.trim()) return;
    onGenerate({
      idea,
      target_users: targetUsers,
      features,
      stack,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3 text-sm">
      <div className="space-y-1">
        <label className="block font-medium">SaaS Idea</label>
        <input
          className="w-full border rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="e.g. Micro-SaaS for freelancers"
        />
      </div>

      <div className="space-y-1">
        <label className="block font-medium">Target Users</label>
        <input
          className="w-full border rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={targetUsers}
          onChange={(e) => setTargetUsers(e.target.value)}
          placeholder="e.g. designers, developers"
        />
      </div>

      <div className="space-y-1">
        <label className="block font-medium">Features</label>
        <textarea
          className="w-full border rounded px-2 py-1 h-20 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={features}
          onChange={(e) => setFeatures(e.target.value)}
          placeholder="Comma-separated features"
        />
      </div>

      <div className="space-y-1">
        <label className="block font-medium">Tech Stack</label>
        <input
          className="w-full border rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={stack}
          onChange={(e) => setStack(e.target.value)}
          placeholder="react+tailwind | fastapi"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="inline-flex items-center px-3 py-1.5 rounded bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-60"
     >
        {loading ? "Generating..." : "Generate Project"}
      </button>
    </form>
  );
}
