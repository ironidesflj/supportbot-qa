import React, { useState } from 'react';

function Ingestion() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');

  const handleUpload = async () => {
    if (!file) return;
    setStatus('Uploading and ingesting...');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/ingest', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setStatus(`Success! Added ${data.chunks_added} chunks from ${data.filename}.`);
      } else {
        setStatus(`Error: ${data.detail}`);
      }
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    }
  };

  return (
    <div className="flex flex-col space-y-4">
      <h2 className="text-xl font-bold">Upload Knowledge Base Document</h2>
      <p className="text-sm text-gray-500">Supported formats: .pdf, .txt, .md</p>
      <input 
        type="file" 
        accept=".pdf,.txt,.md"
        onChange={(e) => setFile(e.target.files[0])}
        className="border p-2 rounded"
      />
      <button 
        onClick={handleUpload}
        disabled={!file}
        className="bg-green-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        Ingest Document
      </button>
      {status && <div className="mt-4 p-3 bg-gray-100 rounded text-sm">{status}</div>}
    </div>
  );
}

export default Ingestion;
