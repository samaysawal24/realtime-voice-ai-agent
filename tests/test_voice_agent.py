"""
Unit tests for Realtime Voice AI Agent
Author: smay <cricketworldsamay@gmail.com>
"""

import struct
import pytest
from voice_agent import (
    VoiceActivityDetector,
    AudioFrame,
    VoiceSession,
    VoiceSessionConfig,
    AgentState
)


def test_vad_silence_vs_speech():
    vad = VoiceActivityDetector(energy_threshold=0.01)

    # 1. Generate 20ms of silence (zeros)
    silence_pcm = bytes(640)  # 320 samples of 16-bit zero
    frame_silence = AudioFrame(pcm_bytes=silence_pcm)
    res_silence = vad.process_frame(frame_silence)
    assert not res_silence.is_speech

    # 2. Generate 20ms of loud signal
    loud_pcm = bytearray()
    for _ in range(320):
        loud_pcm.extend(struct.pack("<h", 16000))
    frame_loud = AudioFrame(pcm_bytes=bytes(loud_pcm))
    res_loud = vad.process_frame(frame_loud)
    assert res_loud.is_speech
    assert res_loud.energy > 0.1


@pytest.mark.asyncio
async def test_session_state_transition_and_interruption():
    cfg = VoiceSessionConfig(session_id="test_sess_01")
    session = VoiceSession(config=cfg)

    assert session.state == AgentState.IDLE

    # Simulate speaking state
    session.state = AgentState.SPEAKING
    await session.interrupt()
    assert session.state == AgentState.INTERRUPTED
