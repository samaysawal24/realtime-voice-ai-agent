# Realtime Conversational Voice AI Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![WebSockets](https://img.shields.io/badge/WebSockets-Realtime-4F46E5.svg)](https://websockets.readthedocs.io)
[![Author](https://img.shields.io/badge/Author-Samay_Sawal-orange.svg)](https://github.com/samaysawal24)

An ultra-low latency, bidirectional conversational voice agent built with WebSockets/WebRTC streaming, sub-frame Voice Activity Detection (VAD), streaming Speech-to-Text (STT), low-latency LLM generation, and immediate user interruption (barge-in) support.

---

## 🏛️ System Architecture

```mermaid
sequenceDiagram
    autonumber
    actor User as User (Mic Stream)
    participant WS as WebSocket Ingress
    participant VAD as Sub-Frame VAD
    participant STT as Streaming STT
    participant LLM as Streaming LLM Engine
    participant TTS as Streaming TTS Synthesizer
    actor Speaker as User (Speaker)

    User->>WS: Stream 20ms Audio Frames (16kHz PCM)
    WS->>VAD: Analyze Energy & Zero-Crossing Rate
    alt Voice Detected
        VAD->>STT: Accumulate Audio Buffer
    else Silence Detected (>= 600ms)
        VAD->>STT: Trigger Final Transcription
        STT->>LLM: Transcribed User Utterance
        loop Streaming Response
            LLM->>TTS: Stream Token Chunks
            TTS->>WS: Synthesize 20ms Audio Chunks
            WS->>Speaker: Low Latency Audio Playback
        end
    end

    Note over User,Speaker: User Interrupts During Playback (Barge-in)
    User->>VAD: Loud Ingress Frame
    VAD->>LLM: Cancel Execution Task
    VAD->>TTS: Flush Audio Output Buffer
    VAD->>WS: Broadcast Interrupt Event
```

---

## 🚀 Key Features

- **Sub-300ms Glass-to-Glass Latency:** Designed for high-speed fluid conversations without awkward pauses.
- **Immediate Barge-in Interruption:** Cancels active speech generation and flushes output queues the instant the user begins talking.
- **Low-Overhead VAD:** RMS energy thresholding combined with configurable silence windowing.
- **Bi-directional WebSocket Protocol:** Streams binary audio frames and JSON state telemetry over a single persistent socket.
- **Modular Adapter Architecture:** Plug-and-play compatibility with Whisper, Deepgram, Cartesia, ElevenLabs, and OpenAI Realtime API.

---

## 📦 Project Structure

```
realtime-voice-ai-agent/
├── voice_agent/
│   ├── __init__.py           # Package exports
│   ├── llm_stream.py         # Streaming LLM token generator & history
│   ├── models.py             # Pydantic v2 schemas and state enums
│   ├── session.py            # VoiceSession lifecycle & interruption logic
│   ├── stt.py                # Speech-to-Text streaming adapter
│   ├── tts.py                # Text-to-Speech audio synthesizer
│   └── vad.py                # Sub-frame Voice Activity Detection engine
├── api/
│   └── server.py             # FastAPI WebSocket and REST server
├── tests/
│   └── test_voice_agent.py   # Pytest unit tests
├── Dockerfile                # Production container spec
├── docker-compose.yml        # Orchestration spec
├── pyproject.toml            # Python package metadata
├── requirements.txt          # Frozen dependencies
├── LICENSE                   # MIT License (smay)
└── README.md
```

---

## ⚡ Quickstart

### 1. Local Setup

```bash
git clone https://github.com/samaysawal24/realtime-voice-ai-agent.git
cd realtime-voice-ai-agent

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Start WebSocket Server

```bash
uvicorn api.server:app --reload --port 8000
```

### 3. Connect via WebSocket

Connect your client (browser audio context or Python client) to:
```
ws://localhost:8000/ws/voice-agent/{session_id}
```
Stream raw `16000Hz 16-bit Mono PCM` binary frames directly to the socket.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📜 License & Author

- **Author:** smay ([@samaysawal24](https://github.com/samaysawal24))
- **Email:** cricketworldsamay@gmail.com
- **License:** Released under the [MIT License](LICENSE).

