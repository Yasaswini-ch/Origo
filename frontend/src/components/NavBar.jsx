import React from 'react';

// Simple navigation bar with links to page sections.
export default function NavBar() {
  return (
    <nav className="w-full bg-blue-600 text-white px-4 py-3 shadow">
      <div className="max-w-3xl mx-auto flex items-center justify-between">
        <span className="font-semibold text-lg">generic-saas-app</span>
        <div className="flex items-center gap-4 text-sm">
          <a href="#create" className="hover:underline">
            Create
          </a>
          <a href="#list" className="hover:underline">
            List
          </a>
        </div>
      </div>
    </nav>
  );
}
