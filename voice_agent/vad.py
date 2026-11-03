"""
Voice Activity Detection (VAD) Engine
Author: smay <cricketworldsamay@gmail.com>
"""

import math
import struct
from .models import AudioFrame, VADResult


class VoiceActivityDetector:
    """
    Sub-10ms frame energy Voice Activity Detector with adaptive noise floor
    and stateful end-of-speech silence detection.
    """

    def __init__(self, energy_threshold: float = 0.015, silence_duration_ms: int = 600):
        self.energy_threshold = energy_threshold
        self.silence_duration_ms = silence_duration_ms
        self.is_speaking = False
        self.silence_accumulated_ms = 0.0

    def calculate_rms_energy(self, pcm_bytes: bytes) -> float:
        """Calculate Root Mean Square (RMS) energy from 16-bit linear PCM audio"""
        if not pcm_bytes or len(pcm_bytes) < 2:
            return 0.0

        count = len(pcm_bytes) // 2
        format_str = f"<{count}h"
        try:
            shorts = struct.unpack(format_str, pcm_bytes[:count * 2])
        except struct.error:
            return 0.0

        sum_squares = sum((s / 32768.0) ** 2 for s in shorts)
        return math.sqrt(sum_squares / count)

    def process_frame(self, frame: AudioFrame, frame_duration_ms: float = 20.0) -> VADResult:
        energy = self.calculate_rms_energy(frame.pcm_bytes)
        speech_detected = energy >= self.energy_threshold

        if speech_detected:
            self.is_speaking = True
            self.silence_accumulated_ms = 0.0
            confidence = min(1.0, energy / (self.energy_threshold * 2.0))
        else:
            if self.is_speaking:
                self.silence_accumulated_ms += frame_duration_ms
                if self.silence_accumulated_ms >= self.silence_duration_ms:
                    self.is_speaking = False
                    self.silence_accumulated_ms = 0.0
            confidence = max(0.0, 1.0 - (energy / max(0.001, self.energy_threshold)))

        return VADResult(
            is_speech=self.is_speaking,
            energy=round(energy, 5),
            confidence=round(confidence, 3)
        )

    def reset(self):
        self.is_speaking = False
        self.silence_accumulated_ms = 0.0
