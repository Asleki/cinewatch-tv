from cinewatch_api.settings import Settings


def test_settings_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.environment == "local"
    assert settings.app_name == "CineWatch TV"
    assert settings.service_name == "cinewatch-api"
    assert settings.log_level == "INFO"


def test_settings_accept_field_names() -> None:
    settings = Settings(environment="development", log_level="WARNING", _env_file=None)

    assert settings.environment == "development"
    assert settings.log_level == "WARNING"
