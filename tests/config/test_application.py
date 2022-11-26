from config.application import Application


def test_application_environment():
    app = Application()
    app.load(environment="test")

    assert app.config.current_environment == "test"