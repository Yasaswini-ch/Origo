import React from 'react';

export default function Button({ children, ...props }) {
  return (
    <button
      className='inline-flex items-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white shadow-sm hover:bg-indigo-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2'
      {...props}
    >
      {children}
    </button>
  );
}
