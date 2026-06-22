import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messageIdCounter = useRef(0);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      id: ++messageIdCounter.current,
      role: 'user',
      text: input,
    };
    setMessages(prev => [...prev, userMessage]);
    const queryText = input;
    setInput('');
    setLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const res = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText }),
      });

      const data = await res.json();

      if (!res.ok) {
        // Surface backend error detail to the user
        const errorMsg = data.detail || `Request failed with status ${res.status}`;
        setMessages(prev => [...prev, {
          id: ++messageIdCounter.current,
          role: 'bot',
          text: `**Error:** ${errorMsg}`,
          isError: true,
        }]);
        return;
      }

      const botMessage = {
        id: ++messageIdCounter.current,
        role: 'bot',
        text: data.answer,
        sources: data.sources || [],
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: ++messageIdCounter.current,
        role: 'bot',
        text: `**Network error:** Unable to reach the server. Please check your connection and try again.`,
        isError: true,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[32rem]">
      <div
        className="flex-1 overflow-y-auto mb-6 space-y-6 pr-2 custom-scrollbar"
        aria-live="polite"
        aria-busy={loading}
      >
        {messages.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-center text-slate-400">
            <div className="mb-4 text-5xl opacity-30">💬</div>
            <p className="text-lg font-medium text-slate-300 mb-2">No messages yet</p>
            <p className="text-sm">Ask SupportBot a question about the knowledge base to get started.</p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex fade-in-up ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] p-4 ${msg.isError ? 'bg-red-900/40 border border-red-500/40' : msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot'}`}
              role={msg.role === 'user' ? undefined : 'article'}
            >
              <div className="prose prose-invert max-w-none text-sm md:text-base">
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/10 text-xs italic text-blue-200/70">
                  <span className="font-semibold text-blue-300">Sources:</span> {msg.sources.join(', ')}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start fade-in-up">
            <div
              className="chat-bubble-bot p-4 flex items-center space-x-2"
              aria-label="Assistant is typing"
            >
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-100"></div>
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-200"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex space-x-3 mt-auto">
        <label htmlFor="chat-input" className="sr-only">
          Ask SupportBot a question
        </label>
        <input
          id="chat-input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className="glass-input flex-1"
          placeholder="Ask SupportBot a question..."
          disabled={loading}
          aria-label="Question input"
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="glass-button flex items-center justify-center min-w-[100px] disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Send question"
        >
          {loading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default Chat;
