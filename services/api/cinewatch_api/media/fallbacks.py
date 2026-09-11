"""Deterministic provider-media gap and fallback naming authority."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Literal

EntityType = Literal["person", "network", "movie", "tv"]
AssetKind = Literal["profile", "logo", "poster", "backdrop"]
Remediation = Literal["AWAITING_HUMAN_RESEARCH", "GENERATION_ALLOWED"]

_DIRECTORY_BY_ASSET: dict[AssetKind, str] = {
    "profile": "people",
    "logo": "networks",
    "poster": "posters",
    "backdrop": "backdrops",
}

_ALLOWED: set[tuple[EntityType, AssetKind]] = {
    ("person", "profile"),
    ("network", "logo"),
    ("movie", "poster"),
    ("movie", "backdrop"),
    ("tv", "poster"),
    ("tv", "backdrop"),
}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return slug or "entity"


def remediation_for(asset_kind: AssetKind) -> Remediation:
    if asset_kind in {"logo", "backdrop"}:
        return "GENERATION_ALLOWED"
    return "AWAITING_HUMAN_RESEARCH"


@dataclass(frozen=True, slots=True)
class MediaGap:
    provider: str
    entity_type: EntityType
    provider_id: int
    entity_name: str
    asset_kind: AssetKind

    def __post_init__(self) -> None:
        if self.provider_id <= 0:
            raise ValueError("provider_id must be positive.")
        if (self.entity_type, self.asset_kind) not in _ALLOWED:
            raise ValueError(
                f"unsupported media gap combination: {self.entity_type}/{self.asset_kind}"
            )
        if not re.fullmatch(r"[a-z0-9]+", self.provider):
            raise ValueError("provider must be a lowercase alphanumeric code.")

    @property
    def remediation(self) -> Remediation:
        return remediation_for(self.asset_kind)

    @property
    def directory(self) -> str:
        return _DIRECTORY_BY_ASSET[self.asset_kind]

    @property
    def suggested_filename(self) -> str:
        return (
            f"{self.provider}-{self.entity_type}-{self.provider_id}-"
            f"{slugify(self.entity_name)}.webp"
        )

    @property
    def public_path(self) -> str:
        return f"/provider-fallbacks/{self.directory}/{self.suggested_filename}"

    def as_record(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "entity_type": self.entity_type,
            "provider_id": self.provider_id,
            "entity_name": self.entity_name,
            "asset_kind": self.asset_kind,
            "remediation": self.remediation,
            "suggested_filename": self.suggested_filename,
            "public_path": self.public_path,
        }
