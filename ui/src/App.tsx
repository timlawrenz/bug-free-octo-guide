import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { text: 'Welcome to the PRD Generator! What is the feature you would like to build?', author: 'bot' },
  ]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const chatBoxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (input.trim()) {
      const newMessages = [...messages, { text: input, author: 'user' }];
      setMessages(newMessages);
      const messageToSend = input;
      setInput('');

      try {
        const response = await fetch('http://184.72.72.233:8000/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: messageToSend, session_id: sessionId }),
        });

        if (response.ok) {
          const data = await response.json();
          setMessages([...newMessages, { text: data.response, author: 'bot' }]);
          setSessionId(data.session_id);
        } else {
          console.error('Error sending message');
          setMessages([...newMessages, { text: 'Error: Could not connect to the server.', author: 'bot' }]);
        }
      } catch (error) {
        console.error('Error sending message:', error);
        setMessages([...newMessages, { text: 'Error: Could not connect to the server.', author: 'bot' }]);
      }
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <div className="bg-blue-600 text-white p-4 text-center text-lg font-semibold">
        PRD Generator
      </div>
      <div ref={chatBoxRef} className="flex-1 p-4 overflow-y-auto">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.author === 'bot' ? 'justify-start' : 'justify-end'} mb-2`}>
            <div className={`rounded-lg px-4 py-2 ${msg.author === 'bot' ? 'bg-gray-300 text-black' : 'bg-blue-600 text-white'}`}>
              {msg.text}
            </div>
          </div>
        ))}
      </div>
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex">
          <input
            type="text"
            className="flex-1 p-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
          />
          <button className="bg-blue-600 text-white px-4 rounded-r-lg hover:bg-blue-700" onClick={handleSend}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;

