import { useEffect, useState } from 'react';

export default function useApi(path) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function run() {
      try {
        const res = await fetch(`http://localhost:8000${path}`);
        if (!res.ok) throw new Error(res.statusText);
        const json = await res.json();
        setData(json);
      } catch (err) {
        setError(err.message || 'request-failed');
      } finally {
        setLoading(false);
      }
    }
    run();
  }, [path]);

  return { data, loading, error };
}
