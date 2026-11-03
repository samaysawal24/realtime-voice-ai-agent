"""
Voice Agent Session Coordinator with Barge-in Interruption
Author: Samay Sawal <cricketworldsamay@gmail.com>
"""

import asyncio
from typing import Callable, Optional
from .models import (
    VoiceSessionConfig,
    AgentState,
    AudioFrame,
    TranscriptSegment,
    SessionEvent
)
from .vad import VoiceActivityDetector
from .stt import SpeechToTextProvider
from .tts import TextToSpeechProvider
from .llm_stream import LLMStreamingEngine


class VoiceSession:
    """
    Coordinates real-time bi-directional voice loop:
    Audio In -> VAD -> STT -> Streaming LLM -> TTS -> Audio Out
    With instant cancellation on user interruption (Barge-in).
    """

    def __init__(self, config: VoiceSessionConfig, on_event: Optional[Callable[[SessionEvent], None]] = None):
        self.config = config
        self.on_event = on_event
        self.state = AgentState.IDLE
        self.vad = VoiceActivityDetector(
            energy_threshold=config.vad_energy_threshold,
            silence_duration_ms=config.vad_silence_duration_ms
        )
        self.stt = SpeechToTextProvider()
        self.tts = TextToSpeechProvider(voice_id=config.voice_id, sample_rate=config.sample_rate)
        self.llm = LLMStreamingEngine(system_prompt=config.system_prompt, temperature=config.llm_temperature)
        self._current_speaking_task: Optional[asyncio.Task] = None

    def _set_state(self, new_state: AgentState):
        self.state = new_state
        if self.on_event:
            self.on_event(
                SessionEvent(
                    event_type="agent_state",
                    payload={"state": self.state.value, "session_id": self.config.session_id}
                )
            )

    async def handle_audio_frame(self, frame: AudioFrame):
        vad_res = self.vad.process_frame(frame)

        # Barge-in interruption check
        if vad_res.is_speech and self.state == AgentState.SPEAKING and self.config.barge_in_enabled:
            await self.interrupt()

        if vad_res.is_speech:
            if self.state != AgentState.USER_SPEAKING:
                self._set_state(AgentState.USER_SPEAKING)
            self.stt.append_audio(frame)
        else:
            if self.state == AgentState.USER_SPEAKING:
                # User finished speaking -> trigger pipeline
                self._set_state(AgentState.THINKING)
                transcript = self.stt.transcribe_chunk(is_final=True)
                if transcript:
                    if self.on_event:
                        self.on_event(
                            SessionEvent(
                                event_type="transcript",
                                payload=transcript.model_dump()
                            )
                        )
                    # Trigger LLM and audio response
                    self._current_speaking_task = asyncio.create_task(self._generate_and_speak(transcript.text))
                else:
                    self._set_state(AgentState.LISTENING)

    async def _generate_and_speak(self, user_text: str):
        self._set_state(AgentState.SPEAKING)
        full_text = ""

        try:
            async for token in self.llm.stream_response(user_text):
                full_text += token

            if self.on_event:
                self.on_event(
                    SessionEvent(
                        event_type="transcript",
                        payload={"text": full_text, "speaker": "assistant", "is_final": True}
                    )
                )

            # Synthesize and stream audio frames
            async for out_frame in self.tts.stream_audio_from_text(full_text):
                if self.state != AgentState.SPEAKING:
                    break  # Abort on interruption
                if self.on_event:
                    self.on_event(
                        SessionEvent(
                            event_type="audio_chunk",
                            payload={"bytes_length": len(out_frame.pcm_bytes)}
                        )
                    )
                await asyncio.sleep(0.015)

        except asyncio.CancelledError:
            pass
        finally:
            if self.state == AgentState.SPEAKING:
                self._set_state(AgentState.LISTENING)

    async def interrupt(self):
        """Immediately halts agent speaking and flushes playback queue"""
        if self._current_speaking_task and not self._current_speaking_task.done():
            self._current_speaking_task.cancel()
        self._set_state(AgentState.INTERRUPTED)
        if self.on_event:
            self.on_event(
                SessionEvent(
                    event_type="barge_in",
                    payload={"message": "Agent interrupted by user speech", "session_id": self.config.session_id}
                )
            )
        self.vad.reset()

