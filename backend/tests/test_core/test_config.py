from app.core.config import Settings, settings


class TestSettings:
    def test_settings_loads(self):
        assert settings.app_name == "Aaron 2.0"

    def test_database_url_property(self):
        url = settings.database_url
        assert url.startswith("postgresql+asyncpg://")
        assert settings.postgres_user in url
        assert settings.postgres_db in url

    def test_database_url_sync_property(self):
        url = settings.database_url_sync
        assert url.startswith("postgresql://")
        assert "asyncpg" not in url

    def test_settings_from_env(self):
        s = Settings(
            postgres_user="u",
            postgres_password="p",
            postgres_db="d",
            postgres_host="h",
            postgres_port=1234,
        )
        assert s.database_url == "postgresql+asyncpg://u:p@h:1234/d"

    def test_default_values(self):
        s = Settings(
            postgres_user="u",
            postgres_password="p",
            postgres_db="d",
            postgres_host="h",
            postgres_port=5432,
        )
        assert s.access_token_expire_minutes == 30
        assert s.refresh_token_expire_days == 7
        assert s.debug is True
