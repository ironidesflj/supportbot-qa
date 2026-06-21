import React, { useState } from 'react';
import Chat from './components/Chat';
import Ingestion from './components/Ingestion';

function App() {
  const [tab, setTab] = useState('chat');

  return (
    <div className="min-h-screen flex flex-col items-center py-12 px-4">
      <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400 mb-10 text-center tracking-tight drop-shadow-sm">
        SupportBot QA Platform
      </h1>
      
      <div className="mb-8 flex space-x-4 glass-panel p-2">
        <button 
          onClick={() => setTab('chat')}
          className={`px-6 py-2.5 rounded-xl font-medium transition-all duration-300 ${tab === 'chat' ? 'bg-gradient-to-r from-blue-600/80 to-indigo-600/80 text-white shadow-lg shadow-blue-900/50' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}
        >
          Chat Interface
        </button>
        <button 
          onClick={() => setTab('ingest')}
          className={`px-6 py-2.5 rounded-xl font-medium transition-all duration-300 ${tab === 'ingest' ? 'bg-gradient-to-r from-blue-600/80 to-indigo-600/80 text-white shadow-lg shadow-blue-900/50' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}
        >
          Knowledge Base
        </button>
      </div>

      <div className="w-full max-w-3xl glass-panel p-6 md:p-8 animate-fade-in-up">
        {tab === 'chat' ? <Chat /> : <Ingestion />}
      </div>
    </div>
  );
}

export default App;
