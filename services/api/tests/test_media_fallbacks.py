from cinewatch_api.media.fallbacks import MediaGap, remediation_for, slugify


def test_person_profile_requires_human_research() -> None:
    gap = MediaGap(
        provider="tmdb",
        entity_type="person",
        provider_id=42,
        entity_name="Example Person",
        asset_kind="profile",
    )

    assert gap.remediation == "AWAITING_HUMAN_RESEARCH"
    assert gap.suggested_filename == "tmdb-person-42-example-person.webp"
    assert gap.public_path == "/provider-fallbacks/people/tmdb-person-42-example-person.webp"


def test_logos_and_backdrops_allow_generation() -> None:
    assert remediation_for("logo") == "GENERATION_ALLOWED"
    assert remediation_for("backdrop") == "GENERATION_ALLOWED"
    assert remediation_for("poster") == "AWAITING_HUMAN_RESEARCH"


def test_fallback_slug_is_deterministic() -> None:
    assert slugify("Amélie & Friends") == "amelie-friends"
