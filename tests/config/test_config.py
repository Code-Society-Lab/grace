from config.config import Config


def test_set_environment():
    config = Config()
    config.set_environment("test")

    assert config.current_environment == "test"


def test_section_name():
    config = Config()
    config.set_environment("test")

    assert config.environment.name == "test"


def test_database():
    config = Config()
    config.set_environment("test")

    assert config.database["adapter"] == "sqlite"
    assert config.database["database"] == "grace_test.db"


def test_database_uri():
    from sqlalchemy.engine import URL

    config = Config()
    config.set_environment("test")

    assert config.database_uri == URL.create(drivername="sqlite", database="grace_test.db")


def test_get():
    config = Config()
    config.set_environment("test")

    assert config.get("test", "test") == "test"
    assert config.get("test", "test_int") == 42
    assert config.get("test", "test_float") == 42.5
    assert config.get("test", "test_bool") is True
    assert config.get("test", "test_fallback") is None


def test_client():
    config = Config()
    config.set_environment("test")

    assert config.client is not None

