"""
FastAPI WebSocket Voice Streaming Server
Author: Samay Sawal <cricketworldsamay@gmail.com>
"""

import json
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from voice_agent import VoiceSession, VoiceSessionConfig, AudioFrame, SessionEvent

app = FastAPI(
    title="Realtime Voice AI Agent API",
    version="1.0.0",
    description="Ultra-Low Latency Conversational Voice WebSocket Server authored by Samay Sawal"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "realtime-voice-ai-agent",
        "author": "Samay Sawal",
        "engine": "WebRTC-WebSocket-VoiceLoop"
    }


@app.post("/api/v1/session/create")
async def create_session(config: VoiceSessionConfig):
    return {
        "status": "created",
        "session_id": config.session_id,
        "websocket_url": f"/ws/voice-agent/{config.session_id}"
    }


@app.websocket("/ws/voice-agent/{session_id}")
async def websocket_voice_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    def handle_event(event: SessionEvent):
        # Dispatch event asynchronously over WebSocket
        import asyncio
        data = json.dumps({
            "event": event.event_type,
            "payload": event.payload,
            "timestamp": event.timestamp.isoformat()
        })
        asyncio.create_task(websocket.send_text(data))

    cfg = VoiceSessionConfig(session_id=session_id)
    session = VoiceSession(config=cfg, on_event=handle_event)

    try:
        while True:
            # Receive incoming PCM audio frame bytes from client
            message = await websocket.receive()
            if "bytes" in message and message["bytes"]:
                frame = AudioFrame(pcm_bytes=message["bytes"])
                await session.handle_audio_frame(frame)
            elif "text" in message and message["text"]:
                data = json.loads(message["text"])
                if data.get("action") == "interrupt":
                    await session.interrupt()
    except WebSocketDisconnect:
        pass

