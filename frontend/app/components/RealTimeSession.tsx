"use client";
import React from 'react';

export default function RealTimeSession({ sessionId, role }: { sessionId: string, role: string | null }) {
  return (
    <div className="p-10 bg-gray-900 text-white min-h-screen">
      <h2 className="text-xl">Connected to Session: {sessionId}</h2>
      <p>Role: {role}</p>
      {/* We will add the Monaco Editor and WebSockets here next */}
    </div>
  );
}