import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input })
      });
      const data = await res.json();
      
      const botMessage = { 
        role: 'bot', 
        text: data.answer, 
        sources: data.sources 
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', text: "Error connecting to server." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[32rem]">
      <div className="flex-1 overflow-y-auto mb-6 space-y-6 pr-2 custom-scrollbar">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex fade-in-up ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-4 ${msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot'}`}>
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
            <div className="chat-bubble-bot p-4 flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-100"></div>
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-200"></div>
            </div>
          </div>
        )}
      </div>
      <div className="flex space-x-3 mt-auto">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          className="glass-input flex-1"
          placeholder="Ask SupportBot a question..."
        />
        <button onClick={sendMessage} disabled={loading} className="glass-button flex items-center justify-center min-w-[100px]">
          {loading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default Chat;
