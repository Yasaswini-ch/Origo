import React, { useState } from 'react';

// Section that lists existing items and provides edit/delete actions.
export default function ListItems({ items, loading, onRefresh, onUpdate, onDelete }) {
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');

  const startEdit = (item) => {
    setEditingId(item.id);
    setEditText(item.text);
  };

  const submitEdit = (id) => {
    if (!editText.trim()) return;
    onUpdate(id, editText.trim());
    setEditingId(null);
    setEditText('');
  };

  return (
    <section id="list" className="bg-white p-4 rounded shadow space-y-2">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">List Items</h2>
        <button
          onClick={onRefresh}
          className="text-xs px-2 py-1 border border-gray-300 rounded hover:bg-gray-50"
        >
          Refresh
        </button>
      </div>
      {loading && <div className="text-sm text-gray-500">Loading...</div>}
      {!loading && items.length === 0 && (
        <div className="text-sm text-gray-500">No items yet. Create your first one above.</div>
      )}
      <ul className="space-y-2">
        {items.map((item) => (
          <li
            key={item.id}
            className="flex items-center justify-between border border-gray-200 rounded px-2 py-1 text-sm"
          >
            {editingId === item.id ? (
              <input
                className="flex-1 mr-2 border border-gray-300 rounded px-1 py-0.5 text-sm"
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
              />
            ) : (
              <span className="flex-1 mr-2">{item.text}</span>
            )}
            {editingId === item.id ? (
              <>
                <button
                  onClick={() => submitEdit(item.id)}
                  className="text-xs text-white bg-green-600 px-2 py-0.5 rounded mr-1"
                >
                  Save
                </button>
                <button
                  onClick={() => setEditingId(null)}
                  className="text-xs text-gray-600 px-2 py-0.5 rounded border border-gray-300"
                >
                  Cancel
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => startEdit(item)}
                  className="text-xs text-blue-600 px-2 py-0.5 rounded border border-blue-200 mr-1"
                >
                  Edit
                </button>
                <button
                  onClick={() => onDelete(item.id)}
                  className="text-xs text-red-600 px-2 py-0.5 rounded border border-red-200"
                >
                  Delete
                </button>
              </>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
