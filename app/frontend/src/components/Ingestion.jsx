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
    <div className="flex flex-col space-y-6 fade-in-up">
      <div>
        <h2 className="text-2xl font-semibold text-slate-100 mb-2">Upload Knowledge Base</h2>
        <p className="text-sm text-slate-400">Supported formats: <span className="font-mono bg-white/10 px-1 py-0.5 rounded text-blue-300">.pdf</span>, <span className="font-mono bg-white/10 px-1 py-0.5 rounded text-blue-300">.txt</span>, <span className="font-mono bg-white/10 px-1 py-0.5 rounded text-blue-300">.md</span></p>
      </div>
      
      <div className="relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-500"></div>
        <div className="relative bg-slate-900 border border-slate-700 rounded-xl p-4 flex items-center justify-center border-dashed">
          <input 
            type="file" 
            accept=".pdf,.txt,.md"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-600/20 file:text-blue-400 hover:file:bg-blue-600/30 transition cursor-pointer"
          />
        </div>
      </div>

      <button 
        onClick={handleUpload}
        disabled={!file}
        className="glass-button w-full disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
      >
        {status.includes('Uploading') ? 'Processing...' : 'Ingest Document'}
      </button>

      {status && (
        <div className={`mt-4 p-4 rounded-xl text-sm font-medium border fade-in-up ${status.includes('Success') ? 'bg-emerald-900/30 border-emerald-500/30 text-emerald-300' : status.includes('Uploading') ? 'bg-blue-900/30 border-blue-500/30 text-blue-300' : 'bg-red-900/30 border-red-500/30 text-red-300'}`}>
          {status}
        </div>
      )}
    </div>
  );
}

export default Ingestion;
