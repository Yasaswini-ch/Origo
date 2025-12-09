export async function getJson(path) {
  const res = await fetch(`http://localhost:8000${path}`);
  if (!res.ok) {
    throw new Error(res.statusText);
  }
  return res.json();
}
