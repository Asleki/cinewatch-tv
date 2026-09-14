"""Private local staging for explicitly accepted NexVox WAV training samples."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
from pathlib import Path

from cinewatch_api.contracts.voice import VoiceSampleStageRequest, VoiceSampleStageResponse


class VoiceStagingDisabledError(RuntimeError):
    """Raised when private staging has not been configured."""


class InvalidVoiceSampleError(ValueError):
    """Raised when a submitted sample is not a bounded RIFF/WAVE payload."""


class VoiceStagingService:
    """Persist accepted WAV + metadata with private filesystem permissions and no read API."""

    MAX_WAV_BYTES = 12 * 1024 * 1024

    def __init__(self, staging_dir: str | None) -> None:
        self._staging_dir = Path(staging_dir).expanduser() if staging_dir else None

    def stage(self, payload: VoiceSampleStageRequest) -> VoiceSampleStageResponse:
        if self._staging_dir is None:
            raise VoiceStagingDisabledError("NexVox private staging is not configured.")
        try:
            wav = base64.b64decode(payload.wav_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise InvalidVoiceSampleError("Voice sample is not valid base64.") from exc
        if not wav or len(wav) > self.MAX_WAV_BYTES:
            raise InvalidVoiceSampleError("Voice sample exceeds the governed size boundary.")
        if len(wav) < 44 or wav[:4] != b"RIFF" or wav[8:12] != b"WAVE":
            raise InvalidVoiceSampleError("Voice sample must be a RIFF/WAVE file.")

        digest = hashlib.sha256(wav).hexdigest()
        sample_id = f"nexvox-{payload.metadata.tester_id}-{digest[:20]}"
        tester_dir = self._staging_dir / payload.metadata.tester_id
        tester_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            os.chmod(self._staging_dir, 0o700)
            os.chmod(tester_dir, 0o700)
        except OSError:
            pass

        wav_path = tester_dir / f"{sample_id}.wav"
        metadata_path = tester_dir / f"{sample_id}.json"
        metadata = payload.metadata.model_dump(mode="json") | {
            "sample_id": sample_id,
            "sha256": digest,
            "size_bytes": len(wav),
            "retention_status": "LOCAL_PRIVATE_STAGING",
        }

        self._write_private(wav_path, wav)
        self._write_private(
            metadata_path,
            (json.dumps(metadata, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"),
        )
        return VoiceSampleStageResponse(sample_id=sample_id, stored=True)

    @staticmethod
    def _write_private(path: Path, data: bytes) -> None:
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        fd = os.open(path, flags, 0o600)
        try:
            with os.fdopen(fd, "wb", closefd=False) as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            os.close(fd)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
