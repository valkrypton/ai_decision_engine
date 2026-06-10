"""STT provider interface and implementations.

Install extras for real transcription:
    pip install "ai-decision-engine[stt]"   # adds openai package for Whisper API
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path


class STTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str | Path) -> str:
        """Transcribe audio file to text. Returns transcript string."""


class WhisperSTTProvider(STTProvider):
    """Transcribe via OpenAI Whisper API. Requires OPENAI_API_KEY env var."""

    def __init__(self, model: str = "whisper-1", language: str | None = None):
        try:
            import openai  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "openai package required for WhisperSTTProvider. "
                'Install with: pip install "ai-decision-engine[stt]"'
            ) from exc
        self._openai = openai
        self.model = model
        self.language = language
        self._client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def transcribe(self, audio_path: str | Path) -> str:
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        with audio_path.open("rb") as f:
            kwargs = {"model": self.model, "file": f}
            if self.language:
                kwargs["language"] = self.language
            resp = self._client.audio.transcriptions.create(**kwargs)
        return resp.text.strip()


class MockSTTProvider(STTProvider):
    """Returns a fixed transcript — for testing without audio hardware or API keys."""

    def __init__(self, fixed_transcript: str = "test query"):
        self._transcript = fixed_transcript

    def transcribe(self, audio_path: str | Path) -> str:
        return self._transcript
