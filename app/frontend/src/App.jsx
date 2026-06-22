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

      <div
        className="mb-8 flex space-x-4 glass-panel p-2"
        role="tablist"
        aria-label="Main navigation"
      >
        <button
          onClick={() => setTab('chat')}
          role="tab"
          id="tab-chat"
          aria-selected={tab === 'chat'}
          aria-controls="panel-chat"
          className={`px-6 py-2.5 rounded-xl font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-slate-900 ${tab === 'chat' ? 'bg-gradient-to-r from-blue-600/80 to-indigo-600/80 text-white shadow-lg shadow-blue-900/50' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}
        >
          Chat Interface
        </button>
        <button
          onClick={() => setTab('ingest')}
          role="tab"
          id="tab-ingest"
          aria-selected={tab === 'ingest'}
          aria-controls="panel-ingest"
          className={`px-6 py-2.5 rounded-xl font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-slate-900 ${tab === 'ingest' ? 'bg-gradient-to-r from-blue-600/80 to-indigo-600/80 text-white shadow-lg shadow-blue-900/50' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}
        >
          Knowledge Base
        </button>
      </div>

      <div className="w-full max-w-3xl glass-panel p-6 md:p-8 animate-fade-in-up">
        <div
          role="tabpanel"
          id="panel-chat"
          aria-labelledby="tab-chat"
          hidden={tab !== 'chat'}
        >
          {tab === 'chat' && <Chat />}
        </div>
        <div
          role="tabpanel"
          id="panel-ingest"
          aria-labelledby="tab-ingest"
          hidden={tab !== 'ingest'}
        >
          {tab === 'ingest' && <Ingestion />}
        </div>
      </div>
    </div>
  );
}

export default App;
