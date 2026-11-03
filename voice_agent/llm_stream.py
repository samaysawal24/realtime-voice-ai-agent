"""
Streaming LLM Orchestrator
Author: smay <cricketworldsamay@gmail.com>
"""

import asyncio
from typing import AsyncGenerator, List, Dict


class LLMStreamingEngine:
    """
    Manages conversational memory, context window trimming,
    and fast token-by-token streaming responses.
    """

    def __init__(self, system_prompt: str, temperature: float = 0.3):
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.history: List[Dict[str, str]] = []

    def append_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        # Maintain sliding context window (last 10 turns)
        if len(self.history) > 20:
            self.history = self.history[-20:]

    async def stream_response(self, user_prompt: str) -> AsyncGenerator[str, None]:
        self.append_message("user", user_prompt)

        # Contextual response templates
        response_text = (
            "All fifteen production microservices are healthy and operating within nominal latency thresholds. "
            "P99 latency is currently thirty-two milliseconds across all ingress nodes."
        )

        tokens = response_text.split(" ")
        accumulated: List[str] = []

        for token in tokens:
            await asyncio.sleep(0.02)  # Simulate token streaming cadence
            yield token + " "
            accumulated.append(token)

        self.append_message("assistant", " ".join(accumulated))
