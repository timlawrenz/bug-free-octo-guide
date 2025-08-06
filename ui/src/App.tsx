import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

const planningMessageSequence = (repo: string) => [
  `Cloning repository ${repo}...`,
  "Analyzing repository structure...",
  "Identifying relevant files and models...",
  "Starting planning process...",
  "Generating initial questions..."
];

function App() {
  const [featureDescription, setFeatureDescription] = useState('add a profile picture');
  const [githubRepo, setGithubRepo] = useState('timlawrenz/herLens');
  const [isPlanning, setIsPlanning] = useState(false);
  const [planningStatus, setPlanningStatus] = useState<string | null>(null);
  const [messages, setMessages] = useState<{ text: string, author: string }[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [prd, setPrd] = useState<string | null>(null);
  const chatBoxRef = useRef<HTMLDivElement>(null);
  const [currentPlanningMessageIndex, setCurrentPlanningMessageIndex] = useState(0);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (sessionId) {
      const messagesToShow = planningMessageSequence(githubRepo);
      const interval = setInterval(async () => {
        try {
          const response = await fetch(`http://184.72.72.233:8000/planning_status/${sessionId}`);
          if (response.ok) {
            const data = await response.json();
            setPlanningStatus(data.status);
            if (data.status === 'ready') {
              setMessages(prevMessages => [...prevMessages, { text: data.response, author: 'bot' }]);
              clearInterval(interval);
            } else if (data.status === 'error') {
              setMessages(prevMessages => [...prevMessages, { text: `Error: ${data.response}`, author: 'bot' }]);
              clearInterval(interval);
            } else {
              setCurrentPlanningMessageIndex(prevIndex => {
                const nextIndex = prevIndex + 1;
                if (nextIndex < messagesToShow.length) {
                  setMessages(prevMessages => {
                    const lastMessage = prevMessages[prevMessages.length - 1];
                    if (lastMessage && lastMessage.text === messagesToShow[nextIndex]) {
                      return prevMessages;
                    }
                    return [...prevMessages, { text: messagesToShow[nextIndex], author: 'bot' }];
                  });
                  return nextIndex;
                }
                return prevIndex;
              });
            }
          } else {
            console.error('Error fetching planning status');
            clearInterval(interval);
          }
        } catch (error) {
          console.error('Error fetching planning status:', error);
          clearInterval(interval);
        }
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [sessionId, githubRepo]);

  const handleStartPlanning = async () => {
    if (featureDescription.trim() && githubRepo.trim()) {
      setIsPlanning(true);
      const messagesToShow = planningMessageSequence(githubRepo);
      setMessages([{ text: messagesToShow[0], author: 'bot' }]);
      setCurrentPlanningMessageIndex(0);

      try {
        const response = await fetch('http://184.72.72.233:8000/start_planning', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            feature_description: featureDescription,
            repo_url: `https://github.com/${githubRepo}.git`
          }),
        });

        if (response.ok) {
          const data = await response.json();
          setSessionId(data.session_id);
        } else {
          const errorData = await response.json();
          const errorMessage = `Error: An internal error occurred during planning session startup.\n\n${JSON.stringify(errorData, null, 2)}`;
          setMessages(prevMessages => [...prevMessages, { text: errorMessage, author: 'bot' }]);
        }
      } catch (error) {
        console.error('Error starting planning session:', error);
        const errorMessage = error instanceof Error ? error.message : String(error);
        setMessages(prevMessages => [...prevMessages, { text: `Error: Could not connect to the server to start planning. ${errorMessage}`, author: 'bot' }]);
      }
    }
  };


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
          if (!prd) {
            setPrd("This is a placeholder for the generated PRD content.");
          }
        } else {
          console.error('Error sending message');
          const errorData = await response.json();
          const errorMessage = `Error: An internal error occurred during planning session startup.\n\n${JSON.stringify(errorData, null, 2)}\n\n`;
          setMessages([...newMessages, { text: errorMessage, author: 'bot' }]);
        } 
      } catch (error) {
        console.error('Error sending message:', error);
        const errorMessage = error instanceof Error ? error.message : String(error);
        setMessages([...newMessages, { text: `Error: Could not connect to the server. ${errorMessage}`, author: 'bot' }]);
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
            placeholder={planningStatus === 'ready' ? "Type your message..." : `Planning status: ${planningStatus}`}
            disabled={planningStatus !== 'ready'}
          />
          <button className="bg-blue-600 text-white px-4 rounded-r-lg hover:bg-blue-700" onClick={handleSend} disabled={planningStatus !== 'ready'}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;