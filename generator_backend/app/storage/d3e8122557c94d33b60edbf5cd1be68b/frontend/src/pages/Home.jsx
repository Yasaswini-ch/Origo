import React from 'react';
import useApi from '../hooks/useApi.js';

export default function Home() {
  const { data, loading, error } = useApi('/health');

  return (
    <div className='max-w-2xl space-y-4'>
      <h2 className='text-2xl font-semibold tracking-tight'>Welcome to your Origo app</h2>
      <p className='text-slate-300'>This is a minimal fullstack starter wired to a FastAPI backend.</p>
      <div className='rounded-md border border-slate-800 bg-slate-900/60 p-4 text-sm font-mono'>
        <div className='mb-1 text-slate-400'>Backend health:</div>
        {loading && <div>Loading...</div>}
        {error && <div className='text-red-400'>Error: {error}</div>}
        {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
      </div>
    </div>
  );
}
