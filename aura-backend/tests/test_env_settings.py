"""Tests for the EnvSettings unified config loader."""


def test_env_settings_reads_from_env_vars(monkeypatch):
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "9999")
    monkeypatch.setenv("DB_USER", "tester")
    monkeypatch.setenv("DB_PASSWORD", "hunter2")
    monkeypatch.setenv("DB_HOST", "db.example")
    monkeypatch.setenv("DB_PORT", "3307")
    monkeypatch.setenv("DB_NAME", "aura_test")
    monkeypatch.setenv("FRONTEND_URL", "https://aura.example")

    from app.core.config import EnvSettings
    s = EnvSettings()
    assert s.host == "0.0.0.0"
    assert s.port == 9999
    assert s.db_user == "tester"
    assert s.db_password == "hunter2"
    assert s.db_host == "db.example"
    assert s.db_port == 3307
    assert s.db_name == "aura_test"
    assert s.frontend_url == "https://aura.example"


def test_env_settings_mysql_url_property():
    from app.core.config import EnvSettings
    s = EnvSettings(
        db_user="u",
        db_password="p",
        db_host="h",
        db_port=3306,
        db_name="n",
    )
    assert s.mysql_url == "mysql+pymysql://u:p@h:3306/n"


def test_env_settings_database_url_overrides():
    from app.core.config import EnvSettings
    s = EnvSettings(
        db_user="u",
        db_password="p",
        db_host="h",
        db_name="n",
        database_url="postgresql://override",
    )
    assert s.mysql_url == "postgresql://override"
