from __future__ import annotations

import base64
import json
import os
import wave
from io import BytesIO

import pytest

from cinewatch_api.contracts.voice import VoiceSampleMetadata, VoiceSampleStageRequest
from cinewatch_api.voice.service import InvalidVoiceSampleError, VoiceStagingService


def _wav() -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(16000)
        handle.writeframes(b"\x00\x00" * 1600)
    return buffer.getvalue()


def _payload(raw: bytes | None = None) -> VoiceSampleStageRequest:
    return VoiceSampleStageRequest(
        metadata=VoiceSampleMetadata(
            tester_id="tester-01",
            session_id="session-12345678",
            recorded_at="2026-09-12T17:00:00Z",
            language="English",
            prompt="CineWatch Voice Lab qualification prompt.",
            sample_rate=16000,
            duration_seconds=0.1,
            consent_version="CWTV-NEXVOX-CONSENT-R3-001",
        ),
        wav_base64=base64.b64encode(raw or _wav()).decode("ascii"),
    )


def test_staging_writes_private_wav_and_metadata(tmp_path) -> None:
    result = VoiceStagingService(str(tmp_path)).stage(_payload())
    assert result.stored is True
    wav_path = tmp_path / "tester-01" / f"{result.sample_id}.wav"
    metadata_path = tmp_path / "tester-01" / f"{result.sample_id}.json"
    assert wav_path.read_bytes().startswith(b"RIFF")
    metadata = json.loads(metadata_path.read_text())
    assert metadata["tester_id"] == "tester-01"
    assert metadata["consent_version"] == "CWTV-NEXVOX-CONSENT-R3-001"
    if os.name == "posix":
        assert oct(wav_path.stat().st_mode & 0o777) == "0o600"
        assert oct(metadata_path.stat().st_mode & 0o777) == "0o600"


def test_staging_rejects_non_wav(tmp_path) -> None:
    with pytest.raises(InvalidVoiceSampleError):
        VoiceStagingService(str(tmp_path)).stage(_payload(b"not-a-wave-file" * 10))
