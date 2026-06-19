import React, { useState } from 'react';
import Chat from './components/Chat';
import Ingestion from './components/Ingestion';

function App() {
  const [tab, setTab] = useState('chat');

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center py-10">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">SupportBot QA Platform</h1>
      
      <div className="mb-6 flex space-x-4">
        <button 
          onClick={() => setTab('chat')}
          className={`px-4 py-2 rounded ${tab === 'chat' ? 'bg-blue-600 text-white' : 'bg-white text-gray-800 border'}`}
        >
          Chat Interface
        </button>
        <button 
          onClick={() => setTab('ingest')}
          className={`px-4 py-2 rounded ${tab === 'ingest' ? 'bg-blue-600 text-white' : 'bg-white text-gray-800 border'}`}
        >
          Knowledge Base Ingestion
        </button>
      </div>

      <div className="w-full max-w-2xl bg-white shadow-md rounded-lg p-6">
        {tab === 'chat' ? <Chat /> : <Ingestion />}
      </div>
    </div>
  );
}

export default App;
