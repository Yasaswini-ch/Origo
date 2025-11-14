import React, { useState } from 'react';

// Form section used to create a new item.
export default function CreateItem({ onCreate }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onCreate(text.trim());
    setText('');
  };

  return (
    <section id="create" className="bg-white p-4 rounded shadow space-y-2">
      <h2 className="text-lg font-semibold">Create Item</h2>
      <form className="flex gap-2" onSubmit={handleSubmit}>
        <input
          className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Item text"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
        >
          Add
        </button>
      </form>
    </section>
  );
}
