import pytest
from pathlib import Path
from ai_decision_engine.stt import MockSTTProvider, STTProvider


def test_mock_stt_returns_fixed_transcript():
    stt = MockSTTProvider("find me sushi restaurants")
    result = stt.transcribe("/fake/path.wav")
    assert result == "find me sushi restaurants"


def test_mock_stt_default_transcript():
    stt = MockSTTProvider()
    result = stt.transcribe("/fake/audio.mp3")
    assert isinstance(result, str)
    assert len(result) > 0


def test_stt_provider_is_abstract():
    with pytest.raises(TypeError):
        STTProvider()


def test_whisper_provider_import_error_without_openai():
    import sys
    openai_backup = sys.modules.get("openai")
    sys.modules["openai"] = None  # type: ignore[assignment]
    try:
        from importlib import reload
        import ai_decision_engine.stt.providers as mod
        reload(mod)
        with pytest.raises(ImportError, match="openai package required"):
            mod.WhisperSTTProvider()
    finally:
        if openai_backup is not None:
            sys.modules["openai"] = openai_backup
        elif "openai" in sys.modules:
            del sys.modules["openai"]
