import React, { useState, useRef } from 'react';

function Ingestion() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleUpload = async () => {
    if (!file) return;
    setStatus('Uploading and ingesting...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const res = await fetch(`${apiUrl}/api/ingest`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setStatus(`Success! Added ${data.chunks_added} chunks from ${data.filename}.`);
        setFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      } else {
        const errorDetail = data.detail || `Request failed with status ${res.status}`;
        setStatus(`Error: ${errorDetail}`);
      }
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && /\.(pdf|txt|md)$/i.test(droppedFile.name)) {
      setFile(droppedFile);
    }
  };

  return (
    <div className="flex flex-col space-y-6 fade-in-up">
      <div>
        <h2 className="text-2xl font-semibold text-slate-100 mb-2">Upload Knowledge Base</h2>
        <p className="text-sm text-slate-400">
          Supported formats:{' '}
          <span className="font-mono bg-white/10 px-1 py-0.5 rounded text-blue-300">.pdf</span>,{' '}
          <span className="font-mono bg-white/10 px-1 py-0.5 rounded text-blue-300">.txt</span>,{' '}
          <span className="font-mono bg-white/10 px-1 py-0.5 rounded text-blue-300">.md</span>
        </p>
      </div>

      <div
        className={`relative group ${isDragging ? 'ring-2 ring-blue-400 ring-offset-2 ring-offset-slate-900 rounded-xl' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-500"></div>
        <div
          className={`relative bg-slate-900 border border-dashed rounded-xl p-4 flex items-center justify-center transition-colors ${isDragging ? 'border-blue-400 bg-blue-900/20' : 'border-slate-700'}`}
        >
          <label
            htmlFor="file-input"
            className="w-full text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-600/20 file:text-blue-400 hover:file:bg-blue-600/30 transition cursor-pointer flex items-center justify-center py-2"
          >
            <span className="text-center">
              {file ? (
                <>📎 {file.name} <span className="text-xs text-slate-500">({(file.size / 1024).toFixed(1)} KB)</span></>
              ) : (
                <>📁 Click to select or drag & drop a file here</>
              )}
            </span>
          </label>
          <input
            id="file-input"
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md"
            onChange={(e) => setFile(e.target.files[0])}
            className="sr-only"
            aria-label="Select file to upload"
          />
        </div>
      </div>

      <button
        onClick={handleUpload}
        disabled={!file}
        className="glass-button w-full disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        aria-label="Ingest document into knowledge base"
      >
        {status.includes('Uploading') ? 'Processing...' : 'Ingest Document'}
      </button>

      {status && (
        <div
          role="status"
          className={`mt-4 p-4 rounded-xl text-sm font-medium border fade-in-up ${
            status.includes('Success')
              ? 'bg-emerald-900/30 border-emerald-500/30 text-emerald-300'
              : status.includes('Uploading')
              ? 'bg-blue-900/30 border-blue-500/30 text-blue-300'
              : 'bg-red-900/30 border-red-500/30 text-red-300'
          }`}
        >
          {status}
        </div>
      )}
    </div>
  );
}

export default Ingestion;
