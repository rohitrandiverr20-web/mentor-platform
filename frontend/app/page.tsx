"use client";
import { useState } from "react";

import RealTimeSession from "./components/RealTimeSession"; 

export default function Home() {
  const [role, setRole] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeSession, setActiveSession] = useState<string | null>(null);

  const API_URL = "http://localhost:8000";

 
  const handleCreateSession = async () => {
    setLoading(true);
    try {
     
      const response = await fetch("http://localhost:8000/sessions/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        
        body: JSON.stringify({ mentor_id: "mentor_123" }), 
      });

      const data = await response.json();
      if (response.ok) {
        setActiveSession(data.session_id); 
      } else {
        alert("Failed to create session: " + data.detail);
      }
    } catch (error) {
      console.error("Failed to create session", error);
    }
    setLoading(false);
  };

   
  const handleJoinSession = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/sessions/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          session_id: sessionId,
          student_id: "student_456" // [cite: 81]
        }), 
      });

      if (response.ok) {
        setActiveSession(sessionId); // [cite: 85]
      } else {
        alert("Invalid Session ID");
      }
    } catch (error) {
      console.error("Failed to join session", error);
    }
    setLoading(false);
  };



  
  if (activeSession) {
    return <RealTimeSession sessionId={activeSession} role={role} />;
  }

 
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">
      <div className="absolute top-10 text-center">
        <h1 className="text-5xl font-extrabold mb-2 bg-linear-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
          Mentor-Platform
        </h1>
        
      </div>

      {!role ? (
        <div className="flex flex-col items-center gap-8">
          <h2 className="text-xl font-medium text-gray-300">Choose your role to get started</h2>
          <div className="flex gap-6">
            <button onClick={() => setRole("mentor")} className="group relative px-8 py-4 bg-blue-600 rounded-2xl shadow-xl hover:bg-blue-500 transition-all">
              <span className="font-bold text-lg">I am a Mentor</span>
              <div className="text-xs text-blue-200 opacity-70">Create & Lead</div>
            </button>
            <button onClick={() => setRole("student")} className="group relative px-8 py-4 bg-emerald-600 rounded-2xl shadow-xl hover:bg-emerald-500 transition-all">
              <span className="font-bold text-lg">I am a Student</span>
              <div className="text-xs text-emerald-200 opacity-70">Join & Learn</div>
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-gray-800 p-10 rounded-3xl shadow-2xl border border-gray-700 w-full max-w-md transition-all animate-in fade-in zoom-in">
          <button onClick={() => setRole(null)} className="mb-6 text-gray-500 hover:text-white flex items-center gap-2 text-sm transition-colors">
            ← Back to roles
          </button>
          
          <h2 className="text-2xl font-bold mb-8 capitalize">{role} Control Panel</h2>
          
          {role === "mentor" ? (
            <div className="space-y-6">
              <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl text-sm text-blue-300">
                You will generate a unique ID to share with your student. 
              </div>
              <button 
                onClick={handleCreateSession} 
                disabled={loading}
                className="w-full py-4 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 transition-all shadow-lg shadow-blue-900/20"
              >
                {loading ? "Initializing..." : "New Session"}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <label className="text-sm font-semibold text-gray-400 ml-1">Session Invitation ID</label>
              <input 
                type="text" 
                placeholder="Paste ID here..." 
                className="w-full p-4 bg-gray-900 border border-gray-700 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none text-white transition-all"
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
              />
              <button 
                onClick={handleJoinSession} 
                disabled={loading || !sessionId}
                className="w-full py-4 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-500 disabled:bg-gray-700 disabled:text-gray-500 transition-all shadow-lg shadow-emerald-900/20"
              >
                {loading ? "Joining..." : "Enter Session"}
              </button>
            </div>
          )}
        </div>
      )}
    </main>
  );
}