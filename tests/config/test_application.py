from config.application import Application


def test_environment():
    app = Application()
    app.load(environment="test")

    assert app.config.current_environment == "test"


def test_bot():
    app = Application()
    app.load(environment="test")

    assert app.bot is not None
    assert app.bot.name == "client"


def test_that_fails():
    assert 1 == 2