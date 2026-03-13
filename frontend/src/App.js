import React, { useState, useEffect, createContext, useContext } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import { Send, Mic, ArrowRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

// --- 1. Helper Component: Live Date & Time ---
const LiveDateTime = () => {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);
  return (
    <div className="text-sm font-semibold text-gray-400 tracking-widest uppercase">
      {time.toLocaleDateString()} — {time.toLocaleTimeString()}
    </div>
  );
};

// --- 2. Landing Page Component ---
const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="h-screen w-full bg-white flex flex-col items-center justify-center relative overflow-hidden font-sans">
      {/* 3D Background Text */}
      <h1 
        className="absolute text-[18vw] font-black text-black select-none opacity-5 leading-none z-0"
        style={{
          textShadow: "4px 4px 0px #e0e0e0, 8px 8px 0px #c0c0c0, 12px 12px 0px #a0a0a0",
          transform: "rotate(-5deg) skewX(-2deg)"
        }}
      >
        VERUN AI
      </h1>

      {/* Content Overlay */}
      <div className="relative z-10 text-center px-6 flex flex-col items-center">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-6xl font-black text-black mb-6 tracking-tighter">
            VERUN AI
          </h2>
          <p className="text-gray-500 max-w-lg mx-auto mb-10 text-lg leading-relaxed">
            A sophisticated intelligence layer designed for you. 
            Verun AI consists of high-fidelity <span className="font-bold text-black border-b-2 border-black">Mic input</span> 
            and a seamless <span className="font-bold text-black border-b-2 border-black">Chat interface</span>.
          </p>
          
          <button 
            onClick={() => navigate("/chat")}
            className="group flex items-center gap-3 px-12 py-5 bg-black text-white font-bold rounded-full hover:bg-gray-800 transition-all shadow-2xl active:scale-95"
          >
            START CONVERSATION
            <ArrowRight className="group-hover:translate-x-2 transition-transform" />
          </button>
        </motion.div>
      </div>
    </div>
  );
};

// --- 3. Chat Page Component ---
const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [listening, setListening] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");

    try {
      const res = await fetch("https://verun-ai-backend.onrender.com/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: currentInput })
      });

      const data = await res.json();
      const aiMessage = { role: "assistant", text: data.response };
      setMessages((prev) => [...prev, aiMessage]);

      if (data.voice) {
        const audio = new Audio(data.voice + "?t=" + Date.now());
        audio.play().catch(e => console.log("Audio playback requires user interaction."));
      }

    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Backend connection error. Please ensure your Flask server is running." }
      ]);
    }
  };

  const startListening = () => {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert("Speech Recognition not supported in this browser. Use Chrome.");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  setListening(true);

  recognition.start();

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    setInput(transcript);
    setListening(false);
  };

  recognition.onerror = (event) => {
    console.error("Speech error:", event.error);
    setListening(false);
  };

  recognition.onend = () => {
    setListening(false);
  };
};

  return (
    <div className="h-screen flex flex-col bg-white text-black font-sans">
      {/* Top Navigation */}
      <div className="flex justify-center py-6 border-b border-gray-100 bg-white sticky top-0 z-20">
        <LiveDateTime />
      </div>

      {/* Message Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 max-w-4xl mx-auto w-full">
        <AnimatePresence>
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center text-gray-300 italic">
              No messages yet. Start by saying hello.
            </div>
          )}
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`p-4 rounded-2xl max-w-[80%] shadow-sm border ${
                  msg.role === "user"
                    ? "bg-black text-white border-black"
                    : "bg-gray-50 text-black border-gray-200"
                }`}
              >
                {msg.text}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Input Field */}
      <div className="p-6 bg-white">
        <div className="max-w-4xl mx-auto flex gap-4 items-center bg-gray-100 p-2 rounded-2xl">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Describe your request..."
            className="flex-1 bg-transparent px-4 py-2 outline-none text-black placeholder-gray-400"
          />
          
          <button
            onClick={startListening}
            className={`p-3 rounded-xl transition-all ${
              listening ? "bg-red-500 text-white animate-pulse" : "text-gray-500 hover:bg-gray-200"
            }`}
          >
            <Mic size={20} />
          </button>

          <button
            onClick={sendMessage}
            className="p-3 bg-black text-white rounded-xl hover:bg-gray-800 transition-colors"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

// --- 4. Main App Entry Point ---
export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/chat" element={<ChatPage />} />
      </Routes>
    </Router>
  );
}
