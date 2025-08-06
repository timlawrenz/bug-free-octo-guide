import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

function App() {
  const [featureDescription, setFeatureDescription] = useState('add a profile picture');
  const [githubRepo, setGithubRepo] = useState('timlawrenz/herLens');
  const [isPlanning, setIsPlanning] = useState(false);
  const [messages, setMessages] = useState<{ text: string, author: string }[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [prd, setPrd] = useState<string | null>(null);
  const chatBoxRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const handleDownloadPrd = () => {
    if (prd) {
      const blob = new Blob([prd], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'prd.md';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const handleStartPlanning = async () => {
    if (featureDescription.trim() && githubRepo.trim()) {
      setIsPlanning(true);
      const initialMessage = `Feature: ${featureDescription}\nRepo: https://github.com/${githubRepo}.git`;
      setMessages([{ text: `Starting planning for feature: "${featureDescription}"...`, author: 'bot' }]);
      
      // Directly call the chat endpoint to start the process
      await handleSend(initialMessage);
    }
  };

  const handleSend = async (messageOverride?: string) => {
    const message = messageOverride || input;
    if (message.trim() && !isLoading) {
      const newMessages = [...messages, { text: message, author: 'user' }];
      setMessages(newMessages);
      const messageToSend = message;
      setInput('');
      setIsLoading(true);

      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: messageToSend, session_id: sessionId }),
        });

        if (response.ok) {
          const data = await response.json();
          setMessages(prev => [...prev, { text: data.response, author: 'bot' }]);
          setSessionId(data.session_id);
          // Check if the response contains ticket-like structures to identify PRD
          if (data.response.includes('### Ticket')) {
            // Assuming the PRD is the last bot message before the tickets
            const lastBotMessage = newMessages.filter(m => m.author === 'bot').pop();
            if(lastBotMessage) {
              setPrd(lastBotMessage.text);
            }
          }
        } else {
          console.error('Error sending message');
          const errorData = await response.json();
          const errorMessage = `Error: An internal error occurred.\n\n${JSON.stringify(errorData, null, 2)}\n\n`;
          setMessages(prev => [...prev, { text: errorMessage, author: 'bot' }]);
        } 
      } catch (error) {
        console.error('Error sending message:', error);
        const errorMessage = error instanceof Error ? error.message : String(error);
        setMessages(prev => [...prev, { text: `Error: Could not connect to the server. ${errorMessage}`, author: 'bot' }]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  if (!isPlanning) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
          <h1 className="text-2xl font-bold text-center text-gray-900">Start a New Feature</h1>
          <div>
            <label htmlFor="feature" className="text-sm font-medium text-gray-700">Feature Description</label>
            <textarea
              id="feature"
              className="w-full p-2 mt-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              value={featureDescription}
              onChange={(e) => setFeatureDescription(e.target.value)}
              placeholder="e.g., Implement user deactivation"
            />
          </div>
          <div>
            <label htmlFor="repo" className="text-sm font-medium text-gray-700">GitHub Repository</label>
            <input
              id="repo"
              className="w-full p-2 mt-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              value={githubRepo}
              onChange={(e) => setGithubRepo(e.target.value)}
              placeholder="e.g., timlawrenz/herLens"
            />
          </div>
          <button
            className="w-full py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            onClick={handleStartPlanning}
          >
            Start Planning
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <div className="bg-blue-600 text-white p-4 text-center text-lg font-semibold">
        PRD Generator
      </div>
      <div ref={chatBoxRef} className="flex-1 p-4 overflow-y-auto">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.author === 'bot' ? 'justify-start' : 'justify-end'} mb-2`}>
            <div className={`rounded-lg px-4 py-2 ${msg.author === 'bot' ? 'bg-gray-300 text-black' : 'bg-blue-600 text-white'}`}>
              <ReactMarkdown remarkPlugins={[remarkGfm]} className="prose">{msg.text}</ReactMarkdown>
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
            placeholder={isLoading ? "Thinking..." : "Type 'approve' to generate tickets, or ask for changes."}
            disabled={isLoading}
          />
          <button className="bg-blue-600 text-white px-4 rounded-r-lg hover:bg-blue-700" onClick={() => handleSend()} disabled={isLoading}>Send</button>
        </div>
        {prd && (
          <div className="mt-4 text-center">
            <button
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
              onClick={handleDownloadPrd}
            >
              Download PRD
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
