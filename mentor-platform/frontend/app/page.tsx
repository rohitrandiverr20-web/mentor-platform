"use client";
import { useState } from "react";

export default function Home() {
  const [role, setRole] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeSession, setActiveSession] = useState<string | null>(null);

 const API_URL = "http://localhost:8000";

  // Day 3-5: Create Session (Mentor Task)
  const handleCreateSession = async () => {
    setLoading(true);
    try {
      // 1. THIS LINE CALLS THE BACKEND (YOU ARE MISSING THIS!)
      const response = await fetch("http://localhost:8000/sessions/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      // 2. THIS TRANSLATES THE ANSWER
      const data = await response.json();

      // 3. THIS UPDATES THE SCREEN
      setActiveSession(data.session_id);
      
    } catch (error) {
      console.error("Failed to create session", error);
    }
    setLoading(false);
  };

  // Day 3-5: Join Session (Student Task)
  const handleJoinSession = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/sessions/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }), // [cite: 73, 85]
      });
      if (response.ok) setActiveSession(sessionId);
    } catch (error) {
      console.error("Failed to join session", error);
    }
    setLoading(false);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-50 text-gray-900">
      <h1 className="text-4xl font-bold mb-10 text-blue-600">1-on-1 Mentor Platform</h1>

      {!role ? (
        <div className="flex gap-6">
          <button onClick={() => setRole("mentor")} className="px-8 py-4 bg-blue-500 text-white rounded-xl shadow-lg hover:bg-blue-600 transition-all font-bold">I am a Mentor</button>
          <button onClick={() => setRole("student")} className="px-8 py-4 bg-green-500 text-white rounded-xl shadow-lg hover:bg-green-600 transition-all font-bold">I am a Student</button>
        </div>
      ) : activeSession ? (
        <div className="bg-white p-10 rounded-2xl shadow-2xl border border-gray-100 text-center">
          <h2 className="text-2xl font-bold text-green-600 mb-4">Session Active!</h2>
          <p className="mb-4 font-mono bg-gray-100 p-2 rounded">ID: {activeSession}</p>
          <p className="text-gray-500 italic">Connecting to Real-time Editor and Video... [cite: 86, 129]</p>
        </div>
      ) : (
        <div className="bg-white p-10 rounded-2xl shadow-2xl border border-gray-100 w-full max-w-md">
          <h2 className="text-2xl font-bold mb-6 text-center capitalize">{role} Dashboard</h2>
          
          {role === "mentor" ? (
            <button 
              onClick={handleCreateSession} 
              disabled={loading}
              className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400"
            >
              {loading ? "Creating..." : "Start New Mentoring Session"}
            </button>
          ) : (
            <div className="space-y-4">
              <input 
                type="text" 
                placeholder="Enter Session ID" 
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
              />
              <button 
                onClick={handleJoinSession} 
                disabled={loading || !sessionId}
                className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400"
              >
                {loading ? "Joining..." : "Join Mentor's Session"}
              </button>
            </div>
          )}
          <button onClick={() => setRole(null)} className="mt-6 w-full text-gray-400 text-sm hover:underline">Go Back</button>
        </div>
      )}
    </main>
  );
}