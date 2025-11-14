// Simple API helper functions for working with the item endpoints.

export async function getItems() {
  const response = await fetch('/api/items');
  if (!response.ok) {
    throw new Error('Failed to load items');
  }
  return response.json();
}

export async function createItem(text) {
  const response = await fetch('/api/items', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!response.ok) {
    throw new Error('Failed to create item');
  }
  return response.json();
}

export async function updateItem(id, text) {
  const response = await fetch(`/api/items/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!response.ok) {
    throw new Error('Failed to update item');
  }
  return response.json();
}

export async function deleteItem(id) {
  const response = await fetch(`/api/items/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete item');
  }
}
