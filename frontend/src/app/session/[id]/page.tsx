"use client";

import React, { useEffect, useState, useRef } from "react"; 
import { useParams } from "next/navigation"; 

export default function SessionRoom() {
  const params = useParams();
  const id = params?.id as string;

  const [code, setCode] = useState("");
  const [chatMessages, setChatMessages] = useState<{ sender_id: string; message: string }[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isConnected, setIsConnected] = useState(false);

  const ws = useRef<WebSocket | null>(null);
  const peerConnection = useRef<RTCPeerConnection | null>(null);
  
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);

  const connectWebSocket = () => {
    if (!id) return; 

    const userId = Math.random().toString(36).substring(7); 
    const token = "dummy-token";
    
    ws.current = new WebSocket(`ws://localhost:8000/ws/session/${id}?user_id=${userId}&token=${token}`);

    ws.current.onopen = () => setIsConnected(true);

    ws.current.onmessage = async (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "code") setCode(data.content);
      else if (data.type === "chat") setChatMessages((prev) => [...prev, data]);
      else if (data.type === "offer") handleReceiveOffer(data);
      else if (data.type === "answer") handleReceiveAnswer(data);
      else if (data.type === "ice-candidate") handleNewICECandidateMsg(data);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      setTimeout(() => {
        connectWebSocket();
      }, 3000);
    };
  };

  useEffect(() => {
    if (id) {
      connectWebSocket();
      startLocalVideo();
    }

    return () => {
      ws.current?.close();
      peerConnection.current?.close();
    };
  }, [id]); 

  const startLocalVideo = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }
      initializePeerConnection(stream);
    } catch (error) {
      console.error("Camera access denied or unavailable", error);
    }
  };

  const initializePeerConnection = (stream: MediaStream) => {
    const pc = new RTCPeerConnection({
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    });

    stream.getTracks().forEach((track) => pc.addTrack(track, stream));

    pc.ontrack = (event) => {
      if (remoteVideoRef.current) {
        remoteVideoRef.current.srcObject = event.streams[0];
      }
    };

    pc.onicecandidate = (event) => {
      if (event.candidate && ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({
          type: "ice-candidate",
          candidate: event.candidate
        }));
      }
    };

    peerConnection.current = pc;
  };

  const startCall = async () => {
    if (!peerConnection.current) return;
    const offer = await peerConnection.current.createOffer();
    await peerConnection.current.setLocalDescription(offer);
    ws.current?.send(JSON.stringify({ type: "offer", offer }));
  };

  const handleReceiveOffer = async (data: any) => {
    if (!peerConnection.current) return;
    await peerConnection.current.setRemoteDescription(new RTCSessionDescription(data.offer));
    const answer = await peerConnection.current.createAnswer();
    await peerConnection.current.setLocalDescription(answer);
    ws.current?.send(JSON.stringify({ type: "answer", answer }));
  };

  const handleReceiveAnswer = async (data: any) => {
    await peerConnection.current?.setRemoteDescription(new RTCSessionDescription(data.answer));
  };

  const handleNewICECandidateMsg = async (data: any) => {
    await peerConnection.current?.addIceCandidate(new RTCIceCandidate(data.candidate));
  };

  const handleEditorChange = (newCode: string) => {
    setCode(newCode); 
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: "code", content: newCode }));
    }
  };

  const handleSendChat = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: "chat", message: chatInput }));
    }
    setChatInput(""); 
  };

  return (
    <div className="flex h-screen w-full bg-gray-900 text-white">
      <div className="w-2/3 p-4 border-r border-gray-700 flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Code Workspace</h2>
          <span className={`px-3 py-1 rounded text-sm font-bold ${isConnected ? "bg-green-600" : "bg-red-600 animate-pulse"}`}>
            {isConnected ? "Connected" : "Reconnecting..."}
          </span>
        </div>
        <textarea 
          className="flex-1 bg-gray-800 p-4 font-mono outline-none rounded resize-none"
          value={code}
          onChange={(e) => handleEditorChange(e.target.value)}
          placeholder="Start typing Python code here..."
        />
      </div>

      <div className="w-1/3 p-4 flex flex-col gap-4">
        <div className="flex flex-col gap-2 h-1/2">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold">Video</h2>
            <button onClick={startCall} className="bg-green-600 hover:bg-green-500 px-3 py-1 rounded text-sm font-bold transition">
              Connect Call
            </button>
          </div>
          
          <div className="relative flex-1 bg-black rounded overflow-hidden border border-gray-700">
            <video ref={remoteVideoRef} autoPlay playsInline className="w-full h-full object-cover" />
            <div className="absolute bottom-4 right-4 w-1/3 aspect-video bg-gray-800 rounded border-2 border-gray-500 overflow-hidden shadow-lg">
              <video ref={localVideoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
            </div>
          </div>
        </div>

        <div className="flex flex-col h-1/2 border-t border-gray-700 pt-4">
          <h2 className="text-xl font-bold mb-2">Chat</h2>
          <div className="flex-1 overflow-y-auto bg-gray-800 p-4 mb-2 rounded border border-gray-700">
            {chatMessages.map((msg, index) => (
              <div key={index} className="mb-2 text-sm">
                <span className="font-bold text-blue-400">{msg.sender_id.substring(0, 5)}: </span>
                <span className="text-gray-200">{msg.message}</span>
              </div>
            ))}
          </div>
          <form onSubmit={handleSendChat} className="flex gap-2">
            <input
              type="text"
              className="flex-1 bg-gray-700 p-2 text-sm rounded outline-none border border-gray-600 focus:border-blue-500"
              placeholder="Type a message..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
            />
            <button type="submit" className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded text-sm font-bold transition">
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}