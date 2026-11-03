"""
Data models and state definitions for Realtime Voice AI Agent
Author: Samay Sawal <cricketworldsamay@gmail.com>
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AgentState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    USER_SPEAKING = "user_speaking"
    THINKING = "thinking"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"


class AudioFrame(BaseModel):
    pcm_bytes: bytes
    sample_rate: int = 16000
    channels: int = 1
    timestamp_ms: float = Field(default_factory=lambda: datetime.utcnow().timestamp() * 1000)


class VADResult(BaseModel):
    is_speech: bool
    energy: float
    confidence: float


class TranscriptSegment(BaseModel):
    text: str
    is_final: bool = False
    confidence: float = 1.0
    speaker: str = "user"  # "user" or "assistant"
    duration_ms: float = 0.0


class VoiceSessionConfig(BaseModel):
    session_id: str
    sample_rate: int = 16000
    vad_energy_threshold: float = 0.015
    vad_silence_duration_ms: int = 600
    barge_in_enabled: bool = True
    system_prompt: str = (
        "You are an ultra-fast, professional, and concise voice AI assistant. "
        "Keep responses direct and conversational, typically within 1 to 2 sentences."
    )
    llm_temperature: float = 0.3
    voice_id: str = "en-US-neural-clarity"


class SessionEvent(BaseModel):
    event_type: str  # "transcript", "audio_chunk", "agent_state", "barge_in", "error"
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

