from pydantic import SecretStr

from cinewatch_api.settings import Settings


def test_provider_settings_are_secret_values() -> None:
    settings = Settings(
        tmdb_api_key="tmdb-local-secret",
        omdb_api_key="omdb-local-secret",
        _env_file=None,
    )

    assert isinstance(settings.tmdb_api_key, SecretStr)
    assert isinstance(settings.omdb_api_key, SecretStr)
    assert settings.tmdb_api_key.get_secret_value() == "tmdb-local-secret"
    assert settings.omdb_api_key.get_secret_value() == "omdb-local-secret"
    assert "tmdb-local-secret" not in repr(settings.tmdb_api_key)
    assert "omdb-local-secret" not in repr(settings.omdb_api_key)
