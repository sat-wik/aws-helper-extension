import React, { useState, useRef, useEffect } from "react";
import { PaperAirplaneIcon, ChatBubbleLeftIcon } from "@heroicons/react/24/solid";


const App: React.FC = () => {
  const [messages, setMessages] = useState<{ type: string; text: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false); // Dark mode toggle state
  const chatRef = useRef<HTMLDivElement>(null);

  const handleSend = async () => {
    if (!input.trim()) return;
  
    setMessages([...messages, { type: "user", text: input }]);
    setLoading(true);
  
    try {
      const response = await fetch("http://127.0.0.1:8000/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ input }),
      });
  
      const data = await response.json();
      const botMessage = data.response;
  
      setMessages((prev) => [...prev, { type: "bot", text: botMessage }]);
  
      // Extract CSS selector for highlighting
      const regex = /Selector for button: (#[a-zA-Z0-9-_]+)/;
      const match = botMessage.match(regex);
      if (match) {
        const selector = match[1];
        chrome.runtime.sendMessage({ action: "highlight", selector });
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { type: "bot", text: "An error occurred. Please try again." },
      ]);
    } finally {
      setLoading(false);
      setInput("");
    }
  };
  

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, loading]);

  return (
    <div
      className={`flex flex-col w-[400px] h-[600px] overflow-hidden shadow-lg ${
        darkMode ? "bg-gray-800 border-gray-600" : "bg-gray-50 border-gray-300"
      }`}
    >
      {/* Header with Dark Mode Toggle */}
      <div className={`p-3 flex justify-between items-center bg-gray-100 text-white font-bold ${
        darkMode ? "bg-gray-900" : "bg-gray-100"
      }`}>
        <span></span>
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="text-sm p-2 rounded-md bg-zinc-700 hover:bg-zinc-400 active:bg-zinc-700"
        >
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </div>

      {/* Chat Window */}
      <div
        ref={chatRef}
        className={`flex-grow p-4 overflow-y-auto flex flex-col ${
          darkMode ? "bg-gray-900" : "bg-gray-100"
        }`}
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-3 my-2 rounded-lg text-sm font-medium shadow-md flex items-center ${
              msg.type === "user"
                ? darkMode
                  ? "bg-blue-700 text-white self-end"
                  : "bg-blue-500 text-white self-end"
                : darkMode
                ? "bg-gray-700 text-gray-200 self-start"
                : "bg-gray-300 text-black self-start"
            } max-w-[75%]`}
          >
            {msg.type === "bot" && (
              <ChatBubbleLeftIcon className="h-5 w-5 text-gray-500 mr-2" />
            )}
            {msg.text}
          </div>
        ))}
        {loading && (
          <div
            className={`p-3 my-2 rounded-lg italic flex items-center ${
              darkMode ? "bg-gray-700 text-gray-200" : "bg-gray-300 text-black"
            } max-w-[75%] self-start`}
          >
            <ChatBubbleLeftIcon className="h-5 w-5 text-gray-500 mr-2" />
            Bot is typing...
          </div>
        )}
      </div>

      {/* Input Area */}
      <div
        className={`flex items-center p-4 border-t ${
          darkMode ? "border-gray-700 bg-gray-800" : "border-gray-300 bg-white"
        }`}
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about AWS..."
          className={`flex-grow p-3 rounded-lg resize-none ${
            darkMode
              ? "bg-gray-800 text-gray-200 placeholder-gray-400"
              : "bg-white text-gray-700 placeholder-gray-500"
          } focus:outline-none`}
          rows={1}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className={`ml-3 px-4 py-3 rounded-lg shadow-md flex items-center justify-center ${
            loading
              ? "bg-gray-400 text-gray-800 cursor-not-allowed"
              : darkMode
              ? "bg-blue-600 text-white hover:bg-blue-500 active:bg-blue-700"
              : "bg-blue-500 text-white hover:bg-blue-600 active:bg-blue-700"
          }`}
        >
          {loading ? (
            "Loading..."
          ) : (
            <PaperAirplaneIcon className="h-5 w-5 text-white" />
          )}
        </button>
      </div>
    </div>
  );
};

export default App;
