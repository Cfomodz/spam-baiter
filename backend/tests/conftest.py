"""Test configuration.

Environment variables must be set before ``app.config`` is imported,
because Settings is instantiated at import time. Everything points at a
temp directory so tests never touch the real DB, audio files, or
soundboard.
"""

import os
import tempfile
from pathlib import Path

import pytest

_tmp = Path(tempfile.mkdtemp(prefix="spam_baiter_tests_"))

_persona = _tmp / "soundboard" / "Test Persona"
_persona.mkdir(parents=True)
(_persona / "Hello there.wav").write_bytes(b"RIFF")
_tier = _persona / "early_question_responses" / "tier_1"
_tier.mkdir(parents=True)
(_tier / "Yes.wav").write_bytes(b"RIFF")

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_tmp / 'test.db'}"
os.environ["AUDIO_FILES_DIR"] = str(_tmp / "audio_files")
os.environ["SOUNDBOARD_DIR"] = str(_tmp / "soundboard")
os.environ["ELEVENLABS_API_KEY"] = ""
os.environ["PHONE_BRIDGE"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
